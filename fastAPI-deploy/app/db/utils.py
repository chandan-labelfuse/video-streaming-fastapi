from db import models
from db.database import SessionLocal

from core.security import get_password_hash

def create_user(email, password, username):
	db = SessionLocal()
	hashed_password = get_password_hash(password)
	db_user = models.User(email=email, username=username, password=hashed_password)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	print (db_user)

#print ("Creating User..")
#create_user('test@gmail.com', 'test', 'test')