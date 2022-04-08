from pydantic import BaseModel, Field, validator, EmailStr, conlist, Json, BaseConfig
from pydantic.fields import ModelField
from typing import Optional, Type, List
import uuid
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import status, Request, Form
import inspect
from datetime import datetime, time
from bson.json_util import ObjectId



# def as_form(cls: Type[BaseModel]):
#     new_parameters = []

#     for field_name, model_field in cls.__fields__.items():
#         model_field: ModelField  # type: ignore

#         if not model_field.required:
#             new_parameters.append(
#                 inspect.Parameter(
#                     model_field.alias,
#                     inspect.Parameter.POSITIONAL_ONLY,
#                     default=Form(model_field.default),
#                     annotation=model_field.outer_type_,
#                 )
#             )
#         else:
#             new_parameters.append(
#                 inspect.Parameter(
#                     model_field.alias,
#                     inspect.Parameter.POSITIONAL_ONLY,
#                     default=Form(...),
#                     annotation=model_field.outer_type_,
#                 )
#             )

#     async def as_form_func(**data):
#         return cls(**data)

#     sig = inspect.signature(as_form_func)
#     sig = sig.replace(parameters=new_parameters)
#     as_form_func.__signature__ = sig  # type: ignore
#     setattr(cls, 'as_form', as_form_func)
#     return cls


class OID(str):
  @classmethod
  def __get_validators__(cls):
      yield cls.validate

  @classmethod
  def validate(cls, v):
      print("VALIDATE", type(v))
      try:
          return ObjectId(str(v))
      except InvalidId:
          raise ValueError("Not a valid ObjectId")


class MongoModel(BaseModel):

  class Config(BaseConfig):
      allow_population_by_field_name = True
      json_encoders = {
          datetime: lambda dt: dt.isoformat(),
          ObjectId: lambda oid: str(oid),
      }

  @classmethod
  def from_mongo(cls, data: dict):
      """We must convert _id into "id". """
      if not data:
          return data
      id = data.pop('_id', None)
      return cls(**dict(data, id=id))

  def mongo(self, **kwargs):
      exclude_unset = kwargs.pop('exclude_unset', True)
      by_alias = kwargs.pop('by_alias', True)

      parsed = self.dict(
          exclude_unset=exclude_unset,
          by_alias=by_alias,
          **kwargs,
      )

      # Mongo uses `_id` as default key. We should stick to that as well.
      if '_id' not in parsed and 'id' in parsed:
          parsed['_id'] = parsed.pop('id')

      return parsed


def as_form(cls: Type[MongoModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """

    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            # default=default,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls

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

@as_form
class Slideshow(MongoModel):
    id: Optional[OID] = Field(default_factory=OID, alias="_id")
    slideShowName: str = Field(...)
    mondayTime1: time = Field(None)
    mondayTime2: time = Field(None)
    tuesdayTime1: time = Field(None)
    tuesdayTime2: time = Field(None)
    wednesdayTime1: time = Field(None)
    wednesdayTime2: time = Field(None)
    thursdayTime1: time = Field(None)
    thursdayTime2: time = Field(None)
    fridayTime1: time = Field(None)
    fridayTime2: time = Field(None)
    slideList: Json[List[str]] = Field(None)

    @validator("mondayTime1", 'mondayTime2', 'tuesdayTime1', 'tuesdayTime2', 'wednesdayTime1', 'wednesdayTime2', 'thursdayTime1', 'thursdayTime2', 'fridayTime1', 'fridayTime2')
    def time_validator(cls, value):
        dt = datetime.now()
        if value is None:
            return None
        return datetime.combine(dt.date(), value)
    
    @validator("id")
    def id_validator(cls, value):
        return OID(value)

    