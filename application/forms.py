from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import InputRequired, Email

from flask_uploads import UploadSet, IMAGES

images = UploadSet('images', IMAGES)
csv = UploadSet("csv", ["csv"])

class FirstAdminForm(FlaskForm):
    email = StringField("email", validators=[InputRequired("Must fillout @ucsb.edu email."), Email()])

class ProfileForm(FlaskForm):
    firstName = StringField("firstName")
    lastName = StringField("lastName")
    pronouns = StringField("pronouns")
    profilePic = FileField("profilePic", validators=[FileAllowed(images, "Images only")])

class AdminProfileForm(ProfileForm):
    position = SelectField("position", choices=[("LA", "LA"), ("TA","TA"), ("ILG", "ILG"), ("SA", "SA"), ("FA", "FA")])
    physicsClass = StringField("physicsClass")
    action = HiddenField("action")

class UserBatchUploadForm(FlaskForm):
    csvFile = FileField("csvFile", validators=[FileRequired("Must have a file"), FileAllowed(csv, "CSV Files Only")])

class TimeSlotUploadForm(FlaskForm):
    csvFile = FileField("csvFile", validators=[FileRequired("Must have a file"), FileAllowed(csv, "CSV Files Only")])


