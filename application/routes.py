from calendar import weekday
import email
from time import time
from flask import Blueprint, render_template, session, redirect, url_for, abort, flash, request, current_app, jsonify, Markup
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import values
from .extensions import db, oauth, login_manager
from .models import User, Timeslot, user_timeslot
from .forms import FirstAdminForm, ProfileForm, AdminProfileForm, UserBatchUploadForm, TimeSlotUploadForm
from .image import shrinkImage, cropImage
import datetime

from functools import wraps
import os


main = Blueprint("main", __name__)
login_manager.login_view = "main.index"
login_manager.login_message = ("Login expired. Please login again.")
login_manager.refresh_view = "main.index"
login_manager.needs_refresh_message = ("Login expired. Please login again.")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.admin:
            return f(*args, **kwargs)
        flash("You must be an administrator to access this page")
        return redirect(request.referrer or url_for('main.index'))
    
    return wrapper

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def makeCalendarEventsList(timeslots, initial_user=None):
    events = []
    startingHour = datetime.time(23,59)
    endingHour = datetime.time(0,0)
    print("LENGTHS")
    print(len(timeslots))
    for ts in timeslots:
        if ts.startTime < startingHour:
            startingHour = ts.startTime
        if ts.endTime > endingHour:
            endingHour = ts.endTime
        # Updating the weekday value of sunday so its -1. That way when adding
        # to the date of calendar it goes in the right spot of March 20,2022.
        # This is due to showing calendar starting on sunday, but python
        # using monday as day 0.
        if ts.weekday == 6:
            day = -1
        else:
            day = ts.weekday
        
        if initial_user is None:
            for user in ts.users:
                # If a user is not a TA or LA the shouldn't be assigned
                # so they get thrown into the "Other" calendar that will
                # be red to highlight the mistake.
                print(ts.id)
                print(f"\r\nUSER:{user.firstName}")
                if user.position not in ["LA", "TA"]:
                    calendarId = "Othercal"
                else:
                    calendarId = f"{user.position}cal"
                # Add all the events to the calendar to be displayed.
                event = {
                    "start": f"2022-03-{21+day}T{ts.startTime}",
                    "end": f"2022-03-{21+day}T{ts.endTime}",
                    "id": f"Event{len(events)+1}",
                    "calendarId": calendarId,
                    "title": f"{user.firstName[0]}{user.lastName[0]}",
                    "body": f"{user.firstName} {user.lastName}<br>{user.email}<br>{user.position} - {user.physicsClass}"
                }
                events.append(event)
        else:
            # If a user is not a TA or LA the shouldn't be assigned
            # so they get thrown into the "Other" calendar that will
            # be red to highlight the mistake.
            if initial_user.position not in ["LA", "TA"]:
                calendarId = "Othercal"
            else:
                calendarId = f"{initial_user.position}cal"
            # Add all the events to the calendar to be displayed.
            event = {
                "start": f"2022-03-{21+day}T{ts.startTime}",
                "end": f"2022-03-{21+day}T{ts.endTime}",
                "id": f"Event{len(events)+1}",
                "calendarId": calendarId,
                "title": f"{initial_user.firstName[0]}{initial_user.lastName[0]}",
                "body": f"{initial_user.firstName} {initial_user.lastName}<br>{initial_user.email}<br>{initial_user.position} - {initial_user.physicsClass}"
            }
            events.append(event)
    return (events, startingHour.hour, endingHour.hour)

@main.app_template_filter("ftime")
def formatTime(time):
    return time.strftime("%-I:%M")

@main.route("/")
def index():
    userCount = User.query.filter_by(admin=True).first()
    if userCount is None:
        form = FirstAdminForm()
        return render_template("firstAdmin.html", form=form)
    return render_template("index.html")

@main.post("/firstAdmin")
def firstAdmin():
    form = FirstAdminForm()
    if form.validate_on_submit():
        firstUser = User(email=form.email.data, admin=True)
        db.session.add(firstUser)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("firstAdmin.html", form=form)

@main.route("/addUsers",  methods=['GET', 'POST'])
@login_required
@admin_required
def addUsers():
    form = UserBatchUploadForm()
    if request.method == "GET":
        return render_template("uploadUsers.html", form=form)
    elif request.method == "POST":
        # if form.validate_on_submit():
        #     print("VALID")
        users = []
        contents = form.csvFile.data.stream.read()
        contents = contents.decode()
        contents = contents.split("\r\n")
        headers = contents[0].split(",")
        headerLocations = {colName:headers.index(colName) for colName in headers}
        translation = {
            "email": "Email",
            "firstName": "First Name",
            "lastName" : "Last Name",
            "pronouns" : "Pronouns",
            "physicsClass": "Class",
            "position" : "Position"
        }
        for host in contents[1:]:
            temp = {
                "email": None,
                "firstName": None,
                "lastName": None,
                "pronouns": None,
                "physicsClass": None,
                "position": None
            }
            info = host.split(",")
            if len(host) <=1:
                continue
            for key in temp:
                temp[key] = info[headerLocations[translation[key]]]
            user = User.query.filter_by(email=temp["email"]).first()
            if user:
                for att, value in temp.items():
                    setattr(user, att, value)
            else:
                user = User(admin=False, **temp)
                db.session.add(user)
            users.append(user)
            db.session.commit()
        return redirect(url_for("main.users", users=users, review=True))

