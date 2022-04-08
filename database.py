from models import NewUser, User, Token, TokenData
from fastapi import HTTPException, status, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from passlib.context import CryptContext
from jose import JWTError, jwt

from typing import Optional
from datetime import datetime, timedelta
from PIL import Image, ImageOps
import os
from models import Slideshow
import csv
import face_recognition as fr
from slidemaker import makeSlides
import pprint
# from main import oauth2_scheme

# client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
# db = client.slideshow
# users = db.users

SECRET_KEY = "39e8f0e7207e191b0662865b374e241980ad565f5eac08fc05cee487ae36547e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(60*0.5)
THUMBNAIL_SIZE = (128, 128)
SLIDE_PATH = os.path.join("imgs", "slides")
HOST_PATH = os.path.join("imgs", 'hosts')
THUMBNAIL_PATH = os.path.join("imgs", "thumbnails")
HEADSHOT_SIZE = (700,700)
TMP_FILE = os.path.join(".", "static", "imgs", "tmp", "tmp.png")
MAXSIZE = 1000

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

async def add_img_to_database(collection:Collection, file:UploadFile):
    filename = file.filename
    slide_path = os.path.join(SLIDE_PATH, filename)
    thumb_path = os.path.join(THUMBNAIL_PATH, "thumb_"+filename)
    data = {
        "filename": filename,
        "slide_path":slide_path,
        "thumb_path":thumb_path
    }
    slide_path = os.path.join(".", "static", slide_path)
    thumb_path = os.path.join('.', 'static', thumb_path)
    exists = await collection.find_one({"filename":filename})
    if not exists:
        try:
            with Image.open(file.file) as img:
                img.save(slide_path)
                img.thumbnail(THUMBNAIL_SIZE)
                img.save(thumb_path)
                result = await collection.insert_one(data)
                return True
        except OSError as e:
            print(f"ERROR: {e}")
            return False
    else:
        return False

async def get_all_img_thumbs(collection:Collection):
    imgs = await collection.find().to_list(None)
    thumb_paths = [img["thumb_path"] for img in imgs]
    return thumb_paths

async def create_new_slideshow(slideshowCollection:Collection, slideCollection:Collection, slideshow:Slideshow):
    slides = await slideCollection.find({"filename": {"$in":slideshow.slideList}}).to_list(None)
    slideshow.slideList = slides
    # print(slideshow.dict())
    result = await slideshowCollection.insert_one(slideshow.dict())
    return result.inserted_id

async def add_hosts_to_database(collection:Collection, hostCSV:UploadFile):
    contents = await hostCSV.read()
    contents = contents.decode()
    contents = contents.split("\r\n")
    headers = contents[0].split(",")
    headerLocations = {colName:headers.index(colName) for colName in headers}
    
    for host in contents[1:]:
        temp = {
            "Email": None,
            "First Name": None,
            "Last Name": None,
            "Pronouns": None,
            "Class": None,
            "Position": None
        }
        info = host.split(",")
        if len(host) <=1:
            continue
        for key in temp:
            temp[key] = info[headerLocations[key]]
        result = await collection.find_one({"Email": temp["Email"]})
        if result:
            await collection.replace_one({"Email": temp["Email"]}, temp)
        else:
            await collection.insert_one(temp)

async def add_host_img_to_database(collection:Collection, file:UploadFile):
    email = os.path.splitext(file.filename)[0]
    filename = f"{email}.png"
    
    img_path = os.path.join(HOST_PATH, filename)
    thumb_path = os.path.join(THUMBNAIL_PATH, "thumb_"+filename)
    data = {
        "Email": email,
        "filename": filename,
        "img_path":img_path
    }
    host_path = os.path.join(".", "static", img_path)
    thumb_path = os.path.join('.', 'static', thumb_path)
    host = await collection.find_one({"Email":email})
    # print(f"EXISTS: {exists}")
    # print(email)
    if host:
        try:
            #Shrink Image
            shrinkImage(file)
            cropped = cropImage(host_path, thumb_path)
            # with Image.open(file.file) as img:
            #     img = img.resize(HEADSHOT_SIZE)
            #     img.save(host_path)
            #     img.thumbnail(THUMBNAIL_SIZE)
            #     img.save(thumb_path)
            #     result = await collection.update_one({"Email": email}, {'$set':data})
            #     return True
            if not cropped:
                return (False, host)
            else:
                result = await collection.update_one({"Email": email}, {'$set':data})
                host = await collection.find_one({"Email":email})
                return (True, host)
        except OSError as e:
            print(f"ERROR: {e}")
            return (False, Exception())
    else:
        return (False, False)

