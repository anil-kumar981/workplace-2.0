from datetime import datetime, timedelta
from sqlalchemy import select, and_, delete
from app.models.otp_verification import OtpVerification
from .base_repo import BaseRepo

class OtpRepo(BaseRepo):
    async def create_otp(self, email: str, code: str, otp_type: str, expires_at: datetime) -> OtpVerification:
        """
        Creates a new OTP verification record in the database.
        Also invalidates any previous unverified OTP records for the same email and type.
        """
        # Invalidate previous unverified OTPs to keep the DB clean
        stmt = select(OtpVerification).where(
            and_(
                OtpVerification.email == email,
                OtpVerification.otp_type == otp_type,
                OtpVerification.is_verified == False
            )
        )
        result = await self.db.execute(stmt)
        for old_otp in result.scalars().all():
            # Set their expiration to now, effectively invalidating them
            old_otp.expires_at = datetime.utcnow()
            self.db.add(old_otp)

        # Create new OTP
        new_otp = OtpVerification(
            email=email,
            otp_code=code,
            otp_type=otp_type,
            is_verified=False,
            expires_at=expires_at
        )
        self.db.add(new_otp)
        return new_otp

    async def get_active_otp(self, email: str, otp_type: str) -> OtpVerification | None:
        """
        Gets the latest active (unexpired, unverified) OTP record for a given email and type.
        """
        stmt = select(OtpVerification).where(
            and_(
                OtpVerification.email == email,
                OtpVerification.otp_type == otp_type,
                OtpVerification.is_verified == False,
                OtpVerification.expires_at > datetime.utcnow()
            )
        ).order_index = OtpVerification.created_at.desc() # We will order by created_at desc to be safe
        
        # Wait, SQLAlchemy order_by is .order_by(), let's write it cleanly
        stmt = select(OtpVerification).where(
            and_(
                OtpVerification.email == email,
                OtpVerification.otp_type == otp_type,
                OtpVerification.is_verified == False,
                OtpVerification.expires_at > datetime.utcnow()
            )
        ).order_by(OtpVerification.created_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_verified_otp(self, email: str, otp_type: str, window_minutes: int = 10) -> OtpVerification | None:
        """
        Checks if there is a verified OTP status in the database for the given email and type
        within the short consumption window.
        """
        time_limit = datetime.utcnow() - timedelta(minutes=window_minutes)
        stmt = select(OtpVerification).where(
            and_(
                OtpVerification.email == email,
                OtpVerification.otp_type == otp_type,
                OtpVerification.is_verified == True,
                OtpVerification.updated_at >= time_limit
            )
        ).order_by(OtpVerification.updated_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def consume_verified_otp(self, email: str, otp_type: str) -> None:
        """
        Deletes or consumes all verified OTP records for this email and type to prevent replay attacks.
        """
        stmt = delete(OtpVerification).where(
            and_(
                OtpVerification.email == email,
                OtpVerification.otp_type == otp_type
            )
        )
        await self.db.execute(stmt)