@main.route("/users")
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template("users.html", users=users, review=False)

@main.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def user(user_id):
    form = AdminProfileForm()
    user = User.query.get(user_id)
    events, startingHour, endingHour = makeCalendarEventsList(user.timeslots, user)
    if request.method == "GET":
        return render_template("adminProfile.html", form=form, user=user, startingHour=startingHour, endingHour=endingHour+1, eventslist=events)
    elif request.method == "POST":
        for att, value in form.data.items():
            if value is not None and att!="csrf_token" and att != "profilePic":
                setattr(user, att, value)
        db.session.commit()
        if form.profilePic.data is not None:
            tmp_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "tmp", user.email+".png")
            shrinkImage(form.profilePic.data, tmp_path)
            final_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "users", user.email+".png")  
            faces = cropImage(tmp_path, final_path, current_app.config["PROFILE_SIZE"])
            if faces==1:
                os.remove(tmp_path)
                user.profilePic = True
                db.session.commit()
            elif faces==0:
                flash("No faces found in this image!")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
            else:
                flash("Multiple faces found in this image!")
                flash("Your image must be a headshot of JUST you.")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
        if form.data["action"] == "admin":
            user.admin = True
            db.session.commit()
        elif form.data["action"] == "delete":
            db.session.delete(user)
            db.session.commit()
            
            return redirect(url_for("main.users"))
        elif form.data["action"] == "remove-admin":
            admins = User.query.filter_by(admin=True).all()
            if len(admins) <= 2:
                user.admin = False
                db.session.commit()
            else:
                print("Flashing Message")
                flash("This is the last admin!") 
                flash("Promote someone else to admin before removing this one.")
            redirect(url_for("main.adminProfile", user=user, form=form))
        return redirect(url_for("main.adminProfile", user=user, form=form, startingHour=startingHour, endingHour=endingHour+1, eventslist=events))
    
