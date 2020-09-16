import mysql.connector
from datetime import datetime

def get_current_vocabularies(cnx):
    vocabularies = {}
    cursor = cnx.cursor()
    query = ("SELECT id, ref FROM vocabularies")
    cursor.execute(query)
    for (id, ref) in cursor:
        if ref not in vocabularies:
            vocabularies[ref] = id
    cursor.close()
    return vocabularies

def add_vocabulary(vocabulary, cnx):
    sql = ("""INSERT INTO vocabularies(ref, name, url, description, status, version)
              VALUES(%s, %s, %s, %s, %s, %s)""")
    values = (
        vocabulary['ref'].strip(),
        vocabulary['name'].strip(),
        vocabulary['url'].strip(),
        vocabulary['description'].strip(),
        vocabulary['status'].strip(),
        vocabulary['version'].strip(),
    )
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()
    return cursor.lastrowid

def update_task_status(status, uuid, cnx):
    now = datetime.now()
    sql = ("""UPDATE tasks SET status = %s, last_update_date = %s WHERE uuid = %s""")
    values = (
        status,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        uuid,
    )
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()