from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import uuid
from mongoengine import connect, Document, StringField, ListField, DictField
import json
import os
import urllib.parse
import re
#from app import client

connect(db="test", host=os.getenv('DB_HOST'), port=27017)

# mongoEngine model for adding to db
class ShowUser(Document):
    _id = StringField(required=True)
    name = StringField(required=True, max_length=64)
    email = StringField(required=True, max_length=64)
    password = StringField(required=True)
    shows = ListField(DictField())

class User:

    def start_session(self, user):
        del user['password']
        del user['shows']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200
    
    def signup(self):

        # Create to user object
        user = ShowUser(
            _id = uuid.uuid4().hex,
            name = request.form.get('name'),
            email = request.form.get('email'),
            password = request.form.get('password'),
            shows = []
        )

        # Field validation.
        if(len(user.name) <= 0):
            return jsonify({"error": "Name field is empty."}), 400
        emailRegex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(not re.search(emailRegex,user.email)):   
            return jsonify({"error": "Email is not properly formated."}), 400
        if(len(user.password) <=3):
            return jsonify({"error": "Password needs to be greater than 3 characters"}), 400
        if(len(user.name) > 32 or len(user.password) > 32 or len(user.email) > 32):
            return jsonify({"error": "A field is too long"}), 400

        # Encrypt password
        user.password = pbkdf2_sha256.encrypt(user['password'])

        # Check for existing email address
        if ShowUser.objects(email=user['email']).count() != 0:
            return jsonify({"error": "Email address already in use"}), 400

        # Save user to db and start session. 
        # Note: passing python dict of user
        if user.save():
            return self.start_session(json.loads(user.to_json()))

        #print(user.to_json())

        return jsonify({"error": "Signup failed"}), 400

    def signout(self):
        session.clear()
        return redirect('/')

    def login(self):
        
        # Check if email match exists
        if ShowUser.objects(email=request.form.get('email')).count() != 0:
            user = json.loads(ShowUser.objects.get(email =request.form.get('email')).to_json())

            # Check if password match
            if pbkdf2_sha256.verify(request.form.get('password'), user['password']): 
                return self.start_session(user)

        # retur error
        return jsonify({"error": "Invalid login crdentials"}), 401

    # Add show to users shows list
    def addShow(self):
        # Check formating of all inputed fields.
        nameRegex = "^[a-zA-Z0-9\s\-\?\.!_']{1,40}$"
        timeRegex = "^([1-9]|10|11|12):[0-5][0-9] (am|pm)$"
        weekList = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if(not re.search(nameRegex,request.form.get('title'))):
            return jsonify({"error": "Title not properly formated. Accepted Special characters: - _ ? . ! '"}), 401
        if(not re.search(nameRegex,request.form.get('network'))):
                return jsonify({"error": "Network not properly formated. Can't use some special characters. Accepted Special characters: - _ ? . ! '"}), 401
        if(not re.search(timeRegex,request.form.get('time'))):
            return jsonify({"error": "Time not properly formated. E.g. X:XX am or X:XX pm"}), 401
        if(request.form.get('weekday') not in weekList):
            return jsonify({"error": "Error with weekday."}), 401

        userShows = getShowsList(session['user']['email'])

        #Check if reach number of shows limit.
        if(len(userShows) > 42):
            return jsonify({"error": "You reached the 42 show limit."}), 401

        # Check if title is already in users shows list.
        if not any(d.get('title') == request.form.get('title') for d in userShows):
            # create 'show' dictionary using form data.
            show = {
                "title" : request.form.get('title'),
                "network" : request.form.get('network'),
                "time" : request.form.get('time'),
                "weekday" : request.form.get('weekday')
            }
            
            # append show to users shows list.
            ShowUser.objects(email = session['user']['email']).update_one(push__shows=show)

            return jsonify({"success": "Sucess"}), 200
        return jsonify({"error": "Title of show already exits."}), 401

    # Clear all shows of the user.
    def clearShows(self):
        ShowUser.objects(email = session['user']['email']).update_one(set__shows=[])
        return redirect('/dashboard/')

    # Remove a show from users show list.
    def removeShow(self, title):
        ShowUser.objects(email = session['user']['email']).update_one(pull__shows__title=urllib.parse.unquote(title))
        return redirect('/dashboard/')
    
    # Edit a show in a users show list.
    def editShow(self,title):
        # Get old show that will be repaced.
        oldShow = getShow(session['user']['email'],title)
        # Create new show dictionary.
        newShow = {
            "title" : request.form.get('title'),
            "network" : request.form.get('network'),
            "time" : request.form.get('time'),
            "weekday" : request.form.get('weekday')
        }

        # Check if old show is the same as the new show and give error if so.
        if(oldShow['title'] == newShow['title'] and oldShow['network'] == newShow['network'] and oldShow['time'] == newShow['time'] and oldShow['weekday'] == newShow['weekday']):
            return jsonify({"error": "No changes made to this show."}), 401

        # Check formating of all inputed fields.
        nameRegex = "^[a-zA-Z0-9\s\-\?\.!_']{1,40}$"
        timeRegex = "^([1-9]|10|11|12):[0-5][0-9] (am|pm)$"
        weekList = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if(not re.search(nameRegex, newShow['title'])):
            return jsonify({"error": "Title not properly formated. Accepted Special characters: - _ ? . ! '"}), 401
        if(not re.search(nameRegex, newShow['network'])):
                return jsonify({"error": "Network not properly formated. Can't use some special characters. Accepted Special characters: - _ ? . ! '"}), 401
        if(not re.search(timeRegex, newShow['time'])):
            return jsonify({"error": "Time not properly formated. E.g. X:XX am or X:XX pm"}), 401
        if(newShow['weekday'] not in weekList):
            return jsonify({"error": "Error with weekday."}), 401
        
        # Check if the title changed. If so then check if the new title already exits and give error if so.
        if (oldShow['title'] != newShow['title']):
            userShows = getShowsList(session['user']['email'])
            sameTitleList = list(filter(lambda day: day['title'] == newShow['title'], userShows))
            if (len(sameTitleList) != 0):
                return jsonify({"error" : "Title already exits. Can't have two shows with the same title."}), 401
        
        # Remove old show from users show list.
        ShowUser.objects(email = session['user']['email']).update_one(pull__shows=oldShow)
        
        # Add new show to users show list.
        ShowUser.objects(email = session['user']['email']).update_one(push__shows=newShow)

        return jsonify({"success": "Sucess"}), 200

