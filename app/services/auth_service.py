import secrets
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.schema import UserResponse, UserCreate
from app.schema.auth import OtpRequest, OtpVerify, LoginRequest, ForgotPasswordRequest
from app.repos.user_repo import UserRepo
from app.repos.otp_repo import OtpRepo
from app.shared.utils.security import hash_password, verify_password
from app.shared.utils.email_helper import send_otp_email
import logging
from app.core.config import config
from app.shared.exceptions import AppException

logger = logging.getLogger("app.auth_service")

class AuthService:
    """
    AuthService coordinates all transaction and business rules for the authentication
    and secure OTP validation workflows.
    """
    def __init__(self, user_repo: UserRepo, otp_repo: OtpRepo):
        self.user_repo = user_repo
        self.otp_repo = otp_repo

    async def _consume_otp_with_check(self, email: str, otp_type: str, window_minutes: int = 10) -> None:
        """
        Consumes the verified OTP. If the OTP is not found or is expired,
        raises an AppException that will trigger a transaction rollback.
        """
        verified_otp = await self.otp_repo.get_verified_otp(email, otp_type, window_minutes=window_minutes)
        if not verified_otp:
            raise AppException(
                "Your verification session has expired. Please verify your OTP again and retry.",
                400
            )
        await self.otp_repo.consume_verified_otp(email, otp_type)

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        """
        Registers a new user in the system. Requires an active, verified OTP for the email
        and the 'register' flow verified within the last 10 minutes.
        """
        # 1. Enforce verified OTP check (fast fail check before starting database modifications)
        verified_otp = await self.otp_repo.get_verified_otp(user_in.email, "register", window_minutes=10)
        if not verified_otp:
            raise AppException("OTP verification is required before registering. Please verify your OTP first.", 400)

        try:
            # 2. Perform the database modifications
            hashed_pw = hash_password(user_in.password)
            new_user = await self.user_repo.create_user(user_in, hashed_pw)

            # 3. Consume the OTP inside the transaction. If it's expired or not found, this raises an exception and rolls back!
            await self._consume_otp_with_check(user_in.email, "register", window_minutes=10)

            # 4. Commit all operations
            await self.user_repo.db.commit()
            await self.user_repo.db.refresh(new_user)
            return UserResponse.model_validate(new_user)
        except IntegrityError:
            await self.user_repo.db.rollback()
            raise AppException("An account with this email address already exists.", 400)
        except AppException as ae:
            await self.user_repo.db.rollback()
            raise ae
        except Exception as e:
            await self.user_repo.db.rollback()
            raise e

    async def request_otp(self, otp_in: OtpRequest) -> None:
        """
        Validates the user exists, generates a 6-digit numeric OTP,
        stores it in the DB, and dispatches the verification email.
        """
        # 1. Verify user exists in system
        user = await self.user_repo.get_user_by_email(otp_in.email)
        if not user:
            raise AppException("No account is registered with this email address.", 404)

        # 2. Generate a secure 6-digit OTP code
        # In development environment, we use a static OTP "123456" for ease of testing.
        # In production environment, we generate a secure random 6-digit OTP code.
        if config.ENV == 'production':
            otp_code = f"{secrets.randbelow(1000000):06d}"
        else:
            otp_code = "123456"
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        try:
            # 3. Create the record in DB
            await self.otp_repo.create_otp(otp_in.email, otp_code, otp_in.otp_type.value, expires_at)
            await self.otp_repo.db.commit()
        except Exception as e:
            await self.otp_repo.db.rollback()
            raise e

        # 4. Dispatch the email asynchronously in background thread
        # In production, dispatch email. In development, log the simulated OTP in console.
        if config.ENV == 'production':
            await send_otp_email(otp_in.email, otp_code, otp_in.otp_type.value)
        else:
            logger.info(
                f"[DEV MODE] Simulated OTP generation for {otp_in.email}: '{otp_code}' (type: {otp_in.otp_type.value})"
            )

    async def verify_otp(self, verify_in: OtpVerify) -> None:
        """
        Verifies the user's OTP code. If valid, marks the OTP as verified.
        """
        otp_rec = await self.otp_repo.get_active_otp(verify_in.email, verify_in.otp_type.value)
        if not otp_rec or otp_rec.otp_code != verify_in.otp_code:
            raise AppException("Invalid or expired OTP code. Please request a new one.", 400)

        try:
            otp_rec.is_verified = True
            self.otp_repo.db.add(otp_rec)
            await self.otp_repo.db.commit()
        except Exception as e:
            await self.otp_repo.db.rollback()
            raise e

    async def login_user(self, login_in: LoginRequest) -> UserResponse:
        """
        Validates login credentials. Requires an active, verified OTP for the email
        and the 'login' flow verified within the last 10 minutes.
        """
        # 1. Enforce verified OTP check (fast fail check before starting database modifications)
        verified_otp = await self.otp_repo.get_verified_otp(login_in.email, "login", window_minutes=10)
        if not verified_otp:
            raise AppException("OTP verification is required before logging in. Please verify your OTP first.", 400)

        # 2. Authenticate credentials
        user = await self.user_repo.get_user_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise AppException("Invalid email or password.", 400)

        if not user.is_active:
            raise AppException("This account has been deactivated.", 400)

        try:
            # 3. Auto-verify user status upon successful login if not already verified
            if not user.is_verified:
                user.is_verified = True
                self.user_repo.db.add(user)

            # 4. Consume the verified OTP inside the transaction. If it's expired or not found, this raises an exception and rolls back!
            await self._consume_otp_with_check(login_in.email, "login", window_minutes=10)

            await self.user_repo.db.commit()
            await self.user_repo.db.refresh(user)
            return UserResponse.model_validate(user)
        except AppException as ae:
            await self.user_repo.db.rollback()
            raise ae
        except Exception as e:
            await self.user_repo.db.rollback()
            raise e

    async def reset_password(self, reset_in: ForgotPasswordRequest) -> None:
        """
        Resets the user's password. Requires an active, verified OTP for the email
        and the 'forgot_password' flow verified within the last 10 minutes.
        Prevents reusing the current password.
        """
        # 1. Enforce verified OTP check (fast fail check before starting database modifications)
        verified_otp = await self.otp_repo.get_verified_otp(reset_in.email, "forgot_password", window_minutes=10)
        if not verified_otp:
            raise AppException("OTP verification is required before resetting password. Please verify your OTP first.", 400)

        # 2. Retrieve user
        user = await self.user_repo.get_user_by_email(reset_in.email)
        if not user:
            raise AppException("No account is registered with this email address.", 404)

        # 3. Prevent password similarity (reusing current password)
        if verify_password(reset_in.new_password, user.hashed_password):
            raise AppException("New password cannot be the same as your old password. Please choose a different password.", 400)

        try:
            # 4. Update password
            hashed_pw = hash_password(reset_in.new_password)
            await self.user_repo.update_user_password(user, hashed_pw)

            # 5. Consume OTP inside the transaction. If it's expired or not found, this raises an exception and rolls back!
            await self._consume_otp_with_check(reset_in.email, "forgot_password", window_minutes=10)

            await self.user_repo.db.commit()
        except AppException as ae:
            await self.user_repo.db.rollback()
            raise ae
        except Exception as e:
            await self.user_repo.db.rollback()
            raise e
