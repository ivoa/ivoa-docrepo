##### IVOA Document Submission Script
import os
import flask
import pathlib
from forms import InfoForm, ErrataForm, MoreInfo, RFCForm
from flask import (Flask, render_template, url_for, redirect,
                    flash, request, abort, send_from_directory, send_file,
                    current_app, session, json)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug import FileStorage
from datetime import datetime
from flask_bootstrap import Bootstrap
from sqlalchemy import desc
import zipfile
from tarfile import TarFile

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.zip','.tar']
app.config['UPLOAD_DIR'] = 'documents'

UPLOAD_DIR = 'documents'


#############################################
##### SQL DATABASE SECTION ######
#############################################


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)


###################################
###### Table/ Model in SQL ###############
###################################

class Ivoa(db.Model):
    docname =str()

    __tablename__ = 'IVOA'

    id = db.Column(db.Integer)
    group_name = db.Column(db.Text)
    title = db.Column(db.Text)
    concise_name = db.Column(db.Text)
    version_major = db.Column(db.Integer)
    version_minor = db.Column(db.Integer)
    status = db.Column(db.Text)
    date = db.Column(db.Integer, default=datetime.utcnow)
    authors = db.Column(db.Text)
    editors = db.Column(db.Text)
    abstract = db.Column(db.Text)
    docname = db.Column(db.Text, primary_key=True, unique=True)
    package_path = db.Column(db.Text)
    email = db.Column(db.Text)
    comment = db.Column(db.Text)
    contribute = db.Column(db.Text)
    ### One to one relationship between Ivoa and DOI, Bibcode and RFC Link
    doi_bibcode = db.relationship('DOI_Bibcode', backref='ivoa', uselist=False)
    rfc_link = db.relationship('RFC_link', backref='ivoa', uselist=False)
    ### One to many relationship between Ivoa and erratas
    errata = db.relationship('Errata',backref='ivoa',lazy='dynamic')


    def __init__(self,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,contribute):
        self.group_name = group_name
        self.title = title
        self.concise_name = concise_name
        self.version_major = version_major
        self.version_minor = version_minor
        self.status = status
        self.date = date
        self.authors = authors
        self.editors = editors
        self.abstract = abstract
        self.docname = docname
        self.package_path = package_path
        Ivoa.docname = status+"-"+concise_name.replace(" ", "")+"-"+str(version_major)+"."+str(version_minor)+"-"+(str(date).replace("-", ""))
        Ivoa.package_path = os.getcwd()+'/documents'+'/'+concise_name.replace(" ", "")+'/'+(str(date).replace("-", ""))
        self.email = email
        self.comment = comment
        self.contribute = contribute


class DOI_Bibcode(db.Model):

    __tablename__ = 'doi_bibcode'

    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.Text)
    bibcode = db.Column(db.Text)
    ivoa_docname = db.Column(db.Text, db.ForeignKey('IVOA.docname'))

    def __init__(self,doi,bibcode,ivoa_docname):
        self.doi = doi
        self.bibcode = bibcode
        self.ivoa_docname = ivoa_docname

class RFC_link(db.Model):

    __tablename__ = 'rfc_link'

    id = db.Column(db.Integer, primary_key=True)
    rfc_link = db.Column(db.Text)
    ivoa_docname = db.Column(db.Text,db.ForeignKey('IVOA.docname'))

    def __init__(self,rfc_link,ivoa_docname):
        self.rfc_link = rfc_link
        self.docname = ivoa_docname


class Errata(db.Model):
    __tablename__ = 'Errata'

    erratum_id = db.Column(db.Integer,primary_key=True)
    erratum_number = db.Column(db.Integer)
    erratum_title = db.Column(db.Text)
    erratum_author = db.Column(db.Text)
    erratum_date = db.Column(db.Integer)
    erratum_accepted_date = db.Column(db.Integer)
    erratum_link = db.Column(db.Integer)
    ivoa_docname = db.Column(db.Text,db.ForeignKey('IVOA.docname'))

    def __init__(self,erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,ivoa_docname):

        self.erratum_number = erratum_number
        self.erratum_title = erratum_title
        self.erratum_author = erratum_author
        self.erratum_date = erratum_date
        self.erratum_accepted_date = erratum_accepted_date
        self.erratum_link = erratum_link
        self.ivoa_docname = ivoa_docname



