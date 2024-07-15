##################################################################################
######## In case any record in the sqlite database needs to be deleted,###########
########################## this script can be used. ##############################
##################################################################################

import sqlite3

def deleteRecord():
    try:
        sqliteConnection = sqlite3.connect('data.sqlite')
        cursor = sqliteConnection.cursor()
        print("Connected to IVOA Sqlite Database")

         # Deleting single record now
        IVOA_delete_query = """DELETE from IVOA where id = 5"""
        cursor.execute(IVOA_delete_query)
        sqliteConnection.commit()
        print("IVOA Record deleted successfully ")

        doi_bibcode_delete_query = """DELETE from doi_bibcode where id = 5"""
        cursor.execute(doi_bibcode_delete_query)
        sqliteConnection.commit()
        print("doi_bibcode Record deleted successfully ")

        Errata_delete_query = """DELETE from Errata where erratum_id = 5"""
        cursor.execute(Errata_delete_query)
        sqliteConnection.commit()
        print("Errata Record deleted successfully ")

        rfc_link_delete_query = """DELETE from rfc_link where id = 5"""
        cursor.execute(rfc_link_delete_query)
        sqliteConnection.commit()
        print("rfc_link Record deleted successfully ")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("the sqlite connection is closed")

deleteRecord()

#######################################################################################################
################### This program is to rename the column name the the database #############################
#######################################################################################################

import sqlite3

def rename_column(db_file, table_name, old_column_name, new_column_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Rename the column
    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}")
    conn.commit()
    print(f"Column '{old_column_name}' renamed to '{new_column_name}' in table '{table_name}'.")

    # Close the connection
    conn.close()

# Example usage
db_file = "data.sqlite"
table_name = "IVOA"
old_column_name = "contribute"
new_column_name = "extra_description"
rename_column(db_file, table_name, old_column_name, new_column_name)


#######################################################################################################
################### This program is to change all the entries in one column ###########################
################### Ex: Here the email is replaced by a 'new email' in the email column. ##############
#######################################################################################################

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('temp.sqlite')
cursor = conn.cursor()

# Execute the SQL update statement
new_email = 'ivoadoc@ivoa.net'
cursor.execute("UPDATE IVOA SET email = ?", (new_email,))

# Commit the changes and close the connection
conn.commit()
conn.close()
