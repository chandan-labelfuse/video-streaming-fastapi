from sqlalchemy.orm import Session
from db import models, schema

class UserCrud:
	@classmethod
	async def get_user(cls, db: Session, user_id: int):
		return db.query(models.User).filter(models.User.id == user_id).first()

	@classmethod
	async def get_user_by_email(cls, db: Session, email: str):
		print ("GET USER")
		return db.query(models.User).filter(models.User.email == email).first()

	@classmethod
	async def get_user_password(cls, db: Session, email: str):
		return db.query(models.User)
