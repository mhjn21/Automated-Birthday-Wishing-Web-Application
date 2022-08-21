from flask.globals import session
from requests_oauthlib.oauth2_session import TokenUpdated
from werkzeug.datastructures import _CacheControl, Authorization
import models
from flask import Flask, render_template, url_for, request, redirect, jsonify, session, abort
from flask.ctx import AppContext
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime
import fetchContact
import os
import pathlib
from pip._vendor import cachecontrol
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token


# Initialising Flask
app = Flask(__name__)

# #DB Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)
db.create_all()

mail = Mail(app)

# Mailer Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'birthdaywishingbot@gmail.com'
app.config['MAIL_PASSWORD'] = 'approject2021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Authentication
app.secret_key = "AP_Project123"
GOOGLE_CLIENT_ID = "1081305119880-po3v5oon3acud2211pkrrmkrs74t2ftb.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "keys4.json")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback")


def login_is_required(function):
    def wrapper(*args, **kwargs):
        wrapper.__name__ = function.__name__
        if "google_id" not in session:
            return abort(401)  # Authoriztion Required
        else:
            return function()
    return wrapper


@app.route("/login", endpoint='login')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print("Login")
    print("state ",state)
    print("Session",session)
    return redirect(authorization_url)  # Opening google login page

@app.route("/callback", endpoint='callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State doesnot match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    print("Printing Session Info:")
    print(session["google_id"])
    print(session["name"])
    print(id_info)
    return redirect("http://127.0.0.1:5000/app")


@app.route("/logout", endpoint='logout')
def logout():
    session.clear()
    # Redirect to home page
    return redirect("http://127.0.0.1:5000/")
    

# Home Page
@app.route('/', endpoint='home')
def home():
    return render_template("signin.html")

# Home page route
@app.route('/app')
@login_is_required
def index():
    # Fetch all users
    # users = models.User.query.all()
    users = db.session.execute("SELECT * FROM users where userSignIn=:param",{"param":session['email']})
    return render_template("index.html", users=users)


# Form Submission
@app.route('/app', endpoint='test', methods=['POST'])
@login_is_required
def test():
    print("Session ",session)
    if request.method == 'POST':
        print(request.form)
        userName = request.form['name']
        userPhone = request.form['phone']
        userEmail = request.form['email']
        userDob = request.form['dob']
        userMessage = request.form['message']
        userSignIn = session['email']
        userSignInName = session['name'] 

        if(userMessage == ""):
            userMessage = "Happy birthday! I hope all your birthday wishes and dreams come true."
        format = '%Y-%m-%d'
        date = datetime.datetime.strptime(userDob, format)
        print("date : ", date)
        print(userName, userPhone, userEmail, date, userMessage,userSignIn, sep=" ")
        newUser = models.User(name=userName, email=userEmail,
                              phone=userPhone, dob=date, message=userMessage,userSignIn=userSignIn,userSignInName=userSignInName)
        print("new User : ", newUser)
        try:
            print(db)
            print(newUser)
            db.session.add(newUser)  # Storing
            db.session.commit()
            print("User added to DB")
            return render_template('thankyoupage.html', success=True)
        except Exception as e:
            print(repr(e))
            return render_template("thankyoupage.html", success=False)

    else:
        return jsonify({"Response": "Get Request Called"})


# Automated B'day Wisher function
@app.route('/sendbdaywish', endpoint='sendBdayWish', methods=['GET'])
# @login_is_required
def sendBdayWish():

    # Fetch all users details
    users = models.User.query.all()
    print(users)
    for user in users:
        print("Birthday ", user.dob)
        print("Today's Date", datetime.date.today())
        if(datetime.date.today().day == user.dob.day and datetime.date.today().month == user.dob.month):
            print("Sending to :" ,user.name)
            sendEmail(user)
            sendSMS(user)
    return "success"


#delete
@app.route('/delete/<id>')
def deleteUser(id):
    # delete function
    print("User ID to be deleted ",id)
    db.session.execute("DELETE from users where id=:param",{"param":id})
    db.session.commit()
    return redirect("http://127.0.0.1:5000/app")

#import
@app.route('/import')
def importUser():
    return "Import User"

# SMS sending route
# @app.route('/sendsms',methods=['POST','GET'])
def sendSMS(user):
    with app.app_context():
        try:
            print("Sending SMS")
            url = "https://www.fast2sms.com/dev/bulkV2"
            number = user.phone
            message = user.message + "\n-"+user.userSignInName
            querystring = {"authorization": "YyvBSlen5O2ALDk4IQUVzsXHCqMRK7i9aNJwp0x3ud1G6fjTbchiQXjoG2RWI8mTJKODE4cA7baFtx9M",
                           "message": message, "language": "english", "route": "q", "numbers": number}
            headers = {
                'cache-control': "no-cache"
            }

            resp = requests.request(
                "GET", url, headers=headers, params=querystring)

            print(resp.text)

            return jsonify({"response": resp.text})
        except Exception as e:
            print(repr(e))
            return jsonify({"response": "Something went wrong"})


# Email sending route
# @app.route('/sendemail',methods=['POST','GET'])
def sendEmail(user):
    with app.app_context():
        try:
            print("Sending Email")
            msg = Message(
                'Birthday Wish :)',
                sender='birthdaywishingbot@gmail.com',
                recipients=[user.email]
            )
            msg.body = user.message+"\n\n From "+user.userSignInName
            mail.send(msg)
            print("Email sent")
            return jsonify({"response": "Mail sent"})
        except Exception as e:
            print(repr(e))
            return jsonify({"response": "Something went wrong"})


# Importing Contacts using google account
@app.route('/importcontacts', endpoint='importContact', methods=['GET'])
@login_is_required
def importContact():    
    with app.app_context():
        try:
            persons = fetchContact.importContacts()

            # Adding people with email or phone or both to db
            userMessage = "Happy birthday! I hope all your birthday wishes and dreams come true" 
            for i in range(len(persons)):
                print(i)
                # Parsing Date
                try:
                    userDOB = "2000"+"-"+str(persons[i]["birthdays"][0]["date"]["month"]) +"-"+str(persons[i]["birthdays"][0]["date"]["day"]) 
                    format = '%Y-%m-%d'
                    dob = datetime.datetime.strptime(userDOB, format)
                except Exception as e:
                    print(e)
                    print("index ",i," error in dob")
                    continue

                # Parsing Email
                try:
                    userEmail = persons[i]["emailAddresses"][0]["value"]
                except:
                    print("index ",i," error in dob")
                    continue

                #parsing Name
                try:
                    userName = persons[i]["names"][0]["displayName"]
                except:
                    print("index ",i," error in dob")
                    continue

                #parsing Mobile (an optional parameter)
                try:
                    print(persons[i]["phoneNumbers"][0]["canonicalForm"][3:13])
                    userMobile = persons[i]["phoneNumbers"][0]["canonicalForm"][3:13]
                except:
                    print("index ",i," error in dob")
                    userMobile = ""

                newUser = models.User(name=userName, email=userEmail,phone=userMobile, dob=dob, message=userMessage,userSignIn=session['email'],userSignInName=session['name'])
                print("new User : ", newUser)
                try:
                    print("We are here")
                    users = db.session.execute("SELECT email FROM users where email=:param",{"param":userEmail})
                    flag = 0
                    for user in users:
                         flag = 1
                         break
                    if flag == 0:
                        db.session.add(newUser)  # Storing
                        db.session.commit()
                        print("User added to DB")
                    # return render_template('thankyoupage.html', success=True)
                except Exception as e:
                    print(repr(e))
                    continue

            return redirect("http://127.0.0.1:5000/app")
        except Exception as e:
            print(repr(e))
            return jsonify({"response": "Something went wrong"})


if __name__ == "__main__":
    print("running")
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(
        sendBdayWish, 'cron', day_of_week='mon-sun', hour=10, minute=16, second=10)
    scheduler.start()
    # app.run(debug=True)
    app.run(use_reloader=False)
