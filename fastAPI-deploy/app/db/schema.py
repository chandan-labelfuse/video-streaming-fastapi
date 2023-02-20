from typing import List
from pydantic import BaseModel


class Setting(BaseModel):
	id: int
	user_id: int

	class Config:
		orm_mode = True


class UserBase(BaseModel):
	email: str

class UserCreate(BaseModel):
	password: str

class User(UserBase):
	id: int
	username: str
	settings: List[Setting] = []

	class Config:
		orm_mode = True