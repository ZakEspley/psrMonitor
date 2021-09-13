from fastapi import FastAPI, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import datetime, timedelta

import uvicorn

from motor.motor_asyncio import AsyncIOMotorClient

from models import NewUser, UserOut, OAuth2PasswordBearerCookie
from database import *
from database import ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="token")
# manager = LoginManager(SECRET_KEY, "/token", use_cookie=True)

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_handler(request, exec):
    if request.method == "POST":
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/login")

#### Dependencies
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(app.users, token_data.username)
    if user is None:
        raise credentials_exception
    return user


### Path Operation Functions

@app.on_event("startup")
async def start_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client["slideshow"]
    app.users = app.mongodb.users

@app.on_event("shutdown") 
async def shutdown_db_client():
    app.mongodb_client.close()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {'request':request})

@app.get("/login", response_class=HTMLResponse)
async def loginPage(request:Request):
    return templates.TemplateResponse("login.html", {'request':request})

@app.get('/slideshow', response_class=HTMLResponse)
async def slideshow(request: Request):
    return templates.TemplateResponse("slideshow.html", {'request':request})

@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/login")
    response.delete_cookie("Authorization")
    return response


@app.post("/signup", response_model=UserOut)
async def signup(newuser:NewUser):
    response = await create_new_user(app.users, newuser)
    if response:
        return response
    raise HTTPException(status_code=400, detail="Error of some sort")

@app.post("/token")
async def login(response:Response, request:Request, form_data:OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(app.users, form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)    
    access_token = create_access_token(
        data={"sub":user.username},
        expires_delta=access_token_expires
    )
    
    # access_token = manager.create_access_token(
    #     expires=access_token_expires,
    #     data={'sub': user.username}
    #     )
    # manager.set_cookie(response, access_token)
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        expires=access_token_expires,
        httponly=True,
        samesite="lax"
    )
    return response
    # return {"Message"}


@app.get("/users/me/", response_model=UserOut)
async def read_users_me(user:User = Depends(get_current_user)):
    return user



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True
    )
