from db.database import SessionLocal, engine

def get_db():
	print ("Get DB")
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()