async def manual_add_host_img_to_database(collection:Collection, file:UploadFile):
    email = os.path.splitext(file.filename)[0]
    filename = f"{email}.png"
    
    img_path = os.path.join(HOST_PATH, filename)
    thumb_path = os.path.join(THUMBNAIL_PATH, "thumb_"+filename)
    data = {
        "Email": email,
        "filename": filename,
        "img_path":img_path
    }
    host_path = os.path.join(".", "static", img_path)
    thumb_path = os.path.join('.', 'static', thumb_path)
    host = await collection.find_one({"Email":email})
    # print(f"EXISTS: {exists}")
    # print(email)
    if host:
        try:
            #Shrink Image
            with Image.open(file) as img:
                img = img.resize(HEADSHOT_SIZE)
                img.save(host_path)
                img = img.resize(THUMBNAIL_SIZE)
                img.save(thumb_path)
                result = await collection.update_one({"Email": email}, {'$set':data})
                host = await collection.find_one({"Email":email})
                return (True, host)
        except OSError as e:
            print(f"ERROR: {e}")
            return (False, Exception())
    else:
        return (False, False)

async def make_slideshow(timeSlotCollection:Collection, slideCollection: Collection, slideshowCollection: Collection, hostCollection:Collection, timeCSV:UploadFile):
    noProfiles, timeSlotModified = await fillTimeSlots(timeSlotCollection, hostCollection, timeCSV)
    # print(noProfiles)
    await deleteExcessTimeSlots(timeSlotCollection, timeSlotModified)
    timeslots = await timeSlotCollection.find().to_list(None)
    # pprint.pprint(timeslots)
    # timeslots = collapseTimeslots2(timeslots)
    
    for timeslot in timeslots:
        updatedTimeslot = makeSlides(timeslot)
        await timeSlotCollection.update_one({"Day": updatedTimeslot['Day'], "Time":updatedTimeslot['Time']}, {"$set":updatedTimeslot})


async def fillTimeSlots(timeSlotCollection: Collection, hostCollection: Collection, timeCSV: UploadFile):
    contents = await timeCSV.read()
    contents = contents.decode()
    contents = contents.split("\r\n")
    headers = contents[0].split(",")
    # headerLength = len(headers)
    # headerLocations = {colName:headers.index(colName) for colName in headers}
    noProfile = []
    timeSlotsModified = []
    hostCheckedOnce = []
    for timeslot in contents[1:]:
        info = timeslot.split(",")
        if len(info) <= 1:
            continue
        temp = {
            "Day": info[0],
            "Time": info[1],
            "Hosts": {}
        }
        hosts = info[2:]
        hostFound = False
        for hostEmail in hosts:
            # Use the emails to get the host profile from the host db
            result = await hostCollection.find_one({"Email": hostEmail})
            if result:
                if f"{result['Position']}s" not in temp['Hosts']:
                    temp['Hosts'][f"{result['Position']}s"] = []
                temp['Hosts'][f"{result['Position']}s"].append(result)

                if hostEmail not in hostCheckedOnce:
                        hostCheckedOnce.append(hostEmail)
                        result['timeslots'] = result['timeslots'] = [{
                            "firstslot":
                            {"Day": temp['Day'],
                             "Time":temp["Time"]
                             },
                                "lastslot":
                                    {"Day": temp['Day'],
                                     "Time":temp["Time"]
                                     },
                                "slots":[[
                                    {"Day": temp['Day'],
                                     "Time":temp["Time"]
                                     }
                            ]]
                        }]
                lastTimeslot = result['timeslots'][-1]
                lastSlot = lastTimeslot['slots'][-1]
                lastDayTime = lastSlot[-1]
                if temp["Day"] == lastDayTime["Day"]:
                    lastTimeInMinutes = getTimeInMinutes(lastDayTime['Time'])
                    currentTimeInMinutes = getTimeInMinutes(temp['Time'])
                    if currentTimeInMinutes - lastTimeInMinutes == 0:
                        lastTimeslot['lastslot'] = {"Day":temp['Day'], "Time":temp["Time"]}
                    elif currentTimeInMinutes - lastTimeInMinutes <= 30:
                        lastSlot.append({"Day":temp['Day'], "Time":temp["Time"]})
                        lastTimeslot['lastslot'] = {"Day":temp['Day'], "Time":temp["Time"]}
                    else:

                        result['timeslots'].append({
                            "firstslot":
                                {"Day":temp['Day'], 
                                "Time":temp["Time"]
                                },
                            "lastslot":
                                {"Day":temp['Day'],
                                "Time":temp["Time"]
                                },
                            "slots":[[
                                {"Day":temp['Day'],
                                "Time":temp["Time"]
                                }
                                ]]
                        })
                else:
                    result['timeslots'].append({
                                "firstslot":
                                    {"Day":temp['Day'], 
                                    "Time":temp["Time"]
                                    },
                                "lastslot":
                                    {"Day":temp['Day'],
                                    "Time":temp["Time"]
                                    },
                                "slots":[[
                                    {"Day":temp['Day'],
                                    "Time":temp["Time"]
                                    }
                                    ]]
                            })
                    
                await hostCollection.update_one({"Email": hostEmail}, {"$set":result})
                hostFound = True
            elif hostEmail != "":
                noProfile.append(hostEmail)
        
        if hostFound:
            result = await timeSlotCollection.find_one({"Day": temp["Day"], "Time": temp['Time']})
            if result:
                await timeSlotCollection.replace_one({"Day": temp["Day"], "Time": temp['Time']}, temp)
            else:
                await timeSlotCollection.insert_one(temp)
            timeSlotsModified.append((temp['Day'], temp['Time']))
    return (noProfile, timeSlotsModified)
        


