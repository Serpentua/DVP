from datetime import datetime, timedelta
from sqlalchemy.sql.expression import true
from dvp.models import *
from dvp import app
import os
import hashlib
import threading
import schedule
import queue
import os.path
import uuid
import requests


activationsite = "http://maximumlan.com/"



def getSystemUUID():
    hwid = str(uuid.uuid1(uuid.getnode(),0))[24:]
    return hwid

def AddAssetObjects(apath, aid, asched):
  with app.app_context():
    files = getListOfFiles(apath)
    parentasset = asset.query.get(aid)
    initialmessage = 'The initial file processing for ' + parentasset.name + ' started!'
    alert = messages(initialmessage, datetime.now(), False)
    db.session.add(alert)
    db.session.commit()
    for eachfile in files:

        print(eachfile)
        filename = os.path.basename(eachfile)
        path = eachfile
        dateCreated = datetime.now()
        checksum = checkSum256(eachfile)
        deleted = 0
        size = os.path.getsize(eachfile)
        split_tup = os.path.splitext(filename)
        file_extension = split_tup[1]

        newasset = assetobjects(aid,filename,dateCreated,path,file_extension,checksum,deleted,size,asched)

        db.session.add(newasset)
        db.session.flush()
        print(newasset.id)
        newcheck = checksumresults(newasset.id, dateCreated,checksum,True)
        db.session.add(newcheck)
        db.session.commit()

    endmessage = 'The initial file processing for ' + parentasset.name + ' completed!'
    alert2 = messages(endmessage, datetime.now(), False)
    db.session.add(alert2)
    db.session.commit()


def totalAssetObjects():
    allassetobjects = assetobjects.query.count()
    return allassetobjects

def totalPassedAssetObjects():
    allassetobjects = checksumresults.query.filter_by(status=True).count()
    return allassetobjects

def totalFailedAssetObjects():
    allassetobjects = checksumresults.query.filter_by(status=False).count()
    return allassetobjects

def getallfailedvalidations():
    failedvalidations = checksumresults.query.filter_by(status=False)
    return failedvalidations

def regenerateChecksum(filepath):
    checksum = checkSum256(filepath)
    return checksum

def sendmessagetodb(mes):
    with app.app_context():
        db.session.add(messages(mes, datetime.now(), False))
        db.session.commit()

def _checksum256(path):
    sha256_hash = hashlib.sha256()
    with open(path,"rb") as f:
        for byte_block in iter(lambda: f.read(65536),b""):
            sha256_hash.update(byte_block)
        sha256filevalue = sha256_hash.hexdigest()  
    
    return sha256filevalue

def _checkSum256multicore(path):
    sha256_hash = hashlib.sha256() 
    with open(path,"rb") as f:
        with ThreadPoolExecutor(max_workers=16) as e:
            for byte_block in iter(lambda: f.read(65536),b""):
                e.submit(sha256_hash.update,byte_block)
        sha256filevalue = sha256_hash.hexdigest()  

    return sha256filevalue
    
def _checksumsha256mc2(path):
    sha256_hash = hashlib.sha256() 

    with open(path,"rb") as f:
        for byte_block in iter(lambda: f.read(16384),b""):         
            t = threading.Thread(target=sha256_hash.update,args=byte_block) 
            t.start()
    sha256filevalue = sha256_hash.hexdigest()  
    return sha256filevalue


def checkSum256(path): 
    hash_results = _checksum256(path)  
    return hash_results

def getexclusions():  
    return excludedfiles.query.all()

def getdeletedobjects():  
    return assetobjects.query.filter_by(deleted=True)


def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            excluded = getexclusions()
            isExcluded = False 
            for exclude in excluded:
                filename = exclude.filename
                if filename in fullPath:
                    isExcluded = True
            if isExcluded == False:
                allFiles.append(fullPath)
                
    return allFiles  

def refreshdirectories(allassets):
    counter = 0
    for eachasset in allassets:
        filepath = eachasset.path
        files = getListOfFiles(eachasset.path)
        for eachfile in files:
            filepath = eachfile
            possibleasset = assetobjects.query.filter(assetobjects.path==filepath).first()
            if not possibleasset:
                filechecksum = checkSum256(filepath)
                possiblechecksum = assetobjects.query.filter(assetobjects.checksumValue==filechecksum).first()
                if not possiblechecksum:
                    dateCreated = datetime.now()
                    asched = datetime.now()
                    deleted = 0
                    size = os.path.getsize(filepath)
                    filename = os.path.basename(filepath)
                    split_tup = os.path.splitext(filename)
                    file_extension = split_tup[1]
                    isValid = True

                    newassetobject = assetobjects(eachasset.id,filename,dateCreated,filepath,file_extension,filechecksum,deleted,size,asched)
                    db.session.add(newassetobject)
                    db.session.flush()
                    counter = counter + 1
                    newcheck = checksumresults(newassetobject.id, datetime.now(),possiblechecksum,isValid)
                    db.session.add(newcheck)
                    db.session.commit()
                else:
                    dateCreated = datetime.now()
                    asched = datetime.now()
                    deleted = 0
                    size = os.path.getsize(filepath)
                    filename = os.path.basename(filepath)
                    split_tup = os.path.splitext(filename)
                    file_extension = split_tup[1]
                    

                    newassetobject = assetobjects(eachasset.id,filename,dateCreated,filepath,file_extension,filechecksum,deleted,size,asched)
                    db.session.add(newassetobject)
                    db.session.flush()
                    counter = counter + 1
                    newcheck = checksumresults(newassetobject.id, datetime.now(),possiblechecksum,isValid)
                    db.session.add(newcheck)
                    db.session.commit()
                    alreadyExists = 'Duplicate File "' + filepath + '" already exists at "' + possiblechecksum.path + '".The asset object was still added'
                    sendmessagetodb(alreadyExists)
    return counter

