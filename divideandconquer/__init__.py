import os
from sha import sha
import json
from datetime import datetime

from flask import Flask, request, render_template, flash, redirect, url_for, g
from flask.ext.login import LoginManager, login_required
from flask.ext.sqlalchemy import SQLAlchemy


import requests


app = Flask(__name__)
app.secret_key = os.environ['APP_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
db = SQLAlchemy(app)
from divideandconquer.models import User, Response
from divideandconquer import queuemanagement
from divideandconquer.views import *
db.create_all()
queuemanagement.init_q()


#queuemanagement.refill_queue_from_db()
if __name__ == '__main__':
    print 'app running'
    app.run(debug=True, port=33507)
