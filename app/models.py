from sqlalchemy import Column, Integer, String
from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    status = Column(String, default="Pending")
    team_code = Column(String, nullable=True, index=True)
    is_checked_in = Column(Boolean, default=False)
    
class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)