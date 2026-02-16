"""
Routes and views for the flask application.
"""

from ast import Try
from datetime import datetime, timedelta
from datetime import time
from re import L
import requests
from flask import request, flash, url_for, redirect, render_template, jsonify
from sqlalchemy.sql.expression import select
from sqlalchemy import desc
from time import gmtime, strftime
from dvp import app, forms
from dvp.models import *
from dvp.file import *
from dvp.reports import *
import threading
from pathlib import Path
import flask_excel as excel
from flask_mail import Mail, Message


ROWS_PER_PAGE = 20

@app.route('/', methods=['GET'])
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    pagemes = request.args.get('pagemes', 1, type=int)
    numofassets = totalAssetObjects()
    numofpassedassets = totalPassedAssetObjects()
    numoffailedassets = totalFailedAssetObjects()
    failedvalidations = getallfailedvalidations()
    aknowledgements = failedacknowledgement.query.filter(failedacknowledgement.aknowledged==False).paginate(page=page, per_page=ROWS_PER_PAGE)
    internalmessages = messages.query.filter(messages.aknowledged==False).order_by(desc(messages.dateCreated)).paginate(page=pagemes, per_page=ROWS_PER_PAGE)
   
    return render_template(
        'index.html',
        title='DashBoard',
        numofasset=numofassets,
        numofpassedassets=numofpassedassets,
        numoffailedassets=numoffailedassets,
        failedvalidations=failedvalidations,
        aknowledgements=aknowledgements,
        internalmessages=internalmessages,
    )

@app.route('/assets/assetgroups', methods=['GET', 'POST'])
def assetgroups():
    createform = forms.AssetGroupForm()
    searchform = forms.SearchAssetGroupsForm()

    if request.method == 'POST':
        if createform.submit.data and  createform.validate_on_submit():
            assetgroup = assetobjectgroup(request.form['name'], datetime.now())
            db.session.add(assetgroup)
            db.session.commit()
            flash('Record was successfully added')
            url = '/assets/assetsingroup/' +str(assetgroup.id)
            return redirect(url)

        if searchform.search.data and searchform.validate_on_submit():
            search = "%{}%".format(request.form['searchfield'])
            searchresults = assetobjectgroup.query.filter(assetobjectgroup.name.like(search)).all()
            searchform = forms.SearchAssetGroupsForm()
            return render_template(
                '/assets/assetgroups.html',
                title='Asset Groups',
                year=datetime.now().year,
                message='Asset Groups',
                createform=createform,
                searchform=searchform,
                assetobjectgroup = searchresults
            )
    return render_template(
        '/assets/assetgroups.html',
        title='Asset Groups',
        year=datetime.now().year,
        message='Asset Groups',
        createform=createform,
        searchform=searchform,
        assetobjectgroup = assetobjectgroup.query.all()
    )



@app.route('/assets/assetsingroup/<id>', methods=['GET', 'POST'])
def assets(id):
    assetgroup = assetobjectgroup.query.get(id)
    assetsingroup = asset.query.filter_by(assetobjectgroup_id=id) #get assets by group id
    newasset = forms.NewAssetForm()
    newasset.schedules.choices = [(g.id, g.name) for g in sched.query.order_by('name')]
    if request.method == 'POST':
        if newasset.submit.data and  newasset.validate_on_submit():
            assetgroupid = assetobjectgroup.query.get(id)
            path = request.form['path'].strip()
            pathtype = fileprotocols.query.get(2)
            authid = auth.query.get(1)
            if "smb:" in path:
                pathtype = fileprotocols.query.get(1)
            aname = request.form['name'].strip()
            adate = datetime.now()
            apath = path
            asched = request.form['schedules']
            aextid = request.form['externalAssetID']
            aschedfull = sched.query.get(asched)
            daystoadd = aschedfull.span
            
            anextcheck = adate  + timedelta(days=daystoadd)
           
            reqAsset = asset(aname,adate,apath, pathtype.id, authid.id, assetgroupid.id, asched, aextid)
            db.session.add(reqAsset)
            db.session.commit()

            th = threading.Thread(target=AddAssetObjects, args=(reqAsset.path,reqAsset.id,anextcheck))
            th.start()

           
    return render_template(
        '/assets/assets.html',
        title='Assets',
        year=datetime.now().year,
        message='Assets',
        assetgroup = assetgroup,
        assetsingroup = assetsingroup,
        newasset = newasset,
    )


@app.route('/assets/deleteasset/<id>')
def deleteasset(id):
    selectasset = asset.query.get(id)
    return render_template(
        '/assets/deleteassets.html',
        title='Delete Asset',
        year=datetime.now().year,
        message='Delete Asset',
        selectasset=selectasset,
    )
