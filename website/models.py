#define waht database will look like, actual database elsewhere
from . import db #import db from __innit__.py from current folder
from flask_login import UserMixin #helps log users in
from sqlalchemy.sql import func

class Note(db.Model):
    
    id = db.Column(db.Integer, primary_key=True) #id is unique primary key to identify this note
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now()) #func automatically adds current date and time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #links user id with note id 

class User(db.Model, UserMixin): #only use UserMixin for users
    #define columns of user object (fields)
    id = db.Column(db.Integer, primary_key=True)#id is unique primary key to identify this user
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note') #basically store all users past notes into a 'list'