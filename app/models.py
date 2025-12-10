from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from app.db import Base
from sqlalchemy.orm import relationship
from typing import Optional
from datetime import datetime




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) 