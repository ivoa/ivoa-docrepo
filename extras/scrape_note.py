#############################################################################
###### This is the file for scraping EN , PEN and Notes #####################
######## few lines of the code have been changed from scrape.py #############
#############################################################################


import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import sqlite3

######################################################
#### The URL to be scraped ###########################

id = '690'

print("id:",id)

link = "https://www.ivoa.net/documents/latest/rmexp.html"

page = requests.get(link)
soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find()

######################################################
###### Scrape Concise Name of the Documents ##########
######################################################
link_parts = link.split('/')

documents_index = link_parts.index('documents')

if link_parts[documents_index + 1] == 'Notes':
    concise_name_index = documents_index + 2
    concise_name = link_parts[concise_name_index]
    print("concise_name:",concise_name)
elif link_parts[documents_index + 1] == 'notes':
    concise_name_index = documents_index + 2
    concise_name = link_parts[concise_name_index]
    print("concise_name:",concise_name)
elif link_parts[documents_index + 1] == 'latest':
    concise_name_index = documents_index + 2
    concise_name = link_parts[concise_name_index].split('.')[0]
    print("concise_name:",concise_name)
elif link_parts[documents_index + 1] == 'cover':
    concise_name_index = documents_index + 2
    concise_name = link_parts[concise_name_index].split('-')[0]
    print("concise_name:",concise_name)
else:
     concise_name_index = documents_index + 1
     concise_name = link_parts[concise_name_index]
     print("concise_name:",concise_name)


#######################################################
###### Scrape the Title of the Documents ##############
#######################################################
all_content = results.find("div", class_="head")
h1 = results.find("h1")
h1_text = h1.text.strip()
title = h1_text.rsplit('Version', 2)[0]
print("Title:", title)


#######################################################
###### Scrape the Versions of the Documents ###########
#######################################################

version_minor = h1_text.split('.')[-1]
temp = h1_text.split('.')[0]
version_major = temp.split(' ')[-1]
print ("Version:", version_major+'.'+version_minor )

##################################################

##############################################
h2 = results.find("h2")
h2_text = h2.text.strip()
split_h2_text = h2_text.split()

if split_h2_text[1] == 'Recommendation':
    status = 'REC'
    print('Status:', status)
elif split_h2_text[1] == 'Proposed' and split_h2_text[2] == 'Recommendation':
    status = 'PR'
    print('Status:', status)
elif split_h2_text[1] == 'Working' and split_h2_text[2] == 'Draft':
    status = 'WD'
    print('Status:', status)
elif split_h2_text[1] == 'Endorsed' and split_h2_text[2] == 'Note':
    status = 'EN'
    print('Status:', status)
elif split_h2_text[1] == 'Proposed' and split_h2_text[2] == 'Endorsed' and split_h2_text[3] == 'Note':
    status = 'PEN'
    print('Status:', status)
elif split_h2_text[1] == 'Note':
    status = 'Note'
    print('Status:', status)
else:
    print("Status Error")

################################################################################################
split_h2_text = h2_text.split()
day = h2_text.split()[-3]
month = h2_text.split()[-2]
year = h2_text.split()[-1]
date_string = year + " " + month + " " + day
date_obj = datetime.strptime(date_string, "%Y %B %d")
date = date_obj.strftime("%Y-%m-%d")

print("Date:", date)

####################################################
dd = results.find('dd')
input_string = str(dd)
url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

urls = re.findall(url_pattern, input_string)

if urls == list():
    group_name = "Not Applicable"
else:
    group_name = urls[0]
    for url in urls:
        group_name = url
        break
print("Group_name", group_name)
#####################################################################################

def find_element(soup, tag, text):
	for element in soup.findAll(tag):
		if text in element.text:
			return element

authors = find_element(soup, "dt", "Author(s):").find_next_sibling("dd").getText()
print( "Authors:" ,authors)

editors = find_element(soup, "dt", "Editor(s):").find_next_sibling("dd").getText()
print( "Editors:", editors)

check_doi = find_element(soup, "dt", "DOI:")
if find_element(soup, "dt", "DOI:") is None:
    doi = ''
    bibcode = ''
    print("No DOI found and Bibcode found")
else:
    doi = find_element(soup, "dt", "DOI:").find_next_sibling("dd").getText()
    print("DOI:", doi)
    bibcode = doi.split('/')[-1]
    print("Bibcode:", bibcode)

#####################################################################################
check_errata = find_element(soup, "h2", "Errata")
if find_element(soup, "h2", "Errata") is None:
    erratum_number = ''
    erratum_accepted_date = ''
    erratum_link = ''
    erratum_status = ""
    print("No Errata found")
elif find_element(soup, "h2", "Errata").find_next_sibling("p").getText() == 'No errata yet':
    erratum_number = ''
    erratum_accepted_date = ''
    erratum_link = ''
    erratum_status = ""
    print("No Errata found, just empty link")
