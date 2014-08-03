import os
from sha import sha
from base64 import b64encode
import json
from datetime import datetime

from flask import Flask, request, render_template, flash, redirect, url_for, g
from flask.ext.login import LoginManager, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from divideandconquer import app, db
from divideandconquer.models import User, Response
from divideandconquer.queuemanagement import q, refillQueue

def get_from_db(key):
    query = Response.query.filter_by(json_hash=key)
    try:
        query_response = query.first()
    except:
        print 'Error: key not found!' + str(key)
    try:
        print query_response.json
        response = json.loads(query_response.json)
    except:
        print 'Error: json invalid!' + str(response)
    return response


def update_spam_status(key, status):
    query = Response.query.filter_by(json_hash=key)
    try:
        query_response = query.first()
        query_response.is_spam = status
        db.session.add(query_response)
    except:
        print 'Error: key not found!' + str(key)
    db.session.commit()

@app.route('/logout')
@login_required
def logout():
    return login()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(request.form['username']).first()
        except:
            flash('User name not recognized. Maybe you need to register?')
            return redirect(url_for('login'))
        if user.password == sha(request.form['password'] + user.salt).digest():
            return redirect(url_for('classify'))
        else:
            flash('Nope, wrong password. Try again')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register' , methods=['GET','POST'])
def register():
    print 'registering'
    if request.method == 'GET':
        print 'got'
        return render_template('register.html')
    print 'post'
    try:
        user = User.query.filter_by(name=request.form['username']).first()
        if user:
            flash('That user name already exists. Try again')
            return render_template('register.html')
    except:
        pass
    salt = b64encode(os.urandom(15))
    user = User(name=request.form['username'] ,
        password=sha(request.form['password'] + salt).hexdigest(), salt=salt)
    db.session.add(user)
    try:
        db.session.commit()
    except:
        flash('Somebody probably has that username. Try again.')
        redirect('/register')
    flash('You are registered')
    print 'registered'
    return show_message()

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        if request.form.get('spam', None):
            update_spam_status(request.form['id'], 1)
        else:
            update_spam_status(request.form['id'], 0)
    return show_message()


def show_message():
    if q.empty():
        print 'refilling q'
        refillQueue()
        print 'q refilled'
    print 'show message'
    responseId = q.get()
    print 'got'
    response = get_from_db(responseId)
    print 'getting from db'
    return render_template('classify.html', description=response['description'],
        happy=response['happy'], id=responseId)


