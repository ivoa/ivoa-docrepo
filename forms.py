import re
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, DateField,
                    SelectField, TextAreaField, SubmitField, BooleanField,
                    PasswordField, validators, HiddenField,
                    MultipleFileField)
from wtforms.fields.html5 import DateField,URLField,EmailField
from wtforms_sqlalchemy.fields import QuerySelectField




class InfoForm(FlaskForm):

    status = SelectField(u'Status of the Document',
                        choices =[('WD', 'IVOA Working Draft'),
                                    ('PR', 'IVOA Proposed Recommendation'),
                                    ('REC','IVOA Recommendation'),
                                    ('Note', 'IVOA Note'),
                                    ('PEN', 'IVOA Proposed Endorsed Note'),
                                    ('EN', 'IVOA Endorsed Note'),
                                    ('Other', 'Other')])

    title = SelectField(u'Select Title of the Document',
                            choices = [('Simple Application Messaging Protocol', 'Simple Application Messaging Protocol'),
                                        ('VOTable Format definitions', 'VOTable Format definitions'),
                                        ('HEALPix Multi-Order Coverage Map', 'HEALPix Multi-Order Coverage Map'),
                                        ('Hierarchical Progressive Survey', 'Hierarchical Progressive Survey'),
                                        ('Data Access Layer Interface', 'Data Access Layer Interface'),
                                        ('DataLink', 'DataLink'),
                                        ('Simple Cone Search', 'Simple Cone Search'),
                                        ('Simple Image Access', 'Simple Image Access'),
                                        ('Simple Line Access Protocol', 'Simple Line Access Protocol'),
                                        ('Simple Spectral Access Protocol', 'Simple Spectral Access Protocol'),
                                        ('STC-S: Space-Time Coordinate Metadata Linear String Implementation', 'STC-S: Space-Time Coordinate Metadata Linear String Implementation'),
                                        ('Table Access Protocol', 'Table Access Protocol'),
                                        ('TAPRegExt: A VOResource Schema Extension for Describing TAP Services', 'TAPRegExt: A VOResource Schema Extension for Describing TAP Services'),
                                        ('Astronomical Data Query Language', 'Astronomical Data Query Language'),
                                        ('Simulation Data Access Layer', 'Simulation Data Access Layer'),
                                        ('VOEvent Transport Protocol', 'VOEvent Transport Protocol'),
                                        ('Server-side Operations for Data Access', 'Server-side Operations for Data Access'),
                                        ('Object Visibility Simple Access Protocol', 'Object Visibility Simple Access Protocol'),
                                        ('EPN-TAP: Publishing Solar System Data to the Virtual Observatory', 'EPN-TAP: Publishing Solar System Data to the Virtual Observatory'),
					('LineTAP: IVOA Relational Model for Spectral Lines', 'LineTAP: IVOA Relational Model for Spectral Lines'),
                                        ('Photometry Data Model', 'Photometry Data Model'),
                                        ('Simulation Data Model', 'Simulation Data Model'),
                                        ('Space-Time Coordinate Metadata for the Virtual Observatory', 'Space-Time Coordinate Metadata for the Virtual Observatory'),
                                        ('Data Model for Astronomical Dataset Characterisation', 'Data Model for Astronomical Dataset Characterisation'),
                                        ('Simple Spectral Lines Data Model', 'Simple Spectral Lines Data Model'),
                                        ('Spectral Data Model', 'Spectral Data Model'),
					('Spectrum Data Model', 'Spectrum Data Model'),
                                        ('Observation Data Model Core Components and its Implementation in the Table Access Protocol', 'Observation Data Model Core Components and its Implementation in the Table Access Protocol'),
                                        ('A Consistent Modelling Language for IVOA Data Models', 'A Consistent Modelling Language for IVOA Data Models'),
                                        ('Dataset Metadata Model', 'Dataset Metadata Model'),
                                        ('N-Dimensional Cube Model', 'N-Dimensional Cube Model'),
                                        ('Provenance Data Model', 'Provenance Data Model'),
                                        ('Astronomical Coordinates and Coordinate Systems', 'Astronomical Coordinates and Coordinate Systems'),
                                        ('WCS Transform Model', 'WCS Transform Model'),
                                        ('Astronomical Measurements Model', 'Astronomical Measurements Model'),
                                        ('Observation Locator Table Access Protocol', 'Observation Locator Table Access Protocol'),
					('Model Instances in VOTables','Model Instances in VOTables'),
					('Obscore Extension for Radio data', 'Obscore Extension for Radio data'),
                                        ('Parameter Description Language', 'Parameter Description Language'),
                                        ('Single-Sign-On Profile: Authentication Mechanisms', 'Single-Sign-On Profile: Authentication Mechanisms'),
                                        ('VOSpace', 'VOSpace'),
                                        ('Credential Delegation Protocol', 'Credential Delegation Protocol'),
                                        ('Universal Worker Service', 'Universal Worker Service'),
                                        ('IVOA Support Interfaces', 'IVOA Support Interfaces'),
                                        ('Group Membership Service', 'Group Membership Service'),
                                        ('IVOA Identifiers', 'IVOA Identifiers'),
                                        ('IVOA Registry Interfaces', 'IVOA Registry Interfaces'),
                                        ('Resource Metadata for the Virtual Observatory', 'Resource Metadata for the Virtual Observatory'),
                                        ('A VOResource Schema Extension for Describing IVOA Standards', 'A VOResource Schema Extension for Describing IVOA Standards'),
                                        ('Describing Simple Data Access Services', 'Describing Simple Data Access Services'),
                                        ('An XML Encoding Schema for Resource Metadata', 'An XML Encoding Schema for Resource Metadata'),
                                        ('A VOResource Schema Extension for Describing Collections and Services', 'A VOResource Schema Extension for Describing Collections and Services'),
                                        ('Registry Relational Schema', 'Registry Relational Schema'),
                                        ('Educational Resources in the Virtual Observatory','Educational Resources in the Virtual Observatory'),
                                        ('Units in the VO', 'Units in the VO'),
                                        ('An IVOA Standard for Unified Content Descriptors', 'An IVOA Standard for Unified Content Descriptors'),
                                        ('UCD1+ controlled vocabulary - Updated List of Terms', 'UCD1+ controlled vocabulary - Updated List of Terms'),
                                        ('UCD1+ Controlled Vocabulary', 'UCD1+ Controlled Vocabulary'),
                                        ('Maintenance of the list of UCD words', 'Maintenance of the list of UCD words'),
                                        ('Vocabularies in the Virtual Observatory', 'Vocabularies in the Virtual Observatory'),
                                        ('IVOA Document Standards', 'IVOA Document Standards'),
                                        ('Sky Event Reporting Metadata (VOEvent)', 'Sky Event Reporting Metadata (VOEvent)'),
                                        ('An XML Encoding Schema for Resource Metadata for Collections of Events', 'An XML Encoding Schema for Resource Metadata for Collections of Events'),
                                        ('Other', 'Other')])

    new_title = StringField('Enter a new title')
    concise_name = SelectField(u'Concise Name',
                                choices =[('SAMP','SAMP'),('VOTable','VOTable'),('MOC','MOC'),('HiPS','HiPS'),
                                            ('DALI','DALI'),('DataLink','DataLink'),('ConeSearch','ConeSearch'),('SIA','SIA'),
                                            ('SLAP','SLAP'),('SSA','SSA'),('STC-S','STC-S'),('TAP','TAP'),('TAPRegExt','TAPRegExt'),
                                            ('ADQL','ADQL'),('SimDAL','SimDAL'),('VOEventTransport','VOEventTransport'),('SODA','SODA'),
                                            ('ObjVisSAP','ObjVisSAP'),('EPNTAP','EPNTAP'),('LineTAP', 'LineTAP'),
                                            ('PHOTDM','PHOTDM'),('SimDM','SimDM'),('STC','STC'),
                                            ('CharacterisationDM','CharacterisationDM'),('SSLDM','SSLDM'),('SpectralDM','SpectralDM'),('SpectrumDM', 'SpectrumDM'),('ObsCore','ObsCore'),
                                            ('VODML','VODML'),('DatasetDM','DatasetDM'),('CubeDM','CubeDM'),('ProvenanceDM','ProvenanceDM'),('Coords','Coords'),
                                            ('WCSTrans','WCSTrans'),('Meas','Meas'),('ObsLocTAP','ObsLocTAP'),('MIVOT','MIVOT'),('ObsCoreExtensionForRadioData','ObsCoreExtensionForRadioData'),
                                            ('PDL','PDL'),('SSO','SSO'),('VOSpace','VOSpace'),('CredentialDelegation','CredentialDelegation'),
                                            ('UWS','UWS'),('VOSI','VOSI'),('GMS','GMS'),
                                            ('IVOAIdentifiers','IVOAIdentifiers'),('RegistryInterface','RegistryInterface'),('RM','RM'),
                                            ('StandardsRegExt','StandardsRegExt'),('SimpleDALRegExt','SimpleDALRegExt'),('VOResource','VOResource'),('VODataService','VODataService'),
                                            ('RegTAP','RegTAP'),
                                            ('VOUnits','VOUnits'),('UCD','UCD'),('UCD1+','UCD1+'),('UCDlist','UCDlist'),('UCDlistMaintenance','UCDlistMaintenance'),('Vocabularies','Vocabularies'),
                                            ('DocStd','DocStd'),
                                            ('VOEvent','VOEvent'),('VOEventRegExt','VOEventRegExt'),
                                            ('Other','Other')])
    new_consice_name = StringField('Enter a new concise name')
    version_major = SelectField(
                                choices =[('0','0'),('1','1'),('2','2'),
                                        ('3','3'),('4','4'),('5','5'),
                                        ('6','6'),('7','7'), ('8','8'),('9','9')])

    version_minor = SelectField(
                                choices =[('0','0'),('1','1'),('2','2'),
                                        ('3','3'),('4','4'),('5','5'),
                                        ('6','6'),('7','7'), ('8','8'),('9','9')])
    date = DateField('Document Date',format="%Y-%m-%d")

    authors = StringField('Author(s)')
    editors = StringField('Editor(s)')
    group_name = SelectField('Responsible I/W Group:',
                            choices=[('Applications', 'Applications'),('Data Access Layer', 'Data Access Layer'),
                                    ('Data Modelling', 'Data Modelling'), ('Grid & Web Services', 'Grid & Web Services'),
                                    ('Resource Registry', 'Resource Registry'), ('Data Curation & Prevention IG', 'Data Curation & Prevention IG'),
                                    ('Standard & Document Process', 'Standard & Document Process'), ('Semantics', 'Semantics'),
                                    ('Document Standards','Document Standards'),('Theory', 'Theory'), ('VO Event', 'VO Event'),
                                    ('VO table', 'VO Table'), ('VO Query Language', 'VO Query Language')])
    abstract = TextAreaField('Abstract')
    extra_description = URLField('Any Extra Description', [validators.Optional()])
    email = EmailField('Contact Email')
    file = MultipleFileField('Upload File')
    available_formats = StringField('available_formats', [validators.Optional()])
    comment = TextAreaField('Comments', [validators.Optional()])
    submit = SubmitField('Submit')



class ErrataForm(FlaskForm):
    ivoa_docname = StringField('Name of the Document')
    erratum_number = IntegerField('Erratum Number')
    erratum_title = StringField('Title of the Erratum')
    erratum_author = StringField('Author')
    erratum_date = DateField('Date last changed')
    erratum_accepted_date = DateField('Date of erratum accepted')
    erratum_link = URLField('Erratum Link')
    submit = SubmitField("Submit")

class MoreInfo(FlaskForm):

    ivoa_docname = StringField('Name of the Document(Recommendation)')
    doi = StringField('DOI')
    bibcode = StringField('Bibcode')
    submit = SubmitField("Submit")

class RFCForm(FlaskForm):

    ivoa_docname = StringField('Name of the Document(Proposed Recommendation)')
    rfc_link = URLField('Please enter the RFC link if applicable')
    submit = SubmitField("Submit")

class DelForm(FlaskForm):

    docname = StringField("Name of the document to be deleted: ")
    submit = SubmitField("Delete")

