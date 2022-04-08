from PIL import Image, ImageDraw, ImageFont

# This function will be called to make the images for a given timeslot.
# You can replace the functions called inside of this function to make
# the slides look however you'd like.
def makeSlides(timeslot):
    zakAndRaffiSlides(timeslot)
    

def zakAndRaffiSlides(timeslot):
    SIZE = (600, 600)
    RADIUS = 75
    # D_IM1 = (362,477)
    # D_IM2 = (1107, 477)
    D_IM1 = (108,188)
    D_IM2 = (1080, 188)
    
    # D_IM2TEXT = (1172, 312)
    # D_IM1TEXT = (419, 312)
    # D_IM2TEXT = (1356, 379)
    # D_IM1TEXT = (606, 379)
    BACKGROUND_SIZE = (740, 852)
    BACGROUND_COLOR = (252, 245, 221, 255)
    BACKGROUND_BORDER_COLOR = (55, 108, 178, 255)
    BORDER_WIDTH = 8 #px
    D_IM1TEXT = (147, 225)
    D_IM2TEXT = (1118, 225)
    S_IM = (718, 477)
    # S_IMTEXT = (773, 314)
    S_IMTEXT = (960, 379)
    FONT_SIZE = 44
    FONT_COLOR = (0, 0, 0, 255)
    MAX_TEXT_WIDTH = 650
    FONT_FILE = "./fonts/AstroSpace-eZ2Bg.ttf"
    SPACING = 10
    ALIGNMENT = "center"
    ANCHOR = "mm"

