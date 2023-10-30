# User routes #

from flask import Flask
from webapp import app
from user.models import User

@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

@app.route('/user/signout', methods=['GET','DELETE'])
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()

@app.route('/user/profile', methods=['POST'])
def manage_profile():
    return User().manage_profile()

