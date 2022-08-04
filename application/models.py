from datetime import datetime
from .extensions import db
from flask_login import UserMixin
from dataclasses import dataclass

user_timeslot = db.Table('user_timeslot',
    db.Column("user_id", db.Integer, db.ForeignKey('user.id'), ),
    db.Column("timeslot_id", db.Integer, db.ForeignKey('timeslot.id'), ))

@dataclass
class User(UserMixin, db.Model):
    id: int
    admin: bool
    firstName: str
    lastName: str
    position: str
    email: str
    pronouns: str
    physicsClass: str
    profilePic: bool

    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, nullable=False)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    position = db.Column(db.String(3))
    email = db.Column(db.String(109), unique=True, nullable=False)
    pronouns = db.Column(db.String(25))
    physicsClass = db.Column(db.String(6))
    profilePic = db.Column(db.Boolean, default=False)
    
@dataclass
class Timeslot(db.Model):
    id: int
    weekday: int
    startTime: datetime.time
    endTime: datetime.time
    users: list[User]

    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer, nullable=False)
    startTime = db.Column(db.Time)
    endTime = db.Column(db.Time)
    users = db.relationship("User", secondary=user_timeslot, backref=db.backref('timeslots', lazy="joined"), lazy='joined')

    def connected(self, other_timeslot):
        if self.weekday != other_timeslot.weekday:
            return False
        return (self.startTime == other_timeslot.endTime or self.endTime == other_timeslot.startTime)
          
    def __gt__(self, other_timeslot):
        return self.startTime > other_timeslot.startTime

    def __ge__(self, other_timeslot):
        return self.startTime >= other_timeslot.startTime

    def __lt__(self, other_timeslot):
        # print(f"Sorting: {self}.{self.startTime} < {other_timeslot}.{other_timeslot.startTime}: {self.startTime < other_timeslot.startTime}")
        return self.startTime < other_timeslot.startTime

    def __le__(self, other_timeslot):
        return self.startTime <= other_timeslot.startTime
    
    def __eq__(self, other_timeslot):
        return (self.weekday==other_timeslot.weekday and self.startTime==other_timeslot.startTime and self.endTime==other_timeslot.endTime)

    def __ne__(self, other_timeslot):
        return (self.weekday!=other_timeslot.weekday and self.startTime!=other_timeslot.startTime and self.endTime!=other_timeslot.endTime)
    
    def __str__(self):
        return f"Timeslot {self.id}"
    
