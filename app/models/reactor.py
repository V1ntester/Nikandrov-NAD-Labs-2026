from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.base import Base
from models.user import User

class Reactor(Base):
    __tablename__ = "reactors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    image_url = Column(String(1000), nullable=True)
    video_url = Column(String(1000), nullable=True)

    description = Column(String(500), nullable=True)
    thermal_power = Column(Integer, nullable=True)
    electrical_power = Column(Integer, nullable=True)

    status = Column(String(20), nullable=False, default="draft", index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    formed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