@app.route('/assets/confirmeddeleteasset/<id>')
def confirmeddelete(id):
    selectedasset = asset.query.get(id)
    parentgroup = selectedasset.assetobjectgroup_id
    db.session.delete(selectedasset)
    db.session.commit()
    url = '/assets/assetsingroup/' +str(parentgroup)
    return redirect(url)


@app.route('/assets/deleteassetgroup/<id>')
def deleteassetgroup(id):
    selectedassetgroup = assetobjectgroup.query.get(id)
    return render_template(
        '/assets/deleteassetgroup.html',
        title='Delete Asset',
        year=datetime.now().year,
        message='Delete Asset Group',
        selectedassetgroup=selectedassetgroup,
    )
@app.route('/assets/confirmeddeleteassetgroup/<id>')
def confirmedgroupdelete(id):
    selectedassetgroup = assetobjectgroup.query.get(id)
    db.session.delete(selectedassetgroup)
    db.session.commit()
    url = '/assets/assetgroups' 
    return redirect(url)

@app.route('/assets/editassetgroup/<id>', methods=['GET', 'POST'])
def editassetgroup(id):
     form = forms.AssetGroupForm()
     selectedassetgroup = assetobjectgroup.query.get(id)
     form.name.data = selectedassetgroup.name
     if form.validate_on_submit():
        aname = request.form['name']
        selectedassetgroup.name = aname
        db.session.commit()
        url = '/assets/assetgroups'
        return redirect(url)
     return render_template(
        '/assets/editassetgroup.html',
        title='Edit Asset Group',
        year=datetime.now().year,
        message='Edit Asset Group',
        form=form,
        selectedassetgroup=selectedassetgroup,
        )
@app.route('/assets/editasset/<id>', methods=['GET', 'POST'])
def editasset(id):
        form = forms.EditAssetForm()
        selectedasset = asset.query.get(id)
        schedule = sched.query.get(selectedasset.sched_id)
        defaultsched = [(schedule.id, schedule.name)]
        choices = []
        for g in sched.query.all():
            if (g.id is not schedule.id):
                choices.append((g.id, g.name))
        finalchoices = defaultsched + choices 
        form.name.data = selectedasset.name
        form.path.data = selectedasset.path
        form.schedules.choices = finalchoices      
        if form.validate_on_submit():
            aname = request.form['name']
            asched = request.form['schedules']
            aextid = request.form['externalAssetID']
            selectedasset.name = aname
            selectedasset.sched_id = asched
            selectedasset.externalAssetID = aextid
            db.session.commit()
            url = '/assets/assetobject/' +str(selectedasset.id)
            return redirect(url)
        return render_template(
            '/assets/editasset.html',
            title='Edit Asset',
            year=datetime.now().year,
            message='Edit Asset',
            form=form,
            selectedasset=selectedasset,
        )

@app.route('/assets/assetobject/<id>', methods=['GET','POST'])
def assetobject(id):
    searchform = forms.SearchAssetObjectForm()
    page = request.args.get('page', 1, type=int)
    parentasset = asset.query.get(id)
    childassetobjects = assetobjects.query.filter_by(asset_id=id).paginate(page=page, per_page=ROWS_PER_PAGE)
    assetgroup = assetobjectgroup.query.get(parentasset.assetobjectgroup_id)
    if request.method == 'POST':
        if searchform.search.data and  searchform.validate_on_submit():
                search = "%{}%".format(request.form['searchfield'])
                searchresults = assetobjects.query.filter(assetobjects.asset_id==parentasset.id,assetobjects.fileName.like(search)).paginate(page=page, per_page=ROWS_PER_PAGE)
                searchform = forms.SearchAssetObjectForm()
                return render_template(
                    '/assets/assetobject.html',
                    title='Asset Objects',
                    year=datetime.now().year,
                    assetgroup=assetgroup,
                    parentasset=parentasset,
                    message='Asset Objects',
                    searchform = searchform,
                    childassetobjects = searchresults,
                )  
    return render_template(
        '/assets/assetobject.html',
        title='Asset Objects',
        year=datetime.now().year,
        childassetobjects=childassetobjects,
        assetgroup=assetgroup,
        parentasset=parentasset,
        message='Asset Objects',
        searchform = searchform,
    )


