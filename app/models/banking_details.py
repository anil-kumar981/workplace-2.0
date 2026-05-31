from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class BankingDetails(Base):
    __tablename__ = "banking_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    account_number = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    branch_name = Column(String, nullable=False)
    ifsc_code = Column(String, nullable=False)
    account_holder_name = Column(String, nullable=False)

    # Relation Mapping
    user = relationship("User", back_populates="banking_details")