#################################
###### VIEW FUNCTIONS ###########
#################################
@app.route("/documents/")
@app.route('/')
def index():
    SAMP = Ivoa.query.filter_by(group_name='Applications',status='REC',concise_name='SAMP').order_by(desc(Ivoa.date)).limit(1).all()
    VOTable = Ivoa.query.filter_by(group_name='Applications',status='REC',concise_name='VOTable').order_by(desc(Ivoa.date)).limit(1).all()
    MOC = Ivoa.query.filter_by(group_name='Applications',status='REC',concise_name='MOC').order_by(desc(Ivoa.date)).limit(1).all()
    HiPS = Ivoa.query.filter_by(group_name='Applications',status='REC',concise_name='HiPS').order_by(desc(Ivoa.date)).limit(1).all()

    DALI = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='DALI').order_by(desc(Ivoa.date)).limit(1).all()
    DataLink = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='DataLink').order_by(desc(Ivoa.date)).limit(1).all()
    ConeSearch = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='ConeSearch').order_by(desc(Ivoa.date)).limit(1).all()
    SIA = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='SIA').order_by(desc(Ivoa.date)).limit(1).all()
    SLAP = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='SLAP').order_by(desc(Ivoa.date)).limit(1).all()
    SSA = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='SSA').order_by(desc(Ivoa.date)).limit(1).all()
    STC_S = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='STC-S').order_by(desc(Ivoa.date)).limit(1).all()
    TAP = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='TAP').order_by(desc(Ivoa.date)).limit(1).all()
    TAPRegExt = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='TAPRegExt').order_by(desc(Ivoa.date)).limit(1).all()
    ADQL = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='ADQL').order_by(desc(Ivoa.date)).limit(1).all()
    SimDAL = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='SimDAL').order_by(desc(Ivoa.date)).limit(1).all()
    VOEventTransport = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='VOEventTransport').order_by(desc(Ivoa.date)).limit(1).all()
    SODA = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='SODA').order_by(desc(Ivoa.date)).limit(1).all()
    ObjVisSAP = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='ObjVisSAP').order_by(desc(Ivoa.date)).limit(1).all()
    EPNTAP = Ivoa.query.filter_by(group_name='Data Access Layer',status='REC',concise_name='EPNTAP').order_by(desc(Ivoa.date)).limit(1).all()

    PHOTDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='PHOTDM').order_by(desc(Ivoa.date)).limit(1).all()
    SimDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='SimDM').order_by(desc(Ivoa.date)).limit(1).all()
    STC = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='STC').order_by(desc(Ivoa.date)).limit(1).all()
    CharacterisationDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='CharacterisationDM').order_by(desc(Ivoa.date)).limit(1).all()
    SSLDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='SSLDM').order_by(desc(Ivoa.date)).limit(1).all()
    SpectralDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='SpectralDM').order_by(desc(Ivoa.date)).limit(1).all()
    ObsCore = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='ObsCore').order_by(desc(Ivoa.date)).limit(1).all()
    VODML = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='VODML').order_by(desc(Ivoa.date)).limit(1).all()
    DatasetDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='DatasetDM').order_by(desc(Ivoa.date)).limit(1).all()
    CubeDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='CubeDM').order_by(desc(Ivoa.date)).limit(1).all()
    ProvenanceDM = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='ProvenanceDM').order_by(desc(Ivoa.date)).limit(1).all()
    Coords = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='Coords').order_by(desc(Ivoa.date)).limit(1).all()
    WCSTrans = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='WCSTrans').order_by(desc(Ivoa.date)).limit(1).all()
    Meas = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='Meas').order_by(desc(Ivoa.date)).limit(1).all()
    ObsLocTAP = Ivoa.query.filter_by(group_name='Data Modelling',status='REC',concise_name='ObsLocTAP').order_by(desc(Ivoa.date)).limit(1).all()

    PDL = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='PDL').order_by(desc(Ivoa.date)).limit(1).all()
    SSO = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='SSO').order_by(desc(Ivoa.date)).limit(1).all()
    VOSpace = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='VOSpace').order_by(desc(Ivoa.date)).limit(1).all()
    CredentialDelegation = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='CredentialDelegation').order_by(desc(Ivoa.date)).limit(1).all()
    UWS = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='UWS').order_by(desc(Ivoa.date)).limit(1).all()
    VOSI = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='VOSI').order_by(desc(Ivoa.date)).limit(1).all()
    GMS = Ivoa.query.filter_by(group_name='Grid & Web Services',status='REC',concise_name='GMS').order_by(desc(Ivoa.date)).limit(1).all()

    IVOAIdentifiers = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='IVOAIdentifiers').order_by(desc(Ivoa.date)).limit(1).all()
    RegistryInterface = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='RegistryInterface').order_by(desc(Ivoa.date)).limit(1).all()
    RM = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='RM').order_by(desc(Ivoa.date)).limit(1).all()
    StandardsRegExt = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='StandardsRegExt').order_by(desc(Ivoa.date)).limit(1).all()
    SimpleDALRegExt = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='SimpleDALRegExt').order_by(desc(Ivoa.date)).limit(1).all()
    VOResource = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='VOResource').order_by(desc(Ivoa.date)).limit(1).all()
    VODataService = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='VODataService').order_by(desc(Ivoa.date)).limit(1).all()
    RegTAP = Ivoa.query.filter_by(group_name='Resource Registry',status='REC',concise_name='RegTAP').order_by(desc(Ivoa.date)).limit(1).all()

    DataCurationandPreventionIG = Ivoa.query.filter_by(group_name='Data Curation & Prevention IG',status='REC').order_by(desc(Ivoa.date)).limit(1).all()
    StandardandDocumentProcess = Ivoa.query.filter_by(group_name='Standard & Document Process',status='REC').order_by(desc(Ivoa.date)).limit(1).all()

    VOUnits = Ivoa.query.filter_by(group_name='Semantics',status='REC',concise_name='VOUnits').order_by(desc(Ivoa.date)).limit(1).all()
    UCD = Ivoa.query.filter_by(group_name='Semantics',status='REC',concise_name='UCD').order_by(desc(Ivoa.date)).limit(1).all()
    UCD1plus = Ivoa.query.filter_by(group_name='Semantics',status='REC',concise_name='UCD1+').order_by(desc(Ivoa.date)).limit(1).all()
    UCDlistMaintenance = Ivoa.query.filter_by(group_name='Semantics',status='REC',concise_name='UCDlistMaintenance').order_by(desc(Ivoa.date)).limit(1).all()
    Vocabularies = Ivoa.query.filter_by(group_name='Semantics',status='REC',concise_name='Vocabularies').order_by(desc(Ivoa.date)).limit(1).all()

    DocStd = Ivoa.query.filter_by(group_name='Document Standards',status='REC',concise_name="DocStd").order_by(desc(Ivoa.date)).limit(1).all()

    Theory_rec = Ivoa.query.filter_by(group_name='Theory',status='REC').order_by(desc(Ivoa.date)).limit(1).all()

    VOEvent = Ivoa.query.filter_by(group_name='VO Event',status='REC',concise_name='VOEvent').order_by(desc(Ivoa.date)).limit(1).all()
    VOEventRegExt = Ivoa.query.filter_by(group_name='VO Event',status='REC',concise_name='VOEventRegExt').order_by(desc(Ivoa.date)).limit(1).all()

    VOTable_rec = Ivoa.query.filter_by(group_name='VO table',status='REC').order_by(desc(Ivoa.date)).limit(1).all()

    VOQueryLanguage_rec = Ivoa.query.filter_by(group_name='VO Query Language',status='REC').order_by(desc(Ivoa.date)).limit(1).all()

    ivoa_db = Ivoa.query.all()

    #rec_only = Ivoa.query.filter_by(status='REC').all()
    return render_template('home.html', SAMP=SAMP, VOTable=VOTable, MOC=MOC, HiPS=HiPS, DALI=DALI, DataLink=DataLink, ConeSearch=ConeSearch, SIA=SIA,
                SLAP=SLAP, SSA=SSA, STC_S=STC_S, TAP=TAP, TAPRegExt=TAPRegExt, ADQL=ADQL, SimDAL=SimDAL, VOEventTransport=VOEventTransport, SODA=SODA,
                ObjVisSAP=ObjVisSAP, EPNTAP=EPNTAP, PHOTDM=PHOTDM, SimDM=SimDM, STC=STC, CharacterisationDM=CharacterisationDM,
                SSLDM=SSLDM, SpectralDM=SpectralDM, ObsCore=ObsCore, VODML=VODML, DatasetDM=DatasetDM, CubeDM=CubeDM, ProvenanceDM=ProvenanceDM,
                Coords=Coords, WCSTrans=WCSTrans, Meas=Meas, ObsLocTAP=ObsLocTAP, PDL=PDL, SSO=SSO, VOSpace=VOSpace, CredentialDelegation=CredentialDelegation,
                UWS=UWS, VOSI=VOSI, GMS=GMS, IVOAIdentifiers=IVOAIdentifiers, RegistryInterface=RegistryInterface, RM=RM, StandardsRegExt=StandardsRegExt,
                SimpleDALRegExt=SimpleDALRegExt, VOResource=VOResource, VODataService=VODataService, RegTAP=RegTAP, VOUnits=VOUnits, UCD=UCD,
                UCD1plus=UCD1plus, UCDlistMaintenance=UCDlistMaintenance, Vocabularies=Vocabularies, DocStd=DocStd, VOEvent=VOEvent, VOEventRegExt=VOEventRegExt,
                VOQueryLanguage_rec=VOQueryLanguage_rec, VOTable_rec=VOTable_rec, Theory_rec=Theory_rec, DataCurationandPreventionIG=DataCurationandPreventionIG,
                StandardandDocumentProcess=StandardandDocumentProcess, ivoa_db=ivoa_db)

    # rec_only = Ivoa.query.filter_by(status='REC').all()
    # return render_template('home.html', rec_only=rec_only)