@main.route("/uploadTimeslots", methods=["GET", "POST"])
@login_required
@admin_required
def uploadTimeslots():
    form = TimeSlotUploadForm()
    if request.method == "GET":
        return render_template("uploadTimeslot.html", form=form)
    elif request.method == "POST":
        # Start by deleting the columns in the intermediate table
        # user_table, since those don't get deleted on their own.
        d = user_timeslot.delete()
        db.session.execute(d)
        # Also delete all the timeslots.
        Timeslot.query.delete()
        # Commit all the changes.
        db.session.commit()
        # Parse the CSV file in a stupid way.
        contents = form.csvFile.data.stream.read()
        contents = contents.decode()
        contents = contents.split("\r\n")
        # Make a translator dict for how python saves
        # weekdays.
        days = {
            "monday":0,
            "tuesday":1,
            "wednesday":2,
            "thursday":3,
            "friday":4,
            "saturday": 5,
            "sunday":6
        }
        # Create a bunch of lists to store errors
        badEmails = []
        noUsers = []
        badDays = []
        badTimes = []
        # Create a list of events to add to the calendar that will
        # be displayed.
        events = []

        # Each row of the spreadsheet should niavely be a timeslot. We will
        # start by making a timeslot in the db for each row.
        for row in contents[1:]:
            row = row.split(",")
            # Start the error checking looking for bad spelling of different days
            # i.e. wesnday would be added here. And then we would continue to the 
            # next line of the CSV file.
            try:
                day = days[row[0].lower()]
            except KeyError:
                if row[0] not in badDays:
                    badDays.append(row[0])
                continue
            # Try to turn the start and end times into times. Continue onto the 
            # next row in the CSV if there is a issue.
            try:
                startTime = datetime.time(*[int(time) for time in row[1].split(":")])
            except:
                if row[1] not in badTimes:
                    badTimes.append(row[1])
                continue
            try:
                endTime = datetime.time(*[int(time) for time in row[2].split(":")])
            except:
                if row[2] not in badTimes:
                    badTimes.append(row[2])
                continue
            # Make the new timeslot.
            timeslot = Timeslot(weekday=day, startTime=startTime, endTime=endTime)
            db.session.add(timeslot)
            db.session.commit()

            # Loop through all of the users listed in the row of the CSV file
            # and make sure that they are @ucsb.edu emails and that they
            # are actually a user in the system. If either one is not true
            # add them to an errors list to show the user.
            # Otherwise, we add the user to the timeslot
            for userEmail in row[3:]:
                if userEmail == "":
                    continue
                if "@ucsb.edu" not in userEmail:
                    if userEmail not in badEmails:
                        badEmails.append(userEmail)
                    continue
                user = User.query.filter_by(email=userEmail).first()
                if user is None:
                    if userEmail not in noUsers:
                        noUsers.append(userEmail)
                    continue
                
                timeslot.users.append(user)
                db.session.commit()
        # Now that we have niavely made all of the timeslots we want
        # to clean up the data a bit. Where ever we have two or more
        # consecutive (in time) timeslots with the same users we want
        # to reduce that into one timeslot.
        # To do this, we first loop through all of the users and check 
        # if any of the timeslots they are associated with are consecutive 
        # (connected)
        for user in User.query.all():
            #If user has no timeslots move on.
            if user.timeslots is None:
                continue
            connectedTimeslots = []
            checked = []

            # Loop through the users timeslots
            for i, ts in enumerate(user.timeslots):
                connected = []
                # Look at all of the other timeslots and see if any
                # are connected. If so, add all connected timeslots
                # to the connected list. Additionally, we will add 
                # the ts to the checked list, so we don't check what
                # it is connected to multiple times.
                if i < len(user.timeslots) and ts not in checked:
                    checked.append(ts)
                    connected.append(ts)
                    # Looking at all other ts
                    for other_ts in user.timeslots[i+1:]:
                        if ts.connected(other_ts):
                            connected.append(other_ts)
                            checked.append(other_ts)
                    # If the connected list is > 1 then we know we
                    # have at least 2 timeslots to connect together
                    # so we sort them and add them to the connectedTimeslots
                    # list, which is a list of connected timeslots.
                    if len(connected) > 1:
                        sortedConnected = sorted(connected)
                        connectedTimeslots.append(sortedConnected)
                    # We do this until we run out of timeslots to check.
            
            # Now we loop through all the connected timeslots we made. Since
            # they are sorted, we know that the new timeslot will have a startTime
            # of the first timeslot in the connected list, and the endTime of the
            # last timeslot in the connected list. We then search for a timeslot
            # that we already made on a previous itteration of the loop. If it
            # exists, we will check if the user is already in the timeslot.
            # If it doesn't exist then we will make a new timeslot and add
            # our user to it.
            # Finally, we will loop through all of the timeslots in the connected
            # list and remove the user from each of this. If there are no more
            # users associated with a timeslot we will delete it.
            for tss in connectedTimeslots:
                # Get parameters for new timeslot
                startTime = tss[0].startTime
                endTime = tss[-1].endTime
                weekday = tss[0].weekday
                # Check if timeslot exists already
                ts = Timeslot.query.filter_by(weekday=weekday, startTime=startTime, endTime=endTime).first()
                if ts is not None and user not in ts.users:
                    ts.users.append(user)
                    db.session.commit()
                # If not make a new one add the user.
                else:
                    ts = Timeslot(weekday=weekday, startTime=startTime, endTime=endTime)
                    db.session.add(ts)
                    db.session.commit()
                    ts.users.append(user)
                    db.session.commit()
                # Go back through the timeslots in the current connected list
                # and remove the user, deleting useless timeslots along the way.
                for ts in tss:
                    if len(ts.users) == 0:
                        db.session.delete(ts)
                        db.session.commit()
                    else:
                        ts.users.remove(user)
                        db.session.commit()

        timeslots = Timeslot.query.all()
        events, startingHour, endingHour = makeCalendarEventsList(timeslots)
            
        # IF we ran into any errors processing the data, send the feedback to the user.
        if len(badEmails)+len(noUsers)+len(badDays)+len(badTimes) != 0:
            flash("Something(s) went wrong. The timeslots you made won't be complete!")
        for email in badEmails:
            flash(f"{email} invalid. Must contain @ucsb.edu")
        for email in noUsers:
            flash(f"No user with email {email}")
        for day in badDays:
            flash(f"Sorry, I don't understand the day: {day}")
        for time in badTimes:
            flash(f"Sorry, I don't understand the time: {time}")
        
        return redirect(url_for("main.schedule", eventsList=events, startingHour=startingHour, endingHour=endingHour+1), code=307)

@main.get("/manuallyAddHostsImages")
def get_manually_add_host_image():
    return render_template("manualUploadUsersImages.html")

@main.post("/manuallyAddHostsImages")
def post_manually_add_host_image():
    #TODO: Fill out Post Method for Manually Adding a host image
    pass

@main.get("/makeSlideshows")
def get_make_slideshow():
    return render_template("makeSlideshows.html")

