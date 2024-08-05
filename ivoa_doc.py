###########################################
##### IVOA Document Submission Script #####
###########################################

import os
import flask
import pathlib
from forms import InfoForm, ErrataForm, MoreInfo, RFCForm, DelForm
from flask import (Flask,render_template, url_for, redirect,
                    flash, request, abort, send_from_directory, send_file,
                    current_app, session, json)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug import FileStorage
from datetime import datetime
from flask_bootstrap import Bootstrap
from sqlalchemy import desc
import zipfile, tarfile
from tarfile import TarFile
from werkzeug.security import safe_join
from werkzeug.datastructures import MultiDict

app = Flask(__name__)

# The UPLOAD_DIR folder contains all the .zip and .tar files that are uploaded by the app. 
# The uploaded .zip or .tar files are first saved in this folder. It can also be used as a backup of the uploaded documents
UPLOAD_DIR = '/var/www/html/docrepo/uploads'

# The 'documents' folder has the extracted files from the 'uploads'. 
# This is the main repository where the documents will be saved.
documents = '/var/www/html/docrepo/documents'

app.config['SECRET_KEY'] = 'mysecretkey' 
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.zip','.tar']
app.config['UPLOAD_DIR'] = UPLOAD_DIR



################################
##### SQL DATABASE SECTION #####
################################


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)


###################################
###### Table/ Model in SQL ########
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
    extra_description = db.Column(db.Text)
    available_formats = db.Column(db.Text)
    ### One to one relationship between Ivoa and DOI, Bibcode and RFC Link
    doi_bibcode = db.relationship('DOI_Bibcode', backref='ivoa', uselist=False)
    rfc_link = db.relationship('RFC_link', backref='ivoa', uselist=False)
    ### One to many relationship between Ivoa and erratas
    errata = db.relationship('Errata',backref='ivoa',lazy='dynamic')


    def __init__(self,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats):
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
        self.extra_description = extra_description
        self.available_formats = available_formats

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
    erratum_status = db.Column(db.Text)

    def __init__(self,erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,ivoa_docname,erratum_status):

        self.erratum_number = erratum_number
        self.erratum_title = erratum_title
        self.erratum_author = erratum_author
        self.erratum_date = erratum_date
        self.erratum_accepted_date = erratum_accepted_date
        self.erratum_link = erratum_link
        self.ivoa_docname = ivoa_docname
        self.erratum_status = erratum_status



#################################
###### VIEW FUNCTIONS ###########
#################################

