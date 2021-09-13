from models import NewUser, User, Token, TokenData
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from passlib.context import CryptContext
from jose import JWTError, jwt

from typing import Optional
from datetime import datetime, timedelta
# from main import oauth2_scheme

# client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
# db = client.slideshow
# users = db.users

SECRET_KEY = "39e8f0e7207e191b0662865b374e241980ad565f5eac08fc05cee487ae36547e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(60*0.5)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return pwd_context.hash(password)

async def get_user(collection:Collection, username:str):
    user_data = await collection.find_one({"username":username})
    if user_data:
        return User(**user_data)
    return False

async def authenticate_user(collection: Collection, form_data):
    user_data = await collection.find_one({"username":form_data.username})
    if not user_data:
        # raise HTTPException(400, "Incorrect username or password")
        return False
    user = User(**user_data)
    if not verify_password(form_data.password, user.hashed_password):
        return False
        # raise HTTPException(400, "Incorrect username or password")
    return user

def create_access_token(data:dict, expires_delta:Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_new_user(collection:Collection, newuser:NewUser):
    cursor = collection.find(newuser.dict(include={"username"}))
    found = await cursor.to_list(1)
    newuser.password = get_password_hash(newuser.password)
    user = User(
        username=newuser.username,
        hashed_password=newuser.password,
        email=newuser.email
        )
    if len(found) == 1:
        raise HTTPException(400, "Username in use")
    else:
        result = await collection.insert_one(user.dict())
        return user