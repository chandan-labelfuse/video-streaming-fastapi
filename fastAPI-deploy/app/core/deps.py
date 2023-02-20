from typing import Optional
from pydantic import BaseModel

from fastapi import Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from core.auth import oauth2_scheme
from core.exceptions import credentials_exception
from db.crud import UserCrud
from db.deps import get_db


class TokenData(BaseModel):
    username: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	try:
		payload = jwt.decode(
			token,
			"as1234dfg",
			algorithms=["HS256"],
			options={"verify_aud": False},
		)

		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception

		token_data = TokenData(username=username)

	except JWTError:
		raise credentials_exception

	user = await UserCrud.get_user_by_email(db, username)
	if user is None:
		raise credentials_exception
	return user
