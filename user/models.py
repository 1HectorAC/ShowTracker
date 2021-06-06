from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import uuid
from mongoengine import connect, Document, StringField, ListField, DictField
import json
import os
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

        # Encrypt password
        user.password = pbkdf2_sha256.encrypt(user['password'])

        # Check for existing email address
        if ShowUser.objects(email=user['email']).count() != 0:
            return jsonify({"error": "Email address alread in use"}), 400

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

# Get list of shows by user using their email.
def getShowsList(userEmail):
    user = json.loads(ShowUser.objects.get(email = userEmail).to_json())
    userList = user['shows']
    return userList
    