@main.post("/makeSlideshows")
def post_make_slideshow():
    #TODO: Potentially make slideshow making function
    pass

# @main.get("/addSlides")
# def get_add_slides():
#     #return render_template()
#     #TODO: make Template and make it functional
#     pass


@main.route('/authorized')
def authorized():
    # google = oauth.create_client('google')  # create the google oauth client
    token = oauth.google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = oauth.google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    local_user = User.query.filter_by(email=user['email']).first()
    if not local_user:
        return abort(401)
    # session['profile'] = user
    # session.permanent = True
    login_user(local_user)
    if local_user.admin:
        return redirect('/adminProfile')
    return redirect('/profile')

@main.route("/login")
def login():
    # google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('main.authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# @main.route("/user/<email>")
# def createUser(email):
#     newUser = User(email=f"{email}@ucsb.edu")
#     db.session.add(newUser)
#     db.session.commit()
#     return redirect("/")

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if request.method == "GET":
        events, startingHour, endingHour = makeCalendarEventsList(current_user.timeslots, current_user)
        return render_template("profile.html", user=current_user, form=form, eventslist=events, startingHour=startingHour, endingHour=endingHour+1)
    elif request.method == "POST":
        user = User.query.filter_by(email=current_user.email).first()
        for att, value in form.data.items():
            if value is not None and att!="csrf_token" and att != "profilePic":
                setattr(user, att, value)
        db.session.commit()
        if form.profilePic.data is not None:
            tmp_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "tmp", user.email+".png")
            shrinkImage(form.profilePic.data, tmp_path)
            final_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "users", user.email+".png")  
            faces = cropImage(tmp_path, final_path, current_app.config["PROFILE_SIZE"])
            if faces==1:
                os.remove(tmp_path)
                user.profilePic = True
                db.session.commit()
            elif faces==0:
                flash("No faces found in this image!")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
            else:
                flash("Multiple faces found in this image!")
                flash("Your image must be a headshot of JUST you.")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
        return redirect(url_for("main.profile", user=user, form=form))

@main.route("/adminProfile", methods=["GET", "POST"])
@login_required
@admin_required
def adminProfile():
    form = AdminProfileForm()
    if request.method == "GET":
        return render_template("adminProfile.html", user=current_user, form=form)
    elif request.method == "POST":
        user = User.query.filter_by(email=current_user.email).first()
        for att, value in form.data.items():
            if value is not None and att!="csrf_token" and att != "profilePic":
                setattr(user, att, value)
                db.session.commit()
        if form.profilePic.data is not None:
            tmp_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "tmp", user.email+".png")
            shrinkImage(form.profilePic.data, tmp_path)
            final_path = os.path.join(current_app.instance_path, "..", "application","static","imgs", "users", user.email+".png")  
            faces = cropImage(tmp_path, final_path, current_app.config["PROFILE_SIZE"])
            if faces==1:
                os.remove(tmp_path)
                user.profilePic = True
                db.session.commit()
            elif faces==0:
                flash("No faces found in this image!")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
            else:
                flash("Multiple faces found in this image!")
                flash("Your image must be a headshot of JUST you.")
                flash("If this is in error please contact the PSR Coordinator for help or try a different image.")
        
        if form.data["action"] == "remove-admin":
            admins = User.query.filter_by(admin=True).all()
            if len(admins) >= 2:
                user.admin = False
                db.session.commit()
            else:
                flash("This is the last admin!") 
                flash("Promote someone else to admin before removing this one.")
        return redirect(url_for("main.adminProfile", user=user, form=form))

@main.route("/play/<day>/<current_time>")
def getUsersInTimeslot(day, current_time):
    current_time = datetime.time.fromisoformat(current_time)
    day = int(day)
    timeslots = Timeslot.query.filter_by(weekday=day).filter(Timeslot.startTime <= current_time).filter(Timeslot.endTime >= current_time).all()
    users = []
    for timeslot in timeslots:
        startTime = timeslot.startTime
        endTime = timeslot.endTime
        for user in timeslot.users:
            data = {
                "user": user,
                "startTime": str(startTime),
                "endTime" : str(endTime)
            }
            users.append(data)
    return jsonify(users)

@main.route("/play")
def play():
    return render_template("play.html")

@main.route("/userTable")
@login_required
@admin_required
def tables():
    users = User.query.all()
    # s = user_timeslot.select()
    # result = db.session.execute(s)
    return render_template("tables.html", users=users)


@main.route("/schedule")
def schedule():
    timeslots = Timeslot.query.all()
    events, startingHour, endingHour = makeCalendarEventsList(timeslots)
    return render_template("schedule.html", eventsList=events, startingHour=startingHour-1, endingHour=endingHour+1)