@app.route('/assets/ojbectvalidations/<id>', methods=['GET','POST'])
def ojbectvalidations(id):
    page = request.args.get('page', 1, type=int)
    parentassetobject = assetobjects.query.get(id)
    checksumResults = checksumresults.query.filter_by(file_id=id).paginate(page=page, per_page=ROWS_PER_PAGE)
    parentasset = asset.query.get(parentassetobject.asset_id)
    assetgroup = assetobjectgroup.query.get(parentasset.assetobjectgroup_id)
    return render_template(
        '/assets/objectvalidation.html',
        title='Asset Object Validation',
        year=datetime.now().year,
        parentassetobject=parentassetobject,
        checksumResults=checksumResults,
        parentasset=parentasset,
        assetgroup=assetgroup,
        message='Asset Object Validation',
    )

@app.route('/assets/revalidate/<id>')
def revalidate(id):
    parentassetobject = assetobjects.query.get(id)
    checksum = regenerateChecksum(parentassetobject.path)
    parentassetobject.checksumValue = checksum
    db.session.commit()
    url = '/assets/ojbectvalidations/' +str(parentassetobject.id)
    return redirect(url)

@app.route('/dismiss/<id>')
def dismiss(id):
    whichmessage = failedacknowledgement.query.get(id)
    whichmessage.aknowledged = True 
    db.session.commit()
    url = '/'
    return redirect(url)

@app.route('/dismissallak')
def dismissallak():
    messages = failedacknowledgement.query.all()
    for message in messages:
        message.aknowledged = True    
    db.session.commit()
    url = '/'
    return redirect(url)

@app.route('/dismissallalerts')
def dismissallalerts():
    allmessages = messages.query.all()
    for message in allmessages:
        message.aknowledged = True    
    db.session.commit()
    url = '/'
    return redirect(url)


@app.route('/dismissmessage/<id>')
def dismissmessage(id):
    whichmessage = messages.query.get(id)
    whichmessage.aknowledged = True 
    db.session.commit()
    url = '/'
    return redirect(url)

@app.route('/settings/license/delete', methods=['GET'])
def dellicense():
    thelicense = license.query.get(1)
    thelicense.licensekey = None
    thelicense.instanceid = None
    thelicense.activatedon = None
    thelicense.cap = None
    db.session.commit()
    url = '/settings/license'
    return redirect(url)

@app.route('/settings/license', methods=['GET','POST'])
def Mylicense():
    checklicense = license.query.get(1)
    if checklicense is None or checklicense.licensekey is None:
        form = forms.addlicense()
        if request.method == 'POST':
            if form.validate_on_submit():
                
                message = '' 
                licensekey = request.form['licensekey']
                instanceid =  getSystemUUID()
                activatedon = datetime.now()
                url = activationsite + "activate/" + instanceid + "/" + licensekey.replace(" ", "")
                try:
                    uResponse = requests.get(url)
                except requests.ConnectionError:
                   return "Connection Error"  
                
                serverresponse = uResponse.json()
                #add encryption for json 
                if serverresponse['licensevalid'] is True:
                    if serverresponse['instancetaken'] is False:
                        if serverresponse['isactivated'] is True:
                            if checklicense is None:
                                newLicense = license(licensekey, instanceid, activatedon, serverresponse['cap'], False)
                                db.session.add(newLicense)
                                db.session.commit()
                                fullyactivated = True
                                message = 'Activation was successful!'
                            if checklicense is not None:
                                checklicense.licensekey = licensekey
                                checklicense.instanceid = instanceid
                                checklicense.activatedon = activatedon  
                                checklicense.cap = serverresponse['cap']      
                                db.session.commit()
                                fullyactivated = True
                                message = 'Activation was successful!'
                    if serverresponse['isactivated'] is False:
                        message = 'Activation Failed'
                        fullyactivated = False
                    if serverresponse['instancetaken'] is True:
                        message = 'The license was already used for another instance. Please check your subscription settings.'
                        fullyactivated = False
                    if serverresponse['licensevalid'] is False: 
                        message = 'License key is invalid'
                        fullyactivated = False

                if fullyactivated is True: 
                    thelicense = license.query.get(1)
                    return render_template(
                            '/settings/license.html',
                            title='License',
                            year=datetime.now().year,
                            form = None,
                            message = message,
                            key = None,
                            thelicense = thelicense,
                    )
                if fullyactivated is False:
                    form = forms.addlicense()
                    return render_template(
                            '/settings/license.html',
                            title='License',
                            year=datetime.now().year,
                            form = None,
                            key = licensekey,
                            thelicense = None,
                            message = message,
                    )
        return render_template(
            '/settings/license.html',
            title='License',
            year=datetime.now().year,
            form = form,
            message = None,
            thelicense = None,
            key = None,
        )
    return render_template(
        '/settings/license.html',
        title='License',
        year=datetime.now().year,
        thelicense = checklicense,
        form = None,      
    )

