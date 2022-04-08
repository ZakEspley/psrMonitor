from fastapi import FastAPI, Request, Depends, status, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import datetime, timedelta

import uvicorn

from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from models import NewUser, UserOut, OAuth2PasswordBearerCookie, Slideshow, OID
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
    app.slides = app.mongodb.slides
    app.slideshows = app.mongodb.slideshows
    app.hosts = app.mongodb.hosts
    app.timeslots = app.mongodb.timeslots

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
async def logout_and_remove_cookie():
    response = RedirectResponse(url="/login")
    response.delete_cookie("Authorization")
    return response

@app.get("/createNewSlideshow", response_class=HTMLResponse)
async def selectSlidesPage(request:Request, user:User=Depends(get_current_user)):
    imgs = await get_all_img_thumbs(app.slides)
    return templates.TemplateResponse("gallery.html", {'imgs':imgs, "request":request})

@app.post("/createNewSlideshow")
async def createNewSlideshow(request:Request, slideshow: Slideshow=Depends(Slideshow.as_form)):
# async def createNewSlideshow(request:Request, slideshow: Slideshow=Depends(Slideshow.as_form)):
    slideShowId = await create_new_slideshow(app.slideshows, app.slides, slideshow)
    response = RedirectResponse(url=f"/viewSlideshow/{slideShowId}", status_code=status.HTTP_303_SEE_OTHER)
    return response
    # print(f"Creating New Slideshow {slideShowName}")

@app.get("/viewSlideshow/{id}")
async def viewSlideShow(request:Request, id):
    slideshowFuture = await app.slideshows.find_one({"_id":id})
    slideshow = Slideshow.from_mongo(slideshowFuture)
    print(slideshow)
    return templates.TemplateResponse("slideshowView.html", {"request": request, "slideshow":slideshow})

@app.get("/addHosts", response_class=HTMLResponse)
async def getAddHosts(request:Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("uploadUsers.html", {"request":request})
    
@app.post("/addHosts", response_class=RedirectResponse)
async def postAddHosts(request:Request, hostCSV:UploadFile=File(...), user:User=Depends(get_current_user)):
    await add_hosts_to_database(app.hosts, hostCSV)
    # return templates.TemplateResponse("upload.html", {"request":request})
    return RedirectResponse(url="/addHostsImages", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/addHostsImages", response_class=HTMLResponse)
async def getAddHosts(request:Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("uploadUsersImages.html", {"request":request})

@app.post("/addHostsImages", response_class=HTMLResponse)
async def postAddHosts(request:Request, images:List[UploadFile]=File(...), user:User=Depends(get_current_user)):
    success = []
    failure = []
    noProfile= []
    for img in images:
        if "image" not in img.content_type:
            continue
        cropped, outcome = await add_host_img_to_database(app.hosts, img)
        if not cropped:
            if isinstance(outcome, Exception):
                print("Something went wrong")
            elif not outcome:
                noProfile.append(img.filename)
            else:
                failure.append(outcome)
        else:
            success.append(outcome)

    return templates.TemplateResponse("imageUploadReview.html", {"request":request, "noProfile":noProfile, "failure":failure, "success":success})

@app.get("/manuallyAddHostsImages", response_class=HTMLResponse)
async def getManuallyAddHosts(request:Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("manualUploadUsersImages.html", {"request":request})

@app.post("/manuallyAddHostsImages", response_class=HTMLResponse)
async def postManuallyAddHosts(request:Request, images:List[UploadFile]=File(...), user:User=Depends(get_current_user)):
    success = []
    noProfile= []
    for img in images:
        if "image" not in img.content_type:
            continue
        success, host = await add_host_img_to_database(app.hosts, img)
        if not success:
            if isinstance(host, Exception):
                print("Something went wrong")
            elif not host:
                noProfile.append(img.filename)
        else:
            success.append(host)

    return templates.TemplateResponse("imageUploadReview.html", {"request":request, "noProfile":noProfile, "failure":[], "success":success})

@app.get("/makeSlideshows", response_class=HTMLResponse)
async def getMakeSlideshows(request:Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("makeSlideshows.html", {"request":request})

@app.post("/makeSlideshows", response_class=RedirectResponse)
async def postMakeSlideshows(request:Request, timeCSV:UploadFile=File(...), user:User=Depends(get_current_user)):
    # await add_hosts_to_database(app.hosts, hostCSV)
    await make_slideshow(app.timeslots, app.slides, app.slideshows, app.hosts, timeCSV)
    # return templates.TemplateResponse("upload.html", {"request":request})
    return RedirectResponse(url="/play", status_code=status.HTTP_303_SEE_OTHER)

@app.get('/play', response_class=HTMLResponse)
async def getPlaySlideshow(request:Request, user:User=Depends(get_current_user)):
    timeslots = await app.timeslots.find().to_list(None)
    return templates.TemplateResponse("/slideshowView2.html", {"request":request, "timeslots":timeslots, "duration":10, "transition":0.5})

@app.get("/addSlides", response_class=HTMLResponse)
async def addSlidesPage(request:Request, user:User=Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request":request})

@app.post("/addSlides")
async def addSlides(slides:List[UploadFile]=File(...), user:User=Depends(get_current_user)):
    for slide in slides:
        if "image" not in slide.content_type:
            continue
        await add_img_to_database(app.slides, slide)
    return {"Images Uploaded"}


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
