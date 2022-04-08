from PIL import Image, ImageDraw, ImageFont

# This function will be called to make the images for a given timeslot.
# You can replace the functions called inside of this function to make
# the slides look however you'd like.
def makeSlides(timeslot):
    updatedTimeslot = zakSlides(timeslot)
    return updatedTimeslot


def zakSlides(timeslot):
    ########################################################
    #              Constants Across all images.            #
    ########################################################
    SIZE = (600, 600)                               #Size of headshot
    RADIUS = 75                                     #Radius of headshot&card
    TEXT_RADIUS = 50                                #Raduis of textbox
    MAX_TEXT_SIZE = (600, 125)                      #Max size of the text can have.
    TEXT_SIZE = (650, 165)                          #Size of the textbox
    CARD_SIZE = (740, 875)                          #Size of the cards
    BACKGROUND_COLOR = (252, 245, 221, 255)          #Color of the card.
    BACKGROUND_BORDER_COLOR = (55, 108, 178, 255)   #Border color.
    BORDER_WIDTH = 8 #px                            #Border width
    TEXT_BACKGROUND_COLOR = (88, 186, 216, 255)     #Color of the text box.

    TITLE = (650,44)                                #Position of the title textbox
    TITLE_RADIUS = 5                                #Radius of the title textbox
    TITLE_SIZE = (626, 107)                         #Size of the title textbox
    #Region occupied by the title textbox on the background image.
    TITLE_REGION = [TITLE, [sum(x) for x in zip(TITLE, TITLE_SIZE)]]
    #Position of the title text. Anchor position is in the center.
    TITLE_TEXT = [x[0]+x[1]/2 for x in zip(TITLE, TITLE_SIZE)]
    TITLE_FONT_SIZE = 80                            #Title font size
    TITLE_FONT_COLOR = (0, 0, 0, 255)               #Title font color
    TITLE_FONT_FILE = "./fonts/TitanOne-Regular.ttf"#Title font

    SPACING = 15
    ALIGNMENT = "center"
    ANCHOR = "mm"
    titleFont = ImageFont.truetype(TITLE_FONT_FILE, TITLE_FONT_SIZE)
    titleStyles = {
        "fill": TITLE_FONT_COLOR,
        "font": titleFont,
        "spacing": SPACING,
        "align": ALIGNMENT,
        "anchor": ANCHOR
    }
    #======================================================#

    ########################################################
    # Card 1 of double slide (slide with two people on it) #
    ########################################################
    D_CARD1 = (108,188)                 #Position of the card1
    D_CARD1_TEXT_BG = (147, 225)        #Position of textbox
    D_IM1 = (181,410)                   #Position of the first headshot

    # Region occupied by card one on the background image.
    D_CARD1_REGION = [D_CARD1, [sum(x) for x in zip(D_CARD1, CARD_SIZE)]]
    # Region occupied by the text box on the background image.
    D_CARD1_TEXT_REGION = [D_CARD1_TEXT_BG, [sum(x) for x in zip(D_CARD1_TEXT_BG,TEXT_SIZE)]]
    #Position of text. The anchor point is the center.
    D_IM1TEXT = (D_CARD1_TEXT_BG[0]+TEXT_SIZE[0]/2, D_CARD1_TEXT_BG[1]+TEXT_SIZE[1]/2+7)
    #======================================================#

    ########################################################
    # Card 2 of double slide (slide with two people on it) #
    ########################################################
    D_CARD2 = (1080,188)                 #Position of the card2
    D_CARD2_TEXT_BG = (1118, 225)        #Position of textbox
    D_IM2 = (1152,410)                   #Position of the first headshot

    # Region occupied by card two on the background image.
    D_CARD2_REGION = [D_CARD2, [sum(x) for x in zip(D_CARD2, CARD_SIZE)]]
    # Region occupied by the text box on the background image.
    D_CARD2_TEXT_REGION = [D_CARD2_TEXT_BG, [sum(x) for x in zip(D_CARD2_TEXT_BG,TEXT_SIZE)]]
    #Position of text. The anchor point is the center.
    D_IM2TEXT = (D_CARD2_TEXT_BG[0]+TEXT_SIZE[0]/2, D_CARD2_TEXT_BG[1]+TEXT_SIZE[1]/2+7)
    #======================================================#

    ###########################################################
    # Only card of single slide (slide with one person on it) #
    ###########################################################
    S_CARD = (590,188)                  #Position of the card
    S_CARD_TEXT_BG = (629, 225)         #Position of textbox
    S_IM = (660,410)                    #Position of the first headshot

    # # Region occupied by card two on the background image.
    # S_CARD_REGION = [S_CARD, [sum(x) for x in zip(S_CARD, CARD_SIZE)]]
    # # Region occupied by the text box on the background image.
    # S_CARD_TEXT_REGION = [D_CARD2_TEXT_BG, [sum(x) for x in zip(D_CARD2_TEXT_BG,TEXT_SIZE)]]
    #Position of text. The anchor point is the center.
    S_IMTEXT = (S_CARD_TEXT_BG[0]+TEXT_SIZE[0]/2, S_CARD_TEXT_BG[1]+TEXT_SIZE[1]/2+7)
    #========================================================#

    FONT_SIZE = 80
    FONT_COLOR = (0, 0, 0, 255)
    
    # FONT_FILE = "./fonts/AstroSpace-eZ2Bg.ttf"
    # FONT_FILE = "./fonts/ChangaOne-Regular.ttf"
    # FONT_FILE = "./fonts/GoblinOne-Regular.ttf"
    # FONT_FILE = "./fonts/BowlbyOneSC-Regular.ttf"
    FONT_FILE = "./fonts/LuckiestGuy-Regular.ttf"

    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    fontStyles = {
        "fill": FONT_COLOR,
        "font": font,
        "spacing": SPACING,
        "align": ALIGNMENT,
        "anchor": ANCHOR
    }

    # las = timeslot["Hosts"]["LAs"][1:3]
    templateName = "broida.png"
    day = timeslot['Day']
    time = timeslot["Time"]
    timeslot['imgs'] = []
    for position, hosts in timeslot['Hosts'].items():
        titleText = f"{position} On Duty"
        positionTotal = len(hosts)
        counter = 0
        imgcounter = 1
        while counter < positionTotal:

            with Image.open(f"./static/imgs/templates/{templateName}").convert("RGBA") as base:
                #Makes the title textbox
                makeCard(base, 
                    position=TITLE, 
                    size=TITLE_SIZE, 
                    radius=TITLE_RADIUS, 
                    backgroundColor=BACKGROUND_COLOR, 
                    borderColor=BACKGROUND_BORDER_COLOR, 
                    borderWidth=BORDER_WIDTH,
                    text=titleText,
                    textPosition=TITLE_TEXT,
                    textStyles=titleStyles)

                host1 = hosts[counter]
                counter += 1
                with Image.open(f"./static/{host1['img_path']}") as im1:
                    slot = checkTimeslot(timeslot['Day'], timeslot['Time'], host1['timeslots'])
                    times = getWorkHoursString(slot['firstslot']['Time'], slot['lastslot']['Time'])
                    if host1["Pronouns"] != "NA":
                        info = f"{host1['First Name']} {host1['Last Name']} ({host1['Pronouns']})\n{host1['Class']} - {host1['Position']}\n{times}"
                    else:
                        info = f"{host1['First Name']} {host1['Last Name']}\n{host1['Class']} - {host1['Position']}\n{times}"

                    infoStyles = fontStyles.copy()
                    size = font.getsize_multiline(info, spacing=SPACING)
                    if size[0] > MAX_TEXT_SIZE[0] or  size[1] > MAX_TEXT_SIZE[1]:
                        infoStyles['font'] = checkName(info, FONT_SIZE, MAX_TEXT_SIZE, FONT_FILE, SPACING)
                    if positionTotal - counter != 0:
                        makeCard(base, 
                            position=D_CARD1,
                            size=CARD_SIZE,
                            radius=RADIUS,
                            backgroundColor=BACKGROUND_COLOR,
                            borderColor=BACKGROUND_BORDER_COLOR,
                            borderWidth=BORDER_WIDTH,
                            text=info,
                            textPosition=D_IM1TEXT,
                            textStyles=infoStyles,
                            textBoxPosition=D_CARD1_TEXT_BG,
                            textBoxSize=TEXT_SIZE,
                            textBackgroundcolor=TEXT_BACKGROUND_COLOR,
                            textBorderColor=BACKGROUND_BORDER_COLOR,
                            textBorderWidth=BORDER_WIDTH,
                            textRadius=TEXT_RADIUS,
                            img=im1,
                            imgPosition=D_IM1,
                            imgSize=SIZE,
                            imgBorderColor=BACKGROUND_BORDER_COLOR,
                            imgBorderWidth=BORDER_WIDTH,
                            imgRadius=RADIUS)
                        
                        host2 = hosts[counter]
                        counter += 1
                        with Image.open(f"./static/{host2['img_path']}") as im2:
                            slot = checkTimeslot(timeslot['Day'], timeslot['Time'], host2['timeslots'])
                            times = getWorkHoursString(slot['firstslot']['Time'], slot['lastslot']["Time"])
                            if host2["Pronouns"] != "NA":
                                info = f"{host2['First Name']} {host2['Last Name']}\n{host2['Pronouns']}\n{host2['Class']} - {host2['Position']}\n{times}"
                            else:
                                info = f"{host2['First Name']} {host2['Last Name']}\n{host1['Class']} - {host2['Position']}\n{times}"


                            size = font.getsize_multiline(info, spacing=SPACING)
                            if size[0] > MAX_TEXT_SIZE[0] or  size[1] > MAX_TEXT_SIZE[1]:
                                infoStyles['font'] = checkName(info, FONT_SIZE, MAX_TEXT_SIZE, FONT_FILE, SPACING) 
                                        
                            makeCard(base, 
                                position=D_CARD2,
                                size=CARD_SIZE,
                                radius=RADIUS,
                                backgroundColor=BACKGROUND_COLOR,
                                borderColor=BACKGROUND_BORDER_COLOR,
                                borderWidth=BORDER_WIDTH,
                                text=info,
                                textPosition=D_IM2TEXT,
                                textStyles=infoStyles,
                                textBoxPosition=D_CARD2_TEXT_BG,
                                textBoxSize=TEXT_SIZE,
                                textBackgroundcolor=TEXT_BACKGROUND_COLOR,
                                textBorderColor=BACKGROUND_BORDER_COLOR,
                                textBorderWidth=BORDER_WIDTH,
                                textRadius=TEXT_RADIUS,
                                img=im2,
                                imgPosition=D_IM2,
                                imgSize=SIZE,
                                imgBorderColor=BACKGROUND_BORDER_COLOR,
                                imgBorderWidth=BORDER_WIDTH,
                                imgRadius=RADIUS)

                    else:
                        makeCard(base, 
                            position=S_CARD,
                            size=CARD_SIZE,
                            radius=RADIUS,
                            backgroundColor=BACKGROUND_COLOR,
                            borderColor=BACKGROUND_BORDER_COLOR,
                            borderWidth=BORDER_WIDTH,
                            text=info,
                            textPosition=S_IMTEXT,
                            textStyles=infoStyles,
                            textBoxPosition=S_CARD_TEXT_BG,
                            textBoxSize=TEXT_SIZE,
                            textBackgroundcolor=TEXT_BACKGROUND_COLOR,
                            textBorderColor=BACKGROUND_BORDER_COLOR,
                            textBorderWidth=BORDER_WIDTH,
                            textRadius=TEXT_RADIUS,
                            img=im1,
                            imgPosition=S_IM,
                            imgSize=SIZE,
                            imgBorderColor=BACKGROUND_BORDER_COLOR,
                            imgBorderWidth=BORDER_WIDTH,
                            imgRadius=RADIUS)
                     
                    base.save(f"./static/imgs/slides/{position}/{day}{time}_{imgcounter}.png")
                    timeslot['imgs'].append(f"static/imgs/slides/{position}/{day}{time}_{imgcounter}.png")
                    imgcounter += 1

    return timeslot                    
    
    