@app.route('/settings/excludedfiles', methods=['GET', 'POST'])
def settingsexcludedfiles():
    form = forms.addexcludedfiles()
    excluded = excludedfiles.query.all()
    if request.method == 'POST':
        if form.validate_on_submit():
            filenameorpath = request.form['name']
            newexclude = excludedfiles(filenameorpath)
            db.session.add(newexclude)
            db.session.commit()
            form = forms.addexcludedfiles()
            excluded = excludedfiles.query.all()
            return render_template(
                '/settings/excludedfiles.html',
                title='Excluded Files',
                year=datetime.now().year,
                excluded = excluded,
                form = form,
            )
    return render_template(
        '/settings/excludedfiles.html',
        title='Excluded Files',
        year=datetime.now().year,
        excluded = excluded,
        form = form,
    )

@app.route('/settings/excludedfiles/delete/<id>')
def delexclusion(id):
    deleteexcluded = excludedfiles.query.get(id)
    db.session.delete(deleteexcluded)
    db.session.commit()
    return redirect('/settings/excludedfiles')

@app.route('/settings/organization', methods=['GET', 'POST'])
def orgs():
    org = organization.query.get(1)
    if not org:
        form = forms.editOrganization()
        if request.method == 'POST':
            if form.validate_on_submit():
                orgname = request.form['orgname']
                orgphone = request.form['orgphone']
                orgadd1 = request.form['orgadd1']
                orgadd2 = request.form['orgadd2']
                orgcity = request.form['orgcity']
                orgstate = request.form['orgstate']
                orgpostal = request.form['orgpostal']
                neworg = organization(orgname, orgadd1, orgadd2, orgcity, orgstate, orgpostal, orgphone)
                db.session.add(neworg)
                db.session.commit()
                org = organization.query.get(1)
                return render_template(
                    '/settings/organization.html',
                    title='Organization',
                    year=datetime.now().year,
                    org=org,
                    form = None,
                    )
        return render_template(
        '/settings/organization.html',
        title='Organization',
        year=datetime.now().year,
        org = None,
        form=form,
        )
    if org:
        return render_template(
            '/settings/organization.html',
            title='Organization',
            year=datetime.now().year,
            org=org,
            form = None,
            )

@app.route('/settings/editorginization', methods=['GET', 'POST'])
def editorg():
    selectorg = organization.query.get(1)
    form = forms.editOrganization()
    form.orgname.data = selectorg.orgname
    form.orgadd1.data = selectorg.orgadd1
    form.orgadd2.data = selectorg.orgadd2
    form.orgcity.data = selectorg.orgcity
    form.orgstate.data = selectorg.orgstate
    form.orgpostal.data = selectorg.orgpostal
    form.orgphone.data = selectorg.orgphone  
    if request.method == 'POST':
        if form.validate_on_submit():
            selectorg = organization.query.get(1)
            selectorg.orgname = request.form['orgname']
            selectorg.orgphone = request.form['orgphone']
            selectorg.orgadd1 = request.form['orgadd1']
            selectorg.orgadd2 = request.form['orgadd2']
            selectorg.orgcity = request.form['orgcity']
            selectorg.orgstate = request.form['orgstate']
            selectorg.orgpostal = request.form['orgpostal']
            db.session.commit()         
            return render_template(
                '/settings/organization.html',
                title='Organization',
                year=datetime.now().year,
                org = selectorg,
                form = None,
                )
    return render_template(
        '/settings/editorganization.html',
        title='Edit Organization',
        year=datetime.now().year,
        form = form,
        )


@app.route('/settings/system', methods=['GET', 'POST'])
def system():
    timezone = datetime.now().astimezone().tzinfo
    now = datetime.now()
    currenttime = now.strftime("%I:%M:%p")
    schedule = schedulesettings.query.get(1)
    readabletime = datetime.strptime(str(schedule.starttime), "%H:%M:%S")
    parsedTime = readabletime.strftime("%I:%M %p")
    form = forms.editschedule()
 
    if request.method == 'POST':
        if form.validate_on_submit():
            timezone = strftime("%z", gmtime())
            currenttime = datetime.now()
            newstarttime = request.form['starttime']
            schedule.starttime = newstarttime
            db.session.commit()
            schedule = schedulesettings.query.get(1) 
            readabletime = datetime.strptime(str(schedule.starttime), "%H:%M:%S")
            parsedTime = readabletime.strftime("%I:%M %p")
            form = forms.editschedule()
            return render_template(
                '/settings/system.html',
                title='System',
                year=datetime.now().year,
                parsedTime=parsedTime,
                form=form,
                currenttime=currenttime,
                timezone=timezone,
            )
    return render_template(
        '/settings/system.html',
        title='System',
        year=datetime.now().year,
        parsedTime=parsedTime,
        form=form,
        currenttime=currenttime,
        timezone=timezone,
    )

