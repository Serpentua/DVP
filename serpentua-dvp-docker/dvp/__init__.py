"""
The flask application package.
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import flask_excel as excel
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from sqlalchemy.sql import text
from dvp.database import createDBConnectionString
from wtforms import *
from flask_wtf import *



string = createDBConnectionString()
# change to name of your database; add path if necessary


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = string


app.config['SECRET_KEY'] = '\xd936M\xcd\xd2\xabP\xec\x17\xae\x1a\xd8r\x1d\xd7bY\xd6FI\xa1\xbb0'

Bootstrap(app)
excel.init_excel(app)
mail = Mail(app)

from dvp.models import *

with app.app_context():
    db.create_all()

    if not sched.query.first():
        populateDefault()

    try:
        checksmtp = SmtpSettings.query.get(1)
        if checksmtp is not None:
            app.config['MAIL_SERVER']= checksmtp.emailserver
            app.config['MAIL_PORT'] = checksmtp.port
            app.config['MAIL_USERNAME'] = checksmtp.username
            app.config['MAIL_PASSWORD'] = checksmtp.password
            app.config['MAIL_USE_TLS'] = checksmtp.tls
    except Exception:
        pass



import dvp.views
from dvp.file import startscheduledworkers

from threading import Thread
threads = [
    Thread(target = startscheduledworkers)
]
for thread in threads:
    thread.start()