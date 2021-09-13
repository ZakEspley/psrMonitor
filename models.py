from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import uuid
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import status, Request

class NewUser(BaseModel):
    username:str = Field(min_length=3, max_length=40)
    password:str = Field(...)
    email: Optional[EmailStr]

    @validator("username")
    @classmethod
    def valid_username(cls, value):
        if len(value) < 3 or len(value) > 40:
            raise HTTPException(400, "Username must be between 3 and 40 characters.")
        return value

    @validator("password")
    @classmethod
    def valid_password(cls, value):
        if len(value) < 3 or len(value) > 40:
            raise HTTPException(400, "Password must be between 3 and 50 characters.")
        return value

class UserOut(BaseModel):
    username:str = Field(...)
    email:Optional[EmailStr]

class User(BaseModel):
    username:str = Field(...)
    hashed_password:str = Field(...)
    email:Optional[EmailStr]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
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
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )
            else:
                return None
        return param