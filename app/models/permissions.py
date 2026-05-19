from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)

    resource = Column(String, index=True, nullable=False)
    action = Column(String, index=True, nullable=False)
    scope = Column(String, index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("resource", "action", "scope", name="uq_permission"),
    )