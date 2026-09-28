from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.base import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reactor_id = Column(Integer, ForeignKey("reactors.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    