from datetime import datetime, timedelta
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null, true
from dvp.models import *
import os



def formatAssetObjectsData(id):
    assetresults = checksumresults.query.filter(checksumresults.file_id==id).all()
    assetobject = assetobjects.query.get(id)
    topstring = [assetobject.fileName, assetobject.path, 'Original Value: ' + assetobject.checksumValue]
    array = [topstring]
    array.append(['Date Created', 'Checksum Result', 'Is Valid'])
    for assetresult in assetresults:
        assedate = str(assetresult.dateCreated)
        array_value = [assedate,assetresult.result,assetresult.status]
        array.append(array_value)
    return array

def formatAlertsData():
    allmessages = messages.query.all()
    topstring = ['Date','Message', 'Is Aknowledged']
    array = []
    array.append(topstring)
    for eachmessage in allmessages:
        date = str(eachmessage.dateCreated)
        data = [eachmessage.dateCreated, eachmessage.message, eachmessage.aknowledged]
        array.append(data)
    return array

def formatFailedChecksData():
    allfails = checksumresults.query.filter(checksumresults.status==False).all()
    topstring = ['Date','Asset Object', 'Path', 'Original Checksum', 'Failed Checksum']
    array = []
    array.append(topstring)
    for eachfail in allfails:
        date = str(eachfail.dateCreated)
        assetobject = assetobjects.query.get(eachfail.file_id)
        assetname =  assetobject.fileName
        path = assetobject.path      
        originalchecksum = assetobject.checksumValue
        failedchecksumdata = eachfail.result
        
        lineinarray = [date, assetname, path, originalchecksum, failedchecksumdata]
        array.append(lineinarray)
    return array

def formatDeletedData():
    alldeleted = assetobjects.query.filter(assetobjects.deleted==True).all()
    topstring = ['Asset Name','Path', 'Original Checksum Value', 'Deleted']
    array = []
    array.append(topstring)
    for deletedobject in alldeleted:
        name = deletedobject.fileName
        path = deletedobject.path
        checksumvalue = deletedobject.checksumValue 
        data = [name, path, checksumvalue, True]
        array.append(data)
    return array