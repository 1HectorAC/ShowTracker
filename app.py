from flask import Flask,render_template, redirect, session
from functools import wraps
import os

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
    mondays = filter(lambda day: day['weekday'] == 'monday', showList)
    tuesdays = filter(lambda day: day['weekday'] == 'tuesday', showList)
    wednedays = filter(lambda day: day['weekday'] == 'wednesday', showList)
    thurdays = filter(lambda day: day['weekday'] == 'thursday', showList)
    fridays = filter(lambda day: day['weekday'] == 'friday', showList)
    saturdays = filter(lambda day: day['weekday'] == 'saturday', showList)
    sundays = filter(lambda day: day['weekday'] == 'sunday', showList)

    weekdayList = {'Monday': list(mondays),
                'Tuesday': list(tuesdays),
                'Wednesday': list(wednedays),
                'Thursday': list(thurdays),
                'Friday': list(fridays),
                'Saturday': list(saturdays),
                'Sunday': list(sundays),
     }

    return render_template('dashboard.html', shows = weekdayList)
    