@app.route('/reports', methods=['GET', 'POST'])
def reports():
    aobjform = forms.genasobjreportform()
    if request.method == 'POST':
        if aobjform.objid.data and aobjform.validate_on_submit():
            assetid = request.form['objid']
            data = genassetobjreport(assetid)
            return data
    return render_template(
        'reports.html',
        title='Reports',
        year=datetime.now().year,
        aobjform=aobjform,
    )

@app.route('/settings/email', methods=['GET'])
def email():
    checksmtp = SmtpSettings.query.get(1)
    if checksmtp is not None:
        smtp = checksmtp
        return render_template(
            'settings/smtp.html',
            title='Email Settings',
            year=datetime.now().year,
            smtp = smtp,
        )
    if checksmtp is None:
        return redirect('/settings/editemail')

@app.route('/settings/editemail', methods=['GET', 'POST'])
def editemail():
    checksmtp = SmtpSettings.query.get(1)
    form = forms.SMTP()
    if checksmtp is not None:
        form = forms.SMTP(obj=checksmtp)
        return render_template(
            'settings/editsmtp.html',
            title='Email Settings',
            year=datetime.now().year,
            form = form,
        )
    if request.method == 'POST':
        if form.validate_on_submit():
            smtpserver = request.form['emailserver']
            smtpport = request.form['port']
            smtpusername = request.form['username']
            smtppassword = request.form['password']

            if request.form['tls'] is 'y':
                    tlsResult = True
            else:
                    tlsResult = False

            if request.form['emailEnabled'] is 'y':
                    emailResult = True
            else:
                    emailResult = False
             
            smtptls = tlsResult
            smtpemailEnabled = emailResult
            if checksmtp is None:           
                smtpnew = SmtpSettings(smtpserver, smtpport, smtpusername, smtppassword, smtptls, smtpemailEnabled)
                db.session.add(smtpnew)
            if checksmtp is not None:
                checksmtp.emailserver = request.form['emailserver']
                checksmtp.port = request.form['port']
                checksmtp.username = request.form['username']
                checksmtp.password = request.form['password']
                if request.form['tls'] is 'y':
                    tlsResult = True
                else:
                    tlsResult = False
                checksmtp.tls = tlsResult

                if request.form['emailEnabled'] is 'y':
                    emailResult = True
                else:
                    emailResult = False
                checksmtp.emailEnabled = emailResult

            db.session.commit() 
            return redirect('/settings/email')
    return render_template(
            'settings/editsmtp.html',
            title='Email Settings',
            year=datetime.now().year,         
            form = form,
        )


def sendtestemail():
    checksmtp = SmtpSettings.query.get(1)
    msg = Message('Data Validation Platform: Test Message', sender = checksmtp.username, recipients = [checksmtp.username])
    msg.body = "This is an test email from your instance of the Data Validation Platform"
    try:
        mail.send(msg)
        return "Message Sent"
    except:
        return "Message has not been sent"
    

@app.route("/genassetobjreport/<id>", methods=['GET'])
def genassetobjreport(id):
    assetobject = assetobjects.query.get(id)
    results = formatAssetObjectsData(id)
    getdate = datetime.now()
    date = getdate.strftime("%b_%d_%Y")
    filename = assetobject.fileName + '_' + date 
    exceldata = excel.make_response_from_array(results, "csv", file_name=filename)
    return exceldata

@app.route("/genalertsreport", methods=['GET'])
def genalertsreport():
    results = formatAlertsData()
    getdate = datetime.now()
    date = getdate.strftime("%b_%d_%Y")
    filename = 'AllAlerts_' + date
    exceldata = excel.make_response_from_array(results, "csv", file_name=filename)
    return exceldata

@app.route("/genfailassobjreport", methods=['GET'])
def genfailassobjreport():
    results = formatFailedChecksData()
    getdate = datetime.now()
    date = getdate.strftime("%b_%d_%Y")
    filename = 'FailedValidations_' + date
    exceldata = excel.make_response_from_array(results, "csv", file_name=filename)
    return exceldata

@app.route("/gendeletedreport", methods=['GET'])
def gendeletedreport():
    results = formatDeletedData()
    getdate = datetime.now()
    date = getdate.strftime("%b_%d_%Y")
    filename = 'DeletedObjects_' + date
    exceldata = excel.make_response_from_array(results, "csv", file_name=filename)
    return exceldata