@app.route('/')
@app.route("/documents/")
def index():
    ivoa_db = Ivoa.query.all()

    SAMP_st = Ivoa.query.filter_by(concise_name='SAMP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SAMP_ip = Ivoa.query.filter_by(concise_name='SAMP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    VOTable_st = Ivoa.query.filter_by(concise_name='VOTable', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    VOTable_ip = Ivoa.query.filter_by(concise_name='VOTable').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    MOC_st = Ivoa.query.filter_by(concise_name='MOC', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    MOC_ip = Ivoa.query.filter_by(concise_name='MOC').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    HiPS_st = Ivoa.query.filter_by(concise_name='HiPS', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    HiPS_ip = Ivoa.query.filter_by(concise_name='HiPS').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    DALI_st = Ivoa.query.filter_by(concise_name='DALI', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    DALI_ip = Ivoa.query.filter_by(concise_name='DALI').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    DataLink_st = Ivoa.query.filter_by(concise_name='DataLink', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    DataLink_ip = Ivoa.query.filter_by(concise_name='DataLink').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    ConeSearch_st = Ivoa.query.filter_by(concise_name='ConeSearch', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    ConeSearch_ip = Ivoa.query.filter_by(concise_name='ConeSearch').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    SIA_st = Ivoa.query.filter_by(concise_name='SIA', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SIA_ip = Ivoa.query.filter_by(concise_name='SIA').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    SLAP_st = Ivoa.query.filter_by(concise_name='SLAP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SLAP_ip = Ivoa.query.filter_by(concise_name='SLAP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    SSA_st = Ivoa.query.filter_by(concise_name='SSA', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SSA_ip = Ivoa.query.filter_by(concise_name='SSA').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    STC_S_st = Ivoa.query.filter_by(concise_name='STC-S', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    STC_S_ip = Ivoa.query.filter_by(concise_name='STC-S').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    TAP_st = Ivoa.query.filter_by(concise_name='TAP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    TAP_ip = Ivoa.query.filter_by(concise_name='TAP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    TAPRegExt_st = Ivoa.query.filter_by(concise_name='TAPRegExt', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    TAPRegExt_ip = Ivoa.query.filter_by(concise_name='TAPRegExt').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    ADQL_st = Ivoa.query.filter_by(concise_name='ADQL', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    ADQL_ip = Ivoa.query.filter_by(concise_name='ADQL').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    SimDAL_st = Ivoa.query.filter_by(concise_name='SimDAL', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SimDAL_ip = Ivoa.query.filter_by(concise_name='SimDAL').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    VOEventTransport_st = Ivoa.query.filter_by(concise_name='VOEventTransport', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    VOEventTransport_ip = Ivoa.query.filter_by(concise_name='VOEventTransport').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    SODA_st = Ivoa.query.filter_by(concise_name='SODA', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    SODA_ip = Ivoa.query.filter_by(concise_name='SODA').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    ObjVisSAP_st = Ivoa.query.filter_by(concise_name='ObjVisSAP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    ObjVisSAP_ip = Ivoa.query.filter_by(concise_name='ObjVisSAP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    EPNTAP_st = Ivoa.query.filter_by(concise_name='EPNTAP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    EPNTAP_ip = Ivoa.query.filter_by(concise_name='EPNTAP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    LineTAP_st = Ivoa.query.filter_by(concise_name='LineTAP', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    LineTAP_ip = Ivoa.query.filter_by(concise_name='LineTAP').order_by(desc(Ivoa.date)).first() # Latest Document In progress

    PHOTDM_st = Ivoa.query.filter_by(concise_name='PHOTDM', status='REC').order_by(desc(Ivoa.date)).first() #Last stable version of the document
    PHOTDM_ip = Ivoa.query.filter_by(concise_name='PHOTDM').order_by(desc(Ivoa.date)).first() # Latest Document In progress


    return render_template('home.html',ivoa_db=ivoa_db, SAMP_st=SAMP_st, SAMP_ip=SAMP_ip, VOTable_st=VOTable_st, VOTable_ip=VOTable_ip, MOC_st=MOC_st,MOC_ip=MOC_ip,HiPS_st=HiPS_st, HiPS_ip=HiPS_ip, DALI_st=DALI_st, DALI_ip=DALI_ip, DataLink_st=DataLink_st, DataLink_ip=DataLink_ip, ConeSearch_st=ConeSearch_st, ConeSearch_ip=ConeSearch_ip,SIA_st=SIA_st, SIA_ip=SIA_ip, SLAP_st=SLAP_st, SLAP_ip=SLAP_ip, SSA_st=SSA_st,SSA_ip=SSA_ip, STC_S_st=STC_S_st, STC_S_ip=STC_S_ip, TAP_st=TAP_st, TAP_ip=TAP_ip,TAPRegExt_st=TAPRegExt_st, TAPRegExt_ip=TAPRegExt_ip, ADQL_st=ADQL_st, ADQL_ip=ADQL_ip, SimDAL_st=SimDAL_st, SimDAL_ip=SimDAL_ip,VOEventTransport_st=VOEventTransport_st,VOEventTransport_ip=VOEventTransport_ip, SODA_st=SODA_st, SODA_ip=SODA_ip, ObjVisSAP_st=ObjVisSAP_st, ObjVisSAP_ip=ObjVisSAP_ip, EPNTAP_st=EPNTAP_st, EPNTAP_ip=EPNTAP_ip,LineTAP_st=LineTAP_st, LineTAP_ip=LineTAP_ip, PHOTDM_st=PHOTDM_st, PHOTDM_ip=PHOTDM_ip)



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
        extra_description = form.extra_description.data
        docname = status+"-"+concise_name.replace(" ", "")+"-"+str(version_major)+"."+str(version_minor)+"-"+(str(date).replace("-", ""))
        package_path = os.getcwd()+'/documents'+'/'+concise_name.replace(" ", "")+'/'+(str(date).replace("-", ""))
        available_formats = form.available_formats.data

        new_entry = Ivoa(group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats)
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('upload_file'))

    return render_template('fill_form.html',form=form)


@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

@app.route('/add_errata/<docname>', methods=['GET', 'POST'])
def add_errata(docname):

    doc_info_1 = Ivoa.query.filter_by(docname=docname).first()

    if request.method == 'GET':
        form = ErrataForm(formdata=MultiDict({'ivoa_docname': doc_info_1.docname}))
    else:
        form = ErrataForm()

    if form.validate_on_submit():
        ivoa_docname = form.ivoa_docname.data
        erratum_number = form.erratum_number.data
        erratum_title = form.erratum_title.data
        erratum_author = form.erratum_author.data
        erratum_date = form.erratum_date.data
        erratum_accepted_date = form.erratum_accepted_date.data
        erratum_link = form.erratum_link.data
        erratum_status = str("") 

        new_erratum = Errata(erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,ivoa_docname,erratum_status)
        db.session.add(new_erratum)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('add_errata.html', form=form, doc_info_1=doc_info_1)

@app.route('/add_more/<docname>', methods=['GET','POST'])
def add_more(docname):

    doc_info_1 = Ivoa.query.filter_by(docname=docname).first()
    doc_info_3 = DOI_Bibcode.query.filter_by(ivoa_docname=docname).first()

    if request.method == 'GET':
        form = MoreInfo(formdata=MultiDict({'ivoa_docname': doc_info_1.docname}))
    else:
        form = MoreInfo()

    if form.validate_on_submit():

        ivoa_docname = form.ivoa_docname.data
        doi = form.doi.data
        bibcode = form.bibcode.data

        moreinfo = DOI_Bibcode(doi,bibcode,ivoa_docname)
        db.session.add(moreinfo)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('add_more.html', form=form,  doc_info_1=doc_info_1, doc_info_3=doc_info_3)

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

@app.route("/documents/<docname>")
def doc_landing(docname):

    doc_info_1 = Ivoa.query.filter_by(docname=docname).first()
    doc_info_2 = Errata.query.filter_by(ivoa_docname=docname).first()
    doc_info_3 = DOI_Bibcode.query.filter_by(ivoa_docname=docname).first()
    doc_info_4 = RFC_link.query.filter_by(ivoa_docname=docname).first()
    return render_template('doc_landing.html', doc_info_1=doc_info_1,doc_info_2=doc_info_2,doc_info_3=doc_info_3,doc_info_4=doc_info_4)


@app.route('/documents/<path:docname>', methods=['GET', 'POST'])
def download(docname):
    documents = '/var/www/html/docrepo/documents'

    return send_from_directory(directory=documents, filename=docname, as_attachment=True)

# Upload the Document

@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        if filename != '':
	#file_ext gives the the extensions of the uploaded file
            file_ext = os.path.splitext(filename)[1]
	# fname is a temparory variable to get the original filename of the the uploaded file using Pathlib's 'stem' function
            fname = pathlib.Path(filename)
            original_filename = fname.stem
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                flash('Please upload a .zip or .tar file')
                return redirect(url_for('upload_file'))
                #abort(400)
            else:
	#file.save saves the uploaded file in the 'UPLOAD_DIR' with the original name of the uploaded file
                file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
                source=UPLOAD_DIR+"/"+filename
                destination=UPLOAD_DIR+"/"+Ivoa.docname+file_ext
                os.rename(source,destination)
	#In the step above the saved '.zip' or '.tar' file is renamed

	# Below the '.zip' or '.tar' files are separated and extracted into the 'documents' directory and the folder is renamed as per IVOA standards
	# After renaming the folder, its contents (files inside) are renamed keeping their extensions constant.
                if file_ext == '.zip':
                    with zipfile.ZipFile(destination, 'r') as zip_ref:
                        zip_ref.extractall(path='/var/www/html/docrepo/documents')
                        src= '/var/www/html/docrepo/documents/'+original_filename
                        dst= '/var/www/html/docrepo/documents/'+Ivoa.docname
                        os.rename(src,dst)
                        for name in os.listdir(dst):
                            extension = os.path.splitext(name)[1]
                            new_dst = dst + '/' + Ivoa.docname + extension
                            new_src = dst + '/' + name
                            os.rename(new_src, new_dst)
                elif file_ext == '.tar':
                    with tarfile.open(destination, 'r') as tar_ref:
                        tar_ref.extractall(path='/var/www/html/docrepo/documents')
                        src= '/var/www/html/docrepo/documents/'+original_filename
                        dst= '/var/www/html/docrepo/documents/'+Ivoa.docname
                        os.rename(src,dst)
                        for name in os.listdir(dst):
                            extension = os.path.splitext(name)[1]
                            new_dst = dst + '/' + Ivoa.docname + extension
                            new_src = dst + '/' + name
                            os.rename(new_src, new_dst)
                else:
                    return redirect(url_for('upload_file'))
                return redirect(url_for('thank_you'))
    return render_template('upload.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete():

    form = DelForm()

    if form.validate_on_submit():

        docname = form.docname.data

        record_ivoa = Ivoa.query.get(docname)
	#record_ivoa = DOI_Bibcode.query.get(docname)
	#record_ivoa = RFC_link.query.get(docname)
	#record_ivoa = Errata.query.get(docname)
	
        db.session.delete(record_ivoa)
        db.session.commit()

        return redirect(url_for('view_db'))
    return render_template('delete.html', form=form)

@app.route('/rec')
def rec():
    
    ivoa_db = Ivoa.query.filter_by(status='REC').all()

    return render_template('rec.html', ivoa_db=ivoa_db)

@app.route('/endorsed_notes')
def endorsed_notes():

    ivoa_db = Ivoa.query.filter_by(status='EN').all()

    return render_template('endorsed_notes.html', ivoa_db=ivoa_db)

@app.route('/note')
def note():

    ivoa_db = Ivoa.query.filter_by(status='Note').all()

    return render_template('note.html', ivoa_db=ivoa_db)


if __name__ == '__main__':
   app.run(debug=True)
