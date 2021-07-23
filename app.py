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
from user.models import getShowsList, getShow, sortShowsByTime

@app.route("/", methods = ["GET"])
def home():
    return render_template("home.html")

@app.route('/dashboard/', methods=["GET"])
@login_required
def dashboard():
    # Get users show list.
    showList = getShowsList(session['user']['email'])

    # Sort show list by time.
    showList = sortShowsByTime(showList)

    # Organize list by weekday.
    mondays = []
    tuesdays = []
    wednesdays = []
    thursdays = []
    fridays = []
    saturdays = []
    sundays = []
    for show in showList:
        #Added encoded title.
        show['encodedTitle'] = urllib.parse.quote(show['title'], safe='')
        if(show['weekday'] == 'monday'):
            mondays.append(show)
        elif(show['weekday'] == 'tuesday'):
            tuesdays.append(show)
        elif(show['weekday'] == 'wednesday'):
            wednesdays.append(show)
        elif(show['weekday'] == 'thursday'):
            thursdays.append(show)
        elif(show['weekday'] == 'friday'):
            fridays.append(show)
        elif(show['weekday'] == 'saturday'):
            saturdays.append(show)
        else:
            sundays.append(show)

    weekdayList = {'Monday': mondays,
                'Tuesday': tuesdays,
                'Wednesday': wednesdays,
                'Thursday': thursdays,
                'Friday': fridays,
                'Saturday': saturdays,
                'Sunday': sundays,
     }

    data = {'week': weekdayList, 'count': len(showList)}

    return render_template('dashboard.html', shows = data)

@app.route('/profile/', methods=["GET"])
@login_required
def profile():
    return render_template('profile.html')

@app.route("/editShow/<string:title>")
@login_required
def editShow(title):
    usersShow = getShow(session['user']['email'], title)

    # Redirect if show doesn't exists.
    if(not usersShow):
        return redirect('/dashboard/')

    usersShow['encodedTitle'] = urllib.parse.quote(usersShow['title'], safe='')
    usersShow['weekday'] = str.capitalize(usersShow['weekday'])
    return render_template("editShow.html", show = usersShow)