else:
    errata_line = find_element(soup, "h2", "Errata").find_next_sibling("p")
    errata_str = str(errata_line)
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    erratas_list = re.findall(url_pattern, errata_str)
    for erratum_link in erratas_list:
        print("erratum_link:", erratum_link)
    if  erratum_link != '':
        Errata_details = find_element(soup, "h2", "Errata").find_next_sibling("p").getText()
        erratum_number = Errata_details.split(" ")[0]
        erratum_accepted_date = Errata_details.split(" ")[-1].replace(')', '')
        erratum_status = "Accepted"
        print("Errata_number", erratum_number)
        print("Errata_accepted", erratum_accepted_date)
    else:
        erratum_number = ''
        erratum_accepted_date = ''
erratum_id = ""
erratum_title = ""
erratum_author = ""
erratum_date = ""

##############################################################################################

abs = soup.find('h2', text=lambda t: t and "abstract" in t.lower())
abstract = abs.find_next_sibling(string=True)
if abstract is None:
    print("No Abstract Found")
else:
    print("Abstract:", abstract.strip())
###############################################################################################

formats = results.find("div", class_="documentfile")

format = formats.find_all('a', href=True)

file_names = [f"{tag['href']}" for tag in format]

available_formats = ", ".join(file_names)
print("Available formats:", available_formats)

############################################################################################
last_element_of_available_format = available_formats.split(' ')[-1]

all_a_tags = soup.find_all("a") # Find all elements with the tag <a>
if len(all_a_tags) >= 2:
    a_tag = all_a_tags[-2]
    #print(a_tag['href'])
    if a_tag['href'] == last_element_of_available_format:
        print("No extra description found")
        extra_description = "No contribution available"
    else:
        extra_description = a_tag['href']
        print("extra:",extra_description)

############################################################################################

docname = status + "-" + concise_name.replace(" ", "")+"-"+str(version_major)+"."+str(version_minor)+"-"+(str(date).replace("-", ""))
ivoa_docname = docname
print("docname:", docname)

#####################################################################################################
package_path = '/var/www/html/docrepo/documents/'+docname
print("package_path" ,package_path)

email = 'kalyani.pedamkar@inaf.it'
print("Email:", email)

comment = "No comments available"
print( "Comment" ,comment)

contribute = 'No contribution available'
print("contribute", contribute)

rfc_link = ""
print("rfc_link:", rfc_link)
#############################################################################################
############# Create the database ###########################################################
#############################################################################################

def create_database():
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS IVOA
                      (id INTEGER,
                       group_name TEXT,
                       title TEXT,
                       concise_name TEXT,
                       version_major INTEGER,
                       version_minor INTEGER,
                       status TEXT,
                       date INTEGER,
                       authors TEXT,
                       editors TEXT,
                       abstract TEXT,
                       docname TEXT PRIMARY KEY,
                       package_path TEXT,
                       email TEXT,
                       comment TEXT,
                       extra_description TEXT,
                       available_formats TEXT)''')

    conn.commit()
    cursor.execute('''CREATE TABLE IF NOT EXISTS doi_bibcode
                      (id INTEGER,
                       doi TEXT,
                       bibcode TEXT,
                       docname TEXT PRIMARY KEY,
                       FOREIGN KEY(docname)
                          REFERENCES IVOA(docname))''')
    conn.commit()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Errata
                      (id INTEGER,
                       erratum_number INTEGER,
                       erratum_title TEXT,
                       erratum_author TEXT,
                       erratum_date INTEGER,
                       erratum_accepted_date INTEGER,
                       erratum_link TEXT,
                       docname TEXT PRIMARY KEY,
                       erratum_status TEXT,
                       Foreign Key (docname)
                          REFERENCES IVOA(docname))''')
    conn.commit()
    cursor.execute('''CREATE TABLE IF NOT EXISTS rfc_link
                  (id INTEGER,
                   rfc_link TEXT,
                   docname TEXT PRIMARY KEY,
                   Foreign Key (docname)
                      REFERENCES IVOA(docname))''')
    conn.commit()
    conn.close()



# Function to insert data into SQLite table
def insert_data(id,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats,
                doi,bibcode,
                erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,erratum_status,
                rfc_link, ivoa_docname):
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO IVOA (id,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (id,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats))
    conn.commit()
    cursor.execute('''INSERT INTO doi_bibcode (id,doi,bibcode,ivoa_docname)
                      VALUES (?, ?, ?, ?)''', (id,doi,bibcode,docname))
    conn.commit()
    cursor.execute('''INSERT INTO Errata (erratum_id,erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,ivoa_docname,erratum_status)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (id,erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,docname,erratum_status))
    conn.commit()
    cursor.execute('''INSERT INTO  rfc_link (id,rfc_link,ivoa_docname)
                      VALUES (?, ?, ?)''', (id,rfc_link,docname))
    conn.commit()
    conn.close()

create_database()
insert_data(id,group_name,title,concise_name,version_major,version_minor,status,date,authors,editors,abstract,docname,package_path,email,comment,extra_description,available_formats,doi,bibcode,erratum_number,erratum_title,erratum_author,erratum_date,erratum_accepted_date,erratum_link,erratum_status,rfc_link,docname)
