import mysql.connector

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