def checkName(text, font_size, max_size, fontfile, spacing):
    font = ImageFont.truetype(fontfile, font_size)
    size = font.getsize_multiline(text, spacing=spacing)
    while size[0] > max_size[0] or size[1] > max_size[1]:
        font_size -= 1
        font = ImageFont.truetype(fontfile, font_size)
        size = font.getsize_multiline(text, spacing=spacing)
    return font

def makeCard(bgImg, position, size, radius, backgroundColor, borderColor, borderWidth, text=None, textPosition=None, textBoxPosition=None, textBoxSize=None, textRadius=None,textBackgroundcolor=None, textBorderColor=None, textBorderWidth=None, textStyles=None, img=None, imgPosition=None, imgSize=None, imgRadius=None, imgBorderColor=None, imgBorderWidth=None):
    cardRegion = [position, [sum(x) for x in zip(position, size)]]
    card = ImageDraw.Draw(bgImg)
    card.rounded_rectangle(cardRegion, radius=radius, fill=backgroundColor, outline=borderColor, width=borderWidth)
    if text is not None:
        assert textPosition is not None
        assert textStyles is not None
        if not any([textBoxPosition, textBoxSize, textBackgroundcolor, textBorderWidth, textBorderColor, textRadius]):
            card.text(textPosition, text, **textStyles)
        else:
            assert textBoxPosition is not None
            assert textBoxSize is not None
            assert textBackgroundcolor is not None
            assert textBorderColor is not None
            assert textBorderWidth is not None
            assert textRadius is not None
            textBoxRegion = [textBoxPosition, [sum(x) for x in zip(textBoxPosition, textBoxSize)]]
            card.rounded_rectangle(textBoxRegion, radius=textRadius, fill=textBackgroundcolor, outline=textBorderColor, width=textBorderWidth)
            card.text(textPosition, text, **textStyles)
    if img is not None:
        assert imgPosition is not None
        assert imgSize is not None
        assert imgPosition is not None
        assert imgBorderColor is not None
        assert imgBorderWidth is not None
        img = img.resize(imgSize)
        mask = Image.new("L", imgSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0,0), imgSize], radius=imgRadius, fill=255)
        img.putalpha(mask)
        draw2 = ImageDraw.Draw(img)
        draw2.rounded_rectangle([(0,0), imgSize], radius=imgRadius, fill=None, outline=imgBorderColor, width=imgBorderWidth)
        bgImg.paste(img, imgPosition, img)