#bac1b8ff
    hosts = timeslot["Hosts"]
    # hosts[host['Position']].append(host)
    
    taTotal = len(hosts['TAs'])
    laTotal = len(hosts['LAs'])
    
    imgCounter = 1
    taCounter = 0
    laCounter = 0

    while taCounter < taTotal:
        if taTotal - taCounter != 1:
            templateName = "broida.png"
            doubles = True
            host1 = hosts["TAs"][taCounter]
            host2 = hosts["TAs"][taCounter + 1]
            taCounter += 2
        else:
            templateName = "broida.png"
            doubles = False
            host1 = hosts["TAs"][taCounter]
            taCounter += 1
        
        with Image.open(f"./static/imgs/templates/{templateName}").convert("RGBA") as base:
            with Image.open(f"./static/{host1['img_path']}") as im1:
                im1 = im1.resize(SIZE)
                mask = Image.new("L", SIZE, 0)
                draw = ImageDraw.Draw(mask)
                draw
                draw.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=255)
                im1.putalpha(mask)
                draw1 = ImageDraw.Draw(im1)
                draw1.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=None, outline=(0,0,0,255), width=4)
                drawf = ImageDraw.Draw(base)

                if host1["Pronouns"] != "NA":
                    text = f"{host1['First Name']} {host1['Last Name']}\n{host1['Pronouns']}\n{host1['Class']} - {host1['Position']}"
                else:
                    text = f"{host1['First Name']} {host1['Last Name']}\n{host1['Class']} - {host1['Position']}"

                name = f"{host1['First Name']} {host1['Last Name']}"

                if doubles:
                    base.paste(im1, D_IM1, im1)
                    if font.getsize(name)[0] > MAX_TEXT_WIDTH:
                        newFont = checkName(name, FONT_SIZE, MAX_TEXT_WIDTH, FONT_FILE)
                        drawf.text(D_IM1TEXT, text, font=newFont, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    else:
                        drawf.text(D_IM1TEXT, text, font=font, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)

                    with Image.open(f"./static/{host2['img_path']}") as im2:
                        im2 = im2.resize(SIZE)
                        draw2 = ImageDraw.Draw(im2)
                        draw2.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=None, outline=(0,0,0,255), width=4)
                        base.paste(im2, D_IM2, im2)
                        if host2["Pronouns"] != "NA":
                            text = f"{host2['First Name']} {host2['Last Name']}\n{host2['Pronouns']}\n{host2['Class']} - {host2['Position']}"
                        else:
                            text = f"{host2['First Name']} {host2['Last Name']}\n{host2['Class']} - {host2['Position']}"
                else:
                    if font.getsize(name)[0] > MAX_TEXT_WIDTH:
                        newFont = checkName(name, FONT_SIZE, MAX_TEXT_WIDTH, FONT_FILE)
                        drawf.text(S_IMTEXT, text, font=newFont, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    else:
                        drawf.text(S_IMTEXT, text, font=font, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    base.paste(im1, S_IM, im1)

                base = base.convert("RGBA")
                base.save(f"./static/imgs/slides/TAs/{timeslot['Day']}{timeslot['Time']}_{imgCounter}.png")
        imgCounter += 1
    
    imgCounter = 0
    while laCounter < laTotal:
        if laTotal - laCounter != 1:
            templateName = "doublesTemplate.png"
            doubles = True
            host1 = hosts["LAs"][laCounter]
            host2 = hosts["LAs"][laCounter + 1]
            laCounter += 2
        else:
            templateName = "singlesTemplate.png"
            doubles = False
            host1 = hosts["LAs"][laCounter]
            laCounter += 1
        
        with Image.open(f"./static/imgs/templates/{templateName}").convert("RGBA") as base:
            with Image.open(f"./static/{host1['img_path']}") as im1:
                im1 = im1.resize(SIZE)
                mask = Image.new("L", SIZE, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=255)
                im1.putalpha(mask)
                draw1 = ImageDraw.Draw(im1)
                draw1.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=None, outline=(0,0,0,255), width=4)
                drawf = ImageDraw.Draw(base)

                if host1["Pronouns"] != "NA":
                    text = f"{host1['First Name']} {host1['Last Name']}\n{host1['Pronouns']}\n{host1['Class']} - {host1['Position']}"
                else:
                    text = f"{host1['First Name']} {host1['Last Name']}\n{host1['Class']} - {host1['Position']}"

                name = f"{host1['First Name']} {host1['Last Name']}"

                if doubles:
                    base.paste(im1, D_IM1, im1)
                    if font.getsize(name)[0] > MAX_TEXT_WIDTH:
                        newFont = checkName(name, FONT_SIZE, MAX_TEXT_WIDTH, FONT_FILE)
                        drawf.text(D_IM1TEXT, text, font=newFont, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    else:
                        drawf.text(D_IM1TEXT, text, font=font, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)

                    with Image.open(f"./static/{host2['img_path']}") as im2:
                        if host2["Pronouns"] != "NA":
                            text = f"{host2['First Name']} {host2['Last Name']}\n{host2['Pronouns']}\n{host2['Class']} - {host2['Position']}"
                        else:
                            text = f"{host2['First Name']} {host2['Last Name']}\n{host2['Class']} - {host2['Position']}"
                        im2 = im2.resize(SIZE)
                        im2.putalpha(mask)
                        draw2 = ImageDraw.Draw(im2)
                        draw2.rounded_rectangle([(0,0), SIZE], radius=RADIUS, fill=None, outline=(0,0,0,255), width=4)
                        if font.getsize(name)[0] > MAX_TEXT_WIDTH:
                            newFont = checkName(name, FONT_SIZE, MAX_TEXT_WIDTH, FONT_FILE)
                            drawf.text(D_IM2TEXT, text, font=newFont, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                        else:
                            drawf.text(D_IM2TEXT, text, font=font, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                        base.paste(im2, D_IM2, im2) 
                else:
                    if font.getsize(name)[0] > MAX_TEXT_WIDTH:
                        newFont = checkName(name, FONT_SIZE, MAX_TEXT_WIDTH, FONT_FILE)
                        drawf.text(S_IMTEXT, text, font=newFont, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    else:
                        drawf.text(S_IMTEXT, text, font=font, fill=FONT_COLOR, spacing=SPACING, align=ALIGNMENT, anchor=ANCHOR)
                    base.paste(im1, S_IM, im1)

                base = base.convert("RGBA")
                base.save(f"./static/imgs/slides/LAs/{timeslot['Day']}{timeslot['Time']}_{imgCounter}.png")
        imgCounter += 1

def checkName(text, font_size, max_size, fontfile):
    font = ImageFont.truetype(fontfile, font_size)
    while font.getsize(text)[0] > max_size:
        font_size -= 1
        font = ImageFont.truetype(fontfile, font_size)
    return font

                    