async def deleteExcessTimeSlots(timeSlotCollection:Collection, modifiedTimeSlots:list):
    timeslots = await timeSlotCollection.find().to_list(None)
    for timeslot in timeslots:
        dayTime = (timeslot["Day"], timeslot["Time"])
        if dayTime not in modifiedTimeSlots:
            await timeSlotCollection.delete_one(timeslot)


def getTimeInMinutes(timeString:str):
    hours, minutes = map(int, timeString.split(":"))
    return 60*hours + minutes

def shrinkImage(file):
    with Image.open(file.file) as img:
        img = ImageOps.exif_transpose(img)
        x = img.width
        y = img.height
        biggestDim = max(x, y)
        # print(f'File: {name} \t\t\t Biggest Dim: {biggestDim}')
        if biggestDim > MAXSIZE:
            ratio = MAXSIZE/biggestDim
            size = (round(x*ratio), round(y*ratio))
            img = img.resize(size)
        img.save(TMP_FILE)

def cropImage(host_path, thumb_path):
    img = fr.load_image_file(TMP_FILE)
    face_location = fr.face_locations(img)
    if len(face_location) != 1:
        return False
    
    with Image.open(TMP_FILE) as face:
        top, right, bottom, left = face_location[0]
        dx = right - left
        dy = bottom - top
        s = 0.75
        crop = [left-dx*s, top-dy*s, right+dy*s, bottom+dy*s]
        
        if crop[0] < 0:
            crop[0] = 0
        
        if crop[1] < 0:
            crop[1] = 0
        
        if crop[2] > face.width:
            crop[2] = face.width
        
        if crop[3] > face.height:
            crop[3] = face.height
        
        dy = crop[3] - crop[1]
        dx = crop[2] - crop[0]

        if dy != dx:
            dy = min(dy,dx)
            dx = min(dy,dx)
        
        if crop[0] == 0:
            crop[2] = crop[0] + dx
        elif crop[2] == face.width:
            crop[0] = crop[2] - dx
        elif crop[1]==0 or crop[3]==face.height:
            x1 = crop[0]
            x2 = crop[2]
            c = (x1+x2)/2
            crop[0] = c-dx/2
            crop[2] = c+dx/2
        
        if crop[1] == 0:
            crop[3] = crop[1] + dy
        elif crop[3] ==  face.height:
            crop[1] = crop[3] - dy
        elif crop[0]==0 or crop[3]==face.width:
            y1 = crop[1]
            y2 = crop[3]
            c = (y1+y2)/2
            crop[1] = c-dy/2
            crop[3] = c+dy/2
        
        face = face.crop(crop)
        face = face.resize(HEADSHOT_SIZE)
        face.save(host_path)
        face = face.resize(THUMBNAIL_SIZE)
        face.save(thumb_path)
        return True