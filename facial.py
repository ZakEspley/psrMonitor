from PIL import Image, ImageOps, ImageDraw
import face_recognition as fr
imgPath = "/home/zak/Pictures/headshot.jpeg"
img = fr.load_image_file(imgPath)
face_location = fr.face_locations(img)

if len(face_location) != 1:
    print("Something wrong with face_locations")
    print("Too many or too few")
    print(face_location)
    raise Exception

with Image.open(imgPath) as face:
    top, right, bottom, left = face_location[0]
    dx = right - left
    dy = bottom - top
    s = 0.5
    crop = (left-dx*s, top-dy*s, right+dy*s, bottom+dy*s)
    
    face = face.crop(crop)
    face.show()