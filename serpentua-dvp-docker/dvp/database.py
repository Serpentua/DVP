import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

dbuser = os.environ.get('DB_USER', 'dvp')
dbpassword = os.environ.get('DB_PASSWORD', '102938zmPOI!')
dbname = os.environ.get('DB_NAME', 'dvp_app')
dbserver = os.environ.get('DB_HOST', '192.168.1.121')

def createDBConnectionString():
    string = 'mysql+pymysql://' + dbuser + ':' + dbpassword + '@' + dbserver + "/" + dbname
    return string
