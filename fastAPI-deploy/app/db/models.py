from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)	
	email = Column(String, unique=True, index=True)
	username = Column(String)
	password = Column(String)

	settings = relationship("Setting", back_populates="user")


class Setting(Base):
	__tablename__ = "settings"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))

	user = relationship("User", back_populates="settings")