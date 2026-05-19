from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepo:
    def __init__(self, db: AsyncSession):
        self.db = db