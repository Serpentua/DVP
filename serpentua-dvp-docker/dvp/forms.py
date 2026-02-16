from dvp import app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, TimeField, IntegerField, BooleanField, PasswordField

from wtforms.validators import DataRequired
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_bootstrap import Bootstrap

class AssetGroupForm(FlaskForm):
    name = StringField('Asset Group name', validators=[DataRequired()], render_kw={"class":"form-control rounded", "placeholder": "New Asset Group"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"})

class SearchAssetGroupsForm(FlaskForm):
    searchfield = StringField('Search Asset Group', render_kw={"placeholder": "Search Asset Groups", "class":"form-control rounded"})
    search = SubmitField('Search', render_kw={"class":"btn btn-outline-primary"})

class SearchAssetObjectForm(FlaskForm):
    searchfield = StringField('Search File Name', render_kw={"placeholder": "Search File Name", "class":"form-control rounded"})
    search = SubmitField('Search', render_kw={"class":"btn btn-outline-primary"})

class NewAssetForm(FlaskForm):
    name = StringField('Asset Name', render_kw={"placeholder": "Asset Identifier/Name", "class":"form-control form-control-sm"})
    path = StringField('Full path', render_kw={"class":"form-control form-control-sm", "placeholder": "ex. c:\directory\.. /var/share.."})
    externalAssetID  = StringField('External Identifier', render_kw={"class":"form-control form-control-sm","placeholder": "External Identifier"})
    schedules = SelectField('Schedule', coerce=int,render_kw={"class":"form-select form-select-sm"} )
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"})

class EditAssetForm(FlaskForm):
    name = StringField('Asset Name', render_kw={"placeholder": "Asset Identifier/Name", "class":"form-control form-control-sm"})
    path = StringField('Full path', render_kw={'readonly': True, "class":"form-control form-control-sm", "placeholder": "ex. c:\directory\.. /var/share.."})
    externalAssetID  = StringField('External Identifier', render_kw={"class":"form-control form-control-sm","placeholder": "External Identifier"})
    schedules = SelectField('Schedule', coerce=int,render_kw={"class":"form-select form-select-sm"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)

class addexcludedfiles(FlaskForm):
    name = StringField('File Name', render_kw={"placeholder": "File name or path", "class":"form-control form-control-sm"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)

class editschedule(FlaskForm):
    starttime = TimeField('Start Time', render_kw={"class":"form-control form-control-sm"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)

class editOrganization(FlaskForm):
    orgname = StringField('Organization Name', render_kw={"class":"form-control form-control-sm"})
    orgadd1 = StringField('Address Line 1', render_kw={"class":"form-control form-control-sm"})
    orgadd2 = StringField('Address Line 2', render_kw={"class":"form-control form-control-sm"})
    orgcity = StringField('City', render_kw={"class":"form-control form-control-sm"})
    orgstate = StringField('State', render_kw={"class":"form-control form-control-sm"})
    orgpostal = StringField('Postal', render_kw={"class":"form-control form-control-sm"})
    orgphone = StringField('Phone Number', render_kw={"class":"form-control form-control-sm"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)

class genasobjreportform(FlaskForm):
    objid = IntegerField('Asset Object ID',render_kw={"class":"form-control form-control-sm"})
    submit = SubmitField('Generate', render_kw={"class":"btn-primary btn-sm"},)

class addlicense(FlaskForm):
    licensekey = StringField('License Key', render_kw={"placeholder": "xxxx-xxxx-xxxx-xxxxxx-xxxxxx", "class":"form-control form-control-sm"})
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)

class SMTP(FlaskForm):
    emailserver = StringField('Email Server Address', render_kw={"class":"form-control"})
    port = IntegerField('Port', render_kw={"class":"form-control"})
    username = StringField('Username', render_kw={"class":"form-control form-control-sm"})
    password = PasswordField('Password', render_kw={"class":"form-control form-control-sm"})
    tls = BooleanField('TLS')
    emailEnabled = BooleanField('Enable Email')
    submit = SubmitField('Submit', render_kw={"class":"btn-primary btn-sm"},)