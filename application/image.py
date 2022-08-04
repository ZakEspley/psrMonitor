from PIL import Image, ImageOps
import face_recognition as fr
from flask import current_app


def shrinkImage(img_data, tmp_path):
    with Image.open(img_data) as img:
        img = ImageOps.exif_transpose(img)
        x = img.width
        y = img.height
        biggestDim = max(x, y)
        MAXSIZE = current_app.config["MAX_IMAGE_SIZE"]
        if biggestDim > MAXSIZE:
            ratio = MAXSIZE/biggestDim
            size = (round(x*ratio), round(y*ratio))
            img = img.resize(size)
        if tmp_path is None:
            img.save("tmp.png")
        else:
            img.save(tmp_path)

def cropImage(image_path, save_path, size):
    img = fr.load_image_file(image_path)
    face_location = fr.face_locations(img)
    if len(face_location) > 1:
        return len(face_location)
    elif len(face_location) == 0:
        return 0
    
    with Image.open(image_path) as face:
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
        face = face.resize(size)
        face.save(save_path)
        return 1