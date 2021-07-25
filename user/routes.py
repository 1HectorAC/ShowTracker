# Routes related to user.
from flask import Flask
from app import app
from user.models import User

@app.route("/user/signup", methods=["POST"])
def signup():
    return User().signup()

@app.route("/user/signout")
def signout():
    return User().signout()

@app.route("/user/login", methods=["POST"])
def login():
    return User().login()

@app.route("/user/editName", methods=["POST"])
def editName():
    return User().editName()

@app.route("/user/addShow", methods=["POST"])
def addShow():
    return User().addShow()

@app.route("/user/clearShows")
def clearShows():
    return User().clearShows()

@app.route("/user/removeShow/<string:title>")
def removeShow(title:str):
    return User.removeShow(User, title)

@app.route("/user/editShow/<string:title>", methods=["POST"])
def editAShow(title:str):
    return User().editShow(title)