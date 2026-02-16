from sqlalchemy.sql.sqltypes import DateTime, Integer, SmallInteger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from dvp import app
from dvp.dbstruct import createAllTables
import time

db = SQLAlchemy(app)

class vlicense:
  def __init__(self, message,valid, cap):
    self.message = message
    self.valid = valid
    self.cap = cap


class auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255),nullable=False)
    password = db.Column(db.String(255),nullable=True)
    domain = db.Column(db.String(255),nullable=True)
    fileProtocol_id = db.Column(db.Integer, db.ForeignKey('fileprotocols.id'), nullable=True)
    def __init__(self, username, password, domain, fileProtocol_id):
       self.username = username
       self.password = password
       self.domain = domain
       self.fileProtocol_id = fileProtocol_id

class assettype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    def __init__(self, name, dateCreated):
       self.name = name

class fileprotocols(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    def __init__(self, name):
       self.name = name

class sched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    span = db.Column(db.Integer)
    def __init__(self,name,span):
       self.name = name
       self.span = span

class checksumresults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('assetobjects.id', ondelete="CASCADE"), nullable=False)
    dateCreated = db.Column(db.DateTime)
    result = db.Column(db.String(255))
    status = db.Column(db.Boolean)
    def __init__(self, file_id, dateCreated,result,status):
       self.file_id = file_id
       self.dateCreated = dateCreated
       self.result = result
       self.status = status
    @property
    def assetobject(self):
       return assetobjects.query.filter_by(id=self.file_id).first()

class assetobjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id', ondelete="CASCADE"), nullable=False)
    fileName = db.Column(db.String(255))
    dateCreated = db.Column(db.DateTime)
    path = db.Column(db.String(255))
    assetextension = db.Column(db.String(255))
    checksumValue = db.Column(db.String(255))
    deleted = db.Column(db.Boolean)
    sizeMB = db.Column(db.BigInteger)
    nextvalidationdate = db.Column(db.DateTime)
    checksum = relationship('checksumresults', passive_deletes=True)
    def __init__(self, asset_id,fileName, dateCreated, path, assetextension, checksumValue, deleted, sizeMB, nextvalidationdate):
       self.asset_id = asset_id
       self.fileName = fileName
       self.dateCreated = dateCreated
       self.path = path
       self.assetextension = assetextension #file extension
       self.checksumValue = checksumValue
       self.deleted = deleted
       self.sizeMB = sizeMB
       self.nextvalidationdate = nextvalidationdate #might be an extra field, may delete.

class asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    dateCreated = db.Column(db.DateTime)
    path = db.Column(db.String(1024))
    fileprotocols_id = db.Column(db.Integer, db.ForeignKey('fileprotocols.id'), nullable=False) 
    auth_id = db.Column(db.Integer, db.ForeignKey('auth.id'), nullable=False)
    assetobjectgroup_id = db.Column(db.Integer, db.ForeignKey('assetobjectgroup.id', ondelete="CASCADE"), nullable=False)
    sched_id = db.Column(db.Integer, db.ForeignKey('sched.id'), nullable=False)
    externalAssetID = db.Column(db.String(255))
    AssetObjects = relationship('assetobjects', passive_deletes=True)
    def __init__(self, name, dateCreated, path, fileprotocols_id, auth_id, assetobjectgroup_id, sched_id,externalAssetID):
       self.name = name
       self.dateCreated = dateCreated
       self.path = path
       self.fileprotocols_id = fileprotocols_id
       self.auth_id = auth_id
       self.assetobjectgroup_id = assetobjectgroup_id
       self.sched_id = sched_id
       self.externalAssetID = externalAssetID
    @property
    def schedules(self):
        return sched.query.filter_by(id=self.sched_id).first()
    def linkedassetgroup(self):
        return assetobjectgroup.query.filter_by(id=self.assetobjectgroup_id).first()
     
class assetobjectgroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    dateCreated = db.Column(db.DateTime)
    asset = relationship('asset', passive_deletes=True)
    def __init__(self, name, dateCreated):
       self.name = name
       self.dateCreated = dateCreated

class messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime)
    aknowledged = db.Column(db.Boolean)
    def __init__(self, message, dateCreated, aknowledged):
       self.message = message
       self.dateCreated = dateCreated
       self.aknowledged = aknowledged

class schedulesettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    starttime = db.Column(db.Time)
    def __init__(self, starttime):
       self.starttime = starttime

class excludedfiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    def __init__(self, filename):
       self.filename = filename


class license(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    licensekey = db.Column(db.Text, nullable=True)
    instanceid = db.Column(db.Text, nullable=True)
    activatedon = db.Column(db.DateTime)
    cap = db.Column(db.Integer)
    active = db.Column(db.Boolean,nullable=True)
    def __init__(self, licensekey, instanceid, activatedon, cap, active):
       self.licensekey = licensekey
       self.instanceid = instanceid
       self.activatedon = activatedon
       self.cap = cap
       self.active = active

class failedacknowledgement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('assetobjects.id', ondelete="CASCADE"), nullable=False)
    checksum_id = db.Column(db.Integer, db.ForeignKey('checksumresults.id'), nullable=False)
    aknowledged = db.Column(db.Boolean)
    def __init__(self, file_id,checksum_id,aknowledged):
       self.file_id = file_id
       self.checksum_id = checksum_id
       self.aknowledged = aknowledged
    @property
    def linkedassetobject(self):
       return assetobjects.query.filter_by(id=self.file_id).first()
    @property
    def lastcheck(self):
       return checksumresults.query.filter_by(id=self.checksum_id).first()

class organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orgname = db.Column(db.String(255), nullable=False)
    orgadd1 = db.Column(db.String(255), nullable=False)
    orgadd2 = db.Column(db.String(255), nullable=True)
    orgcity = db.Column(db.String(255), nullable=False)
    orgstate = db.Column(db.String(255), nullable=False)
    orgpostal = db.Column(db.String(255), nullable=False)
    orgphone = db.Column(db.String(255))
    def __init__(self, orgname,orgadd1,orgadd2,orgcity,orgstate,orgpostal,orgphone):
       self.orgname = orgname
       self.orgphone = orgphone
       self.orgadd1 = orgadd1
       self.orgadd2 = orgadd2
       self.orgcity = orgcity
       self.orgstate = orgstate
       self.orgpostal = orgpostal
       self.orgphone = orgphone

def populateDefault():
    fileProtocolsmb = fileprotocols('SMB')
    fileProtocollocal = fileprotocols('Local Address')
    addsched = sched('Daily', 1)
    schedule7 = sched('Weekly', 7)
    schedule14 = sched('Bi-Weekly', 14)
    schedule30 = sched('Monthly', 28)
    shedsettings = schedulesettings("01:00:00")
    db.session.add(addsched)
    db.session.commit()
    db.session.add(schedule7)
    db.session.add(schedule14)
    db.session.add(schedule30)
    db.session.add(fileProtocolsmb)
    db.session.add(fileProtocollocal)
    db.session.add(shedsettings)
    db.session.commit()
    localAuthaccount = auth('Local Account', '', '', 1)
    db.session.add(localAuthaccount)
    db.session.commit()

def deletefailedchecks():
    checks = checksumresults.query.filter(checksumresults.status==False)
    for check in checks:
        db.session.delete(check)
    db.session.commit()
def deletedfailedak():
    items = failedacknowledgement.query.all()
    for item in items:
        db.session.delete(item)
    db.session.commit()


class SmtpSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emailserver = db.Column(db.String(255), nullable=False)
    port = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    tls = db.Column(db.Boolean(), nullable=False)
    emailEnabled = db.Column(db.Boolean(), nullable=False)
    def __init__(self, emailserver,port,username,password,tls,emailEnabled):
       self.emailserver = emailserver
       self.port = port
       self.username = username
       self.password = password
       self.tls = tls
       self.emailEnabled = emailEnabled


#deletedfailedak()
#deletefailedchecks()
#createAllTables()
#db.create_all()
#populateDefault()
