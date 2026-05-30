from app.shared.base_repo import BaseRepo
from sqlalchemy import select
from .interfaces.personal_details_repo_interface import IPersonalDetailsRepo
from app.schema import UserPersonalDetailCreate, UserPersonalDetailUpdate
from app.models import UserPersonalDetails, User

class PersonalDetailsRepo(BaseRepo, IPersonalDetailsRepo):
    async def create_personal_details(self, personal_details: UserPersonalDetailCreate, user_id: int) -> UserPersonalDetails:
        data = UserPersonalDetails(**personal_details.dict(), user_id=user_id)
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data

    async def get_personal_details(self, user_id: int) -> UserPersonalDetails | None:
        stmt = select(UserPersonalDetails).where(UserPersonalDetails.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_personal_details(self, personal_details: UserPersonalDetailUpdate, user_id: int) -> UserPersonalDetails:
        update_data = personal_details.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(personal_detail, key, value)
        self.db.add(personal_detail)
        await self.db.commit()
        await self.db.refresh(personal_detail)
        return personal_detail