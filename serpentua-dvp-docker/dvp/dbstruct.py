from sqlalchemy import *
from dvp.database import createDBConnectionString

connectionString = createDBConnectionString()
engine = create_engine(connectionString, echo = True)
meta = MetaData()

def createAllTables():
    assetobjectgroup = Table(
       'assetobjectgroup', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String(255)), 
       Column('dateCreated', DateTime)
    )
    #useed to define file or folder in assetobjects
    assettype = Table(
       'assettype', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String(255))
    )
    fileprotocols = Table(
       'fileprotocols', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String(255))
    )
    sched = Table(
       'sched', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String(255)), 
       Column('span', Integer)
    )
    asset = Table(
       'asset', meta, 
       Column('id', Integer, primary_key = True), 
       Column('name', String(255)), 
       Column('dateCreated', DateTime),
       Column('path', String(1024)), 
       Column('assetobjectgroup_id',Integer, ForeignKey('assetobjectgroup.id', ondelete="CASCADE")), 
       Column('fileprotocols_id',Integer, ForeignKey('fileprotocols.id')), 
       Column('auth_id',Integer, ForeignKey('auth.id')), 
       Column('sched_id',Integer, ForeignKey('sched.id')), 
       Column('externalassetID', String(255))
    )
    assetobjects = Table(
       'assetobjects', meta, 
       Column('id', Integer, primary_key = True), 
       Column('asset_id', Integer, ForeignKey('asset.id', ondelete="CASCADE")),
       Column('fileName', String(255)), 
       Column('dateCreated', DateTime),
       Column('path', String(1024)), 
       Column('assetextension',String(255)),  
       Column('checksumValue',String(255)), 
       Column('deleted',Boolean), 
       Column('sizeMB',BigInteger),
       Column('nextvalidationdate', DateTime),
    )
    checksumresults = Table(
       'checksumresults', meta, 
       Column('id', Integer, primary_key = True), 
       Column('file_id',Integer, ForeignKey('assetobjects.id', ondelete="CASCADE")), 
       Column('dateCreated', DateTime),
       Column('result', String(255)),
       Column('status', Boolean),   
    )
    auth = Table(
       'auth', meta, 
       Column('id', Integer, primary_key = True), 
       Column('username', String(255)), 
       Column('password', String(255)),
       Column('domain', String(255)),
       Column('fileProtocol_id',Integer, ForeignKey('fileprotocols.id'))
    )
    messages = Table(
       'messages', meta, 
       Column('id', Integer, primary_key = True),
       Column('message', Text),
       Column('dateCreated', DateTime),
       Column('aknowledged', Boolean),    
    )
    schedulesettings = Table(
       'schedulesettings', meta, 
       Column('id', Integer, primary_key = True),
       Column('starttime', Time),
    )
    excludedfiles = Table(
       'excludedfiles', meta, 
       Column('id', Integer, primary_key = True),
       Column('filename', String(255)),
    )
    license = Table(
       'license', meta, 
       Column('id', Integer, primary_key = True),
       Column('licensekey', String(255)),
       Column('instanceid', String(255)),
       Column('activatedon', DateTime),
       Column('cap',BigInteger),
       Column('active', Boolean),
    )
    failedacknowledgement = Table(
       'failedacknowledgement', meta, 
       Column('id', Integer, primary_key = True),
       Column('file_id', Integer, ForeignKey('assetobjects.id', ondelete="CASCADE")),
       Column('checksum_id', Integer, ForeignKey('checksumresults.id')),
       Column('aknowledged', Boolean),
    )
    organization = Table(
       'organization', meta, 
       Column('id', Integer, primary_key = True),
       Column('orgname', String(255)),
       Column('orgadd1', String(255)),
       Column('orgadd2', String(255)),
       Column('orgcity', String(255)),
       Column('orgstate', String(255)),
       Column('orgpostal', String(255)),
       Column('orgphone', String(255)),
    )
    SmtpSettings = Table(
       'SmtpSettings', meta, 
       Column('id', Integer, primary_key = True),
       Column('emailserver', String(255)),
       Column('port', String(255)),
       Column('username', String(255)),
       Column('password', String(255)),
       Column('tls', Boolean()),
       Column('emailEnabled', Boolean()),
    )

    meta.create_all(engine)