def getWorkHoursString(startTime, endTime):
    shour, sminutes = map(int, startTime.split(":"))
    sAMPM = "AM"
    ehour, eminutes = map(int, endTime.split(":"))
    eAMPM = "AM"
    if ehour > 12:
        ehour = ehour%12
        eAMPM = "PM"
    if shour > 12:
        shour = shour%12
        sAMPM = "PM"
    eminutes += 30
    if eminutes == 60:
        eminutes = 0
        ehour += 1
    if ehour == 0:
        ehour = 12
    if shour == 0:
        shour == 12
    return f"{shour}:{sminutes:02}{sAMPM} - {ehour}:{eminutes:02}{eAMPM}"

def checkTimeslot(day, time, hostTimeslots):
    currentTime = getTimeInMinutesDB(time)
    for timeslot in hostTimeslots:
        startTime = getTimeInMinutesDB(timeslot['firstslot']['Time'])
        endTime = getTimeInMinutesDB(timeslot['lastslot']["Time"])
        if startTime <= currentTime and currentTime <= endTime:
            return timeslot
    return False

def getTimeInMinutesDB(timeString):
    hours, minutes = map(int, timeString.split(":"))
    return 60*hours + minutes

# if __name__=="__main__":
#     with open("timeslots.json") as fb:
#         timeslot = json.load(fb)
#     # timeslot = timeslotList[2]
#     # zakAndRaffiSlides(timeslot)
#     zakSlides(timeslot)
    