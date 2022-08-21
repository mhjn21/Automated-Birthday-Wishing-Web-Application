from app import db
import time
import uuid
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(500), primary_key = True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    dob = db.Column(db.Date)
    email = db.Column(db.String(255))
    message = db.Column(db.String(1000),default="Happy birthday! I hope all your birthday wishes and dreams come true")
    userSignIn = db.Column(db.String(255))
    userSignInName = db.Column(db.String(255))

    def __init__(self, name, email,phone,dob,userSignIn,userSignInName,message="Happy Birthday!!! I hope all your birthday wishes and dreams come true"):
        self.id = round(time.time() * 1000)
        self.name = name
        self.email = email
        self.phone = phone
        self.dob = dob
        self.message = message
        self.userSignIn = userSignIn
        self.userSignInName = userSignInName

    def __repr__(self):
        print(self.id)
        print(self.name)
        print(self.email)
        print(self.phone)
        print(self.dob)
        print(self.message)
        print(self.userSignIn)
        print(self.userSignInName)
        return '<User %r>' % self.name