def checkIfAssetObjectDeleted():
  with app.app_context():
    startalert = 'Deleted File Scan Job Started!'
    sendmessagetodb(startalert)
    allassetobjects = assetobjects.query.all()
    for assetobject in allassetobjects:
        ifExists = os.path.exists(assetobject.path)
        if not ifExists:
            filealert = 'File missing: ' + assetobject.path + '. Asset Ojbect is marked deleted in the database.'
            assetobject.deleted = true
            db.session.commit()
    endalert = 'Deleted File Scan Job Completed!'
    sendmessagetodb(endalert)

def routineScan():
  with app.app_context():
    startalert = 'Scheduled Validation Job Started'
    sendmessagetodb(startalert)
    allassetobjects = assetobjects.query.all()
    scancounter = 0
    for assetobject in allassetobjects:
        if not assetobject.deleted:
            parentasset = asset.query.get(assetobject.asset_id)
            assetobjectspan = sched.query.get(parentasset.sched_id)
            allcheck = checksumresults.query.filter_by(file_id=assetobject.id)
            lastcheck = allcheck[-1]
            nextscandate = lastcheck.dateCreated + timedelta(days=assetobjectspan.span)
            getnow = datetime.now().date()
            nextscan = nextscandate.date()
            if getnow >= nextscan:
                isValid = True
                checksum = checkSum256(assetobject.path)
                if checksum != assetobject.checksumValue:
                    isValid = False
                newcheck = checksumresults(assetobject.id, datetime.now(), checksum, isValid)
                db.session.add(newcheck)
                db.session.flush()
                if isValid == False:
                    addaknow = failedacknowledgement(assetobject.id,newcheck.id, isValid)
                    newcheck.status = False
                    db.session.add(addaknow)
                db.session.commit()
                scancounter = scancounter + 1
    endalert = 'Scheduled Validation Finished. A total of ' + str(scancounter) + ' validations executed.'
    sendmessagetodb(endalert)

 
def emailDailyEvents():
    x=2

def directoryScan():
  with app.app_context():
    directorystartalert = 'Daily Directory Job Started'
    sendmessagetodb(directorystartalert)
    allassets = asset.query.all()
    countofadditions = refreshdirectories(allassets)
    endDirectoryalert = 'Daily Directory Job Finished. A total of ' + str(countofadditions) + ' asset objects added'
    sendmessagetodb(endDirectoryalert)

def getscanschedule():
  with app.app_context():
    scanschedule = schedulesettings.query.get(1)
    scantime = scanschedule.starttime.strftime("%H:%M:%S")
    return scantime

def removeexcludedfiles():
  with app.app_context():
    alert = 'Checking for excluded Files to remove from database.'
    sendmessagetodb(alert)
    exclusions = getexclusions()
    for exclusion in exclusions:
        selectedassetobjects = assetobjects.query.filter(assetobjects.fileName.like(exclusion.filename)).all()
        for selectao in selectedassetobjects:
            db.session.delete(selectao)
            db.session.commit()
    endalert = 'Excluded files job completed.'
    sendmessagetodb(endalert)


def verifylicense():
  with app.app_context():
    x = vlicense(None, False, None)
    thelicense = license.query.get(1)
    if thelicense is not None:
        licensekey = thelicense.licensekey      
        sysinstanceid =  getSystemUUID()
        dbinstanceid = thelicense.instanceid
        if dbinstanceid != sysinstanceid:
            x.message = "Hardware ID does not match with the license"
            x.valid = False
        if dbinstanceid == sysinstanceid:
            url = activationsite + "verifylicense/" + sysinstanceid + "/" + licensekey.replace(" ", "")
            try:
                uResponse = requests.get(url)
            except requests.ConnectionError:
                return "Connection Error"                
            serverresponse = uResponse.json()
            if serverresponse['isactive'] is True and serverresponse['isactivated'] is True and serverresponse['licensevalid'] is True and serverresponse['instancematched'] is True :
                x.message = "License is active and verified."
                x.valid = True
                x.cap = serverresponse['cap']
                thelicense.cap = serverresponse['cap']
                thelicense.active = serverresponse['isactive']
                db.session.commit()
            if serverresponse['isactive'] is False:
                x.message = "License is active and verified."
                x.valid = False
                thelicense.active = False
                db.session.commit()
            if serverresponse['licensevalid'] is False:
                x.message = "License Key is not valid"
                x.valid = False
                thelicense.active = False
                db.session.commit()
            if serverresponse['instancematched'] is False:
                x.message = "The Hardware ID is mismatched. Routine Scan will not be executed."
                x.valid = False
                thelicense.active = False
                db.session.commit()
        if thelicense is None:
            x.message = "No License has been installed"
            x.valid = False
    sendmessagetodb(x.message)
    return x



def startscheduledworkers():

    jobqueue = queue.Queue()
    def worker_main():
        while 1:
            job_func = jobqueue.get()
            job_func()
            jobqueue.task_done()

    scantime = getscanschedule()
    schedule.every().day.at(scantime).do(jobqueue.put, checkIfAssetObjectDeleted)
    schedule.every().day.at(scantime).do(jobqueue.put, directoryScan)
    schedule.every().day.at(scantime).do(jobqueue.put, removeexcludedfiles)
    schedule.every().day.at(scantime).do(jobqueue.put, routineScan)

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    while 1:
        schedule.run_pending()
        time.sleep(60)

