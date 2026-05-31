from sqlalchemy import Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(1), nullable=False)
    score = Column(Float, nullable=False)
    sins = Column(JSON, nullable=False)          # Liste der Sin-IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