# Get list of shows by user using their email.
def getShowsList(userEmail):
    user = json.loads(ShowUser.objects.get(email = userEmail).to_json())
    userList = user['shows']
    return userList

# Get show by title and users email.
def getShow(userEmail, title):
    user = json.loads(ShowUser.objects.get(email = userEmail).to_json())
    userList = user['shows']
    show = list(filter(lambda s: s['title'] == urllib.parse.unquote(title), userList))
    
    # Check if there are any shows
    if(len(show) != 0):
        return show[0]
    return 0

# Input a list of show dictionaries and it will sort them by 'time.'
def sortShowsByTime(showList):
    # Split into 'am' and 'pm' list.
    amList = list(filter(lambda day: day['time'][-2:] == 'am', showList ))
    pmList = list(filter(lambda day: day['time'][-2:] == 'pm', showList ))

    # Sort 'am' and 'pm' list. Will sort most of it but issue with single digit, double digit, and 12th hours remain.
    amList = sorted(amList, key = lambda ele: ele['time'])
    pmList = sorted(pmList, key = lambda ele: ele['time'])

    # Correct placment of single digit, double digit, and 12th hour.
    amList = sortByTimeHelper(amList)
    pmList = sortByTimeHelper(pmList)

    return amList + pmList

# Helps put single digit, double digit, and 12th hour in right placement.
def sortByTimeHelper(l):
    singleDigitHours = []
    doubleDigitHours = []
    hour12 = []
    for x in l:
        # Filter 12th hour
        if(x['time'][:2] == '12'):
            hour12.append(x)
        # Filter single digit hour
        elif(len(x['time']) == 7):
            singleDigitHours.append(x)
        # Filter double digit hour
        else:
            doubleDigitHours.append(x)
    return hour12 + singleDigitHours + doubleDigitHours