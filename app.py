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

@app.route("/", methods = ["GET"])
def home():
    return render_template("home.html")

@app.route('/dashboard/', methods=["GET"])
@login_required
def dashboard():
    return render_template('dashboard.html')