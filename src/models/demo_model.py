from sqlalchemy import BIGINT, Boolean, Column, DateTime, Integer, String, Text, func

from src.database.database import Base as BaseModel


class DemoUserModel(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(BIGINT, primary_key=True)
    name = Column(Text(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    contact_number = Column(String(20))
    age = Column(Integer, nullable=False)
