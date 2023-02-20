from fastapi.security import OAuth2PasswordBearer, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from jose import jwt

from db.crud import UserCrud
from datetime import datetime, timedelta
from db.deps import get_db

class OAuth2PasswordBearerCookie(OAuth2):
	def __init__(
		self,
		tokenUrl: str,
		scheme_name: str = None,
		scopes: dict = None,
		auto_error: bool = True

	):
		if not scopes:
			scopes = {}
		flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
		super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

	async def __call__(self, request: Request):
		header_authorization: str = request.headers.get("Authorization")
		cookie_authorization: str = request.cookies.get("Authorization")

		header_scheme, header_param = get_authorization_scheme_param(
			header_authorization
		)

		cookie_scheme, cookie_param = get_authorization_scheme_param(
			cookie_authorization
		)

		if header_scheme.lower() == "bearer":
			authorization = True
			scheme = header_scheme
			param = header_param

		elif cookie_scheme.lower() == "bearer":
			authorization = True
			scheme = cookie_scheme
			param = cookie_param
		else:
			authorization = False

		if not authorization or scheme.lower() != "bearer":
			if self.auto_error:
				raise HTTPException(
					status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
				)
			else:
				return None
		print (param)

		return param


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="login")


async def authenticate(email: str, password: str, db: Session):
	print ("authenticate")
	user = await UserCrud.get_user_by_email(db, email)
	print (user)
	if not user:
		return None
	return user


def create_access_token(sub: str):
	return _create_token(
		token_type = "access_token",
		lifetime = timedelta(minutes=int(60 * 24 * 8)),
		sub=sub
	)


def _create_token(token_type:str, lifetime: timedelta, sub:str):
	payload = {}
	expire = datetime.utcnow() + lifetime
	payload["type"] = token_type
	payload["exp"] = expire
	payload["iat"] = datetime.utcnow()
	payload["sub"] = str(sub)

	return jwt.encode(payload, "as1234dfg", algorithm="HS256")

	