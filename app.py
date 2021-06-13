from flask import Flask,render_template, redirect, session
from functools import wraps
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Decorators. (function will be passed in function (dashboard_render), decide if go though or not)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs) #return orginial function trying to access
        else:
            return redirect('/') #redirect to home page
    return wrap

#Routes
from user import routes
from user.models import getShowsList

@app.route("/", methods = ["GET"])
def home():
    return render_template("home.html")

@app.route('/dashboard/', methods=["GET"])
@login_required
def dashboard():
    # Get shows list of user for display.
    showList = getShowsList(session['user']['email'])

    # Organize list by weekdays.
    mondays = list(filter(lambda day: day['weekday'] == 'monday', showList))
    tuesdays = list(filter(lambda day: day['weekday'] == 'tuesday', showList))
    wednesdays = list(filter(lambda day: day['weekday'] == 'wednesday', showList))
    thurdays = list(filter(lambda day: day['weekday'] == 'thursday', showList))
    fridays = list(filter(lambda day: day['weekday'] == 'friday', showList))
    saturdays = list(filter(lambda day: day['weekday'] == 'saturday', showList))
    sundays = list(filter(lambda day: day['weekday'] == 'sunday', showList))

    # Added encoding of title. Need for url setup on webpage.
    for x in mondays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in tuesdays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in wednesdays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in thurdays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in fridays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in saturdays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    for x in sundays:
        x['encodedTitle'] = urllib.parse.quote(x['title'], safe='')
    
    weekdayList = {'Monday': mondays,
                'Tuesday': tuesdays,
                'Wednesday': wednesdays,
                'Thursday': thurdays,
                'Friday': fridays,
                'Saturday': saturdays,
                'Sunday': sundays,
     }

    return render_template('dashboard.html', shows = weekdayList)