@app.route('/new_doc', methods=['GET','POST'])
def fill_form():

    form = InfoForm()

    if form.validate_on_submit():

        title = form.title.data
        concise_name = form.concise_name.data
        version_major = form.version_major.data
        version_minor = form.version_minor.data
        date = form.date.data
        status = form.status.data
        authors = form.authors.data
        editors = form.editors.data
        group_name = form.group_name.data
        abstract = form.abstract.data
        email = form.email.data
        comment = form.comment.data
        contribute = form.contribute.data
        docname = status+"-"+concise_name.replace(" ", "")+"-"+str(version_major)+"."+str(version_minor)+"-"+(str(date).replace("-", ""))
        package_path = os.getcwd()+'/documents'+'/'+concise_name.replace(" ", "")+'/'+(str(date).replace("-", ""))


        new_entry = Ivoa(group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,contribute)
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('upload_file'))

    return render_template('fill_form.html',form=form)


@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

@app.route('/add_errata', methods=['GET', 'POST'])
def add_errata():

    form = ErrataForm()

    if form.validate_on_submit():
        ivoa_docname = form.ivoa_docname.data
        erratum_number = form.erratum_number.data
        erratum_title = form.erratum_title.data
        erratum_author = form.erratum_author.data
        erratum_date = form.erratum_date.data
        erratum_accepted_date = form.erratum_accepted_date.data
        erratum_link = form.erratum_link.data

        new_erratum = Errata(erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,ivoa_docname)
        db.session.add(new_erratum)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('add_errata.html', form=form)


