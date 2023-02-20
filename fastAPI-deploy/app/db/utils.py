from db import models
from db.database import SessionLocal

def create_user(email, password, username):
	db = SessionLocal()
	db_user = models.User(email=email, username=username, password=password)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	print (db_user)

#create_user('test@gmail.com', 'test')