@app.route('/add_more', methods=['GET','POST'])
def add_more():

    form = MoreInfo()
    rec = Ivoa.query.filter_by(status='REC').all()

    if form.validate_on_submit():

        ivoa_docname = form.ivoa_docname.data
        doi = form.doi.data
        bibcode = form.bibcode.data

        moreinfo = DOI_Bibcode(doi,bibcode,ivoa_docname)
        db.session.add(moreinfo)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('add_more.html', form=form)

@app.route('/add_rfc', methods=['GET','POST'])
def rfc():

    form = RFCForm()

    if form.validate_on_submit():
        ivoa_docname = form.ivoa_docname.data
        rfc_link = form.rfc_link.data

        rfc = RFC_link(rfc_link,ivoa_docname)
        db.session.add(rfc)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('add_rfc.html', form=form)


@app.route('/view_db')
def view_db():
    #ivoa_db = Ivoa.query.filter_by(status='REC').all()
    #To view fill list
    ivoa_db = Ivoa.query.all()
    doi_bibcode_db = DOI_Bibcode.query.all()
    rfc_link_db = RFC_link.query.all()
    errata_db = Errata.query.all()
    return render_template('view_db.html', ivoa_db=ivoa_db)

@app.route("/documents/<concise_name>/<date>/<docname>")
def doc_landing(docname,concise_name,date):

    doc_info_1 = Ivoa.query.filter_by(docname=docname).first()
    doc_info_2 = Errata.query.filter_by(ivoa_docname=docname).first()
    doc_info_3 = DOI_Bibcode.query.filter_by(ivoa_docname=docname).first()
    doc_info_4 = RFC_link.query.filter_by(ivoa_docname=docname).first()
    return render_template('doc_landing.html', doc_info_1=doc_info_1,doc_info_2=doc_info_2,doc_info_3=doc_info_3,doc_info_4=doc_info_4,concise_name=concise_name, date=date)


@app.route('/download/<docname>', methods=['GET', 'POST'])
def download(docname):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_DIR'])
    # Returning file from appended path
    return send_from_directory(directory=uploads, filename=docname, as_attachment=True)

# Upload API
@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['docfile']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            for files in uploaded_file:
                uploaded_file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
                source=UPLOAD_DIR+"/"+filename
                destination=UPLOAD_DIR+"/"+Ivoa.docname+file_ext
                #print(destination)
                os.rename(source,destination)
                return redirect(url_for('thank_you'))

            #return redirect('/download_file/'+filename)
    return render_template('upload.html')



if __name__ == '__main__':
    app.run(debug=True)

