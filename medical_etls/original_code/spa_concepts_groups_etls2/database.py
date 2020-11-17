import mysql.connector
import time

def get_current_domains(cnx):
    domains = {}
    cursor = cnx.cursor()
    query = ("SELECT domain_id, domain_name FROM domain")
    cursor.execute(query)
    for (id, name) in cursor:
        if name not in domains:
            domains[name] = id
    cursor.close()
    return domains

def add_domain(name, cnx):
    sql = ("INSERT INTO domain(domain_name, domain_concept_id, type, client_id) VALUES(%s, 0, 'public', 0)")
    values = (name,)
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()
    return cursor.lastrowid

def get_current_vocabularies(cnx):
    vocabularies = {}
    cursor = cnx.cursor()
    query = ("SELECT vocabulary_id, vocabulary_name FROM vocabulary")
    cursor.execute(query)
    for (id, name) in cursor:
        if name not in vocabularies:
            vocabularies[name] = id
    cursor.close()
    return vocabularies

def add_vocabulary(name, version, cnx):
    sql = ("INSERT INTO vocabulary(vocabulary_name, vocabulary_version, vocabulary_concept_id, type, client_id) VALUES(%s, %s, 0, 'public', 0)")
    values = (name, version)
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()
    return cursor.lastrowid

def get_current_concepts(cnx):
    concepts = {}
    cursor = cnx.cursor()
    query = ("""SELECT id,
                       PXORDX,
                       OLDPXORDX,
                       CODETYPE,
                       CONCEPT_CLASS_ID,
                       CONCEPT_ID,
                       TYPE,
                       VOCABULARY_ID,
                       DOMAIN_ID,
                       TRACK,
                       STANDARD_CONCEPT,
                       CODE,
                       CODEWITHPERIODS,
                       CODESCHEME,
                       LONG_DESC,
                       SHORT_DESC,
                       CODE_STATUS,
                       CODE_CHANGE,
                       CODE_CHANGE_YEAR,
                       CODE_PLANNED_TYPE,
                       CODE_BILLING_STATUS,
                       CODE_CMS_CLAIM_STATUS,
                       SEX_CD,
                       ANAT_OR_COND,
                       PL_COND_CLASS_CD1,
                       PL_COND_CLASS_DESC1,
                       PL_COND_CLASS_CD2,
                       PL_COND_CLASS_DESC2,
                       PL_COND_CLASS_CD3,
                       PL_COND_CLASS_DESC3,
                       PL_COND_CLASS_CD4,
                       PL_COND_CLASS_DESC4,                       
                       POA_CODE_STATUS,
                       POA_CODE_CHANGE,
                       POA_CODE_CHANGE_YEAR,
                       VALID_START_DATE,
                       VALID_END_DATE,
                       INVALID_REASON,
                       CREATE_DT,
                       TYPE,
                       CLIENT_ID
                FROM allconcepts WHERE CLIENT_ID = 0""")
    cursor.execute(query)

    for (id, 
         pxordx,
         oldpxordx,
         codetype,
         concept_class_id,
         concept_id,
         type_concept,
         vocabulary_id,
         domain_id,
         track,
         standard_concept,
         code,
         codewithperiods,
         codescheme,
         long_desc,
         short_desc,
         code_status,
         code_change,
         code_change_year,
         code_planned_type,
         code_billing_status,
         code_cms_claim_status,
         sex_cd,
         anat_or_cond,
         pl_cond_class_cd1,
         pl_cond_class_desc1,
         pl_cond_class_cd2,
         pl_cond_class_desc2,
         pl_cond_class_cd3,
         pl_cond_class_desc3,
         pl_cond_class_cd4,
         pl_cond_class_desc4,         
         poa_code_status,
         poa_code_change,
         poa_code_change_year,
         valid_start_date,
         valid_end_date,
         invalid_reason,
         create_date,
         concept_type,
         client_id) in cursor:
        key = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}'.format(pxordx,
                                               codetype,
                                               code,
                                               concept_id,
                                               vocabulary_id,
                                               domain_id,
                                               concept_type,
                                               client_id).strip()
        if key not in concepts:
            concepts[key] = {
                "id": id,
                "oldpxordx": oldpxordx,
                "concept_class_id": concept_class_id,
                "type": type_concept,
                "track": track,
                "standard_concept": standard_concept,
                "codewithperiods": codewithperiods,
                "codescheme": codescheme,
                "long_desc": long_desc,
                "short_desc": short_desc,
                "code_status": code_status,
                "code_change": code_change,
                "code_change_year": code_change_year,
                "code_planned_type": code_planned_type,
                "code_billing_status": code_billing_status,
                "code_cms_claim_status": code_cms_claim_status,
                "sex_cd": sex_cd,
                "anat_or_cond": anat_or_cond,
                "pl_cond_class_cd1": pl_cond_class_cd1,
                "pl_cond_class_desc1": pl_cond_class_desc1,
                "pl_cond_class_cd2": pl_cond_class_cd2,
                "pl_cond_class_desc2": pl_cond_class_desc2,
                "pl_cond_class_cd3": pl_cond_class_cd3,
                "pl_cond_class_desc3": pl_cond_class_desc3,
                "pl_cond_class_cd4": pl_cond_class_cd4,
                "pl_cond_class_desc4": pl_cond_class_desc4,                
                "poa_code_status": poa_code_status,
                "poa_code_change": poa_code_change,
                "poa_code_change_year": poa_code_change_year,
                "valid_start_date": valid_start_date,
                "valid_end_date": valid_end_date,
                "invalid_reason": invalid_reason
            }
    cursor.close()
    return concepts

def add_concept(concept, cnx):
    sql = """INSERT INTO allconcepts (PXORDX,
                                      OLDPXORDX,
                                      CODETYPE,
                                      CONCEPT_CLASS_ID,
                                      CONCEPT_ID,
                                      TYPE,
                                      VOCABULARY_ID,
                                      DOMAIN_ID,
                                      TRACK,
                                      STANDARD_CONCEPT,
                                      CODE,
                                      CODEWITHPERIODS,
                                      CODESCHEME,
                                      LONG_DESC,
                                      SHORT_DESC,
                                      CODE_STATUS,
                                      CODE_CHANGE,
                                      CODE_CHANGE_YEAR,
                                      CODE_PLANNED_TYPE,
                                      CODE_BILLING_STATUS,
                                      CODE_CMS_CLAIM_STATUS,
                                      SEX_CD,
                                      ANAT_OR_COND,
                                      PL_COND_CLASS_CD1,
                                      PL_COND_CLASS_DESC1,
                                      PL_COND_CLASS_CD2,
                                      PL_COND_CLASS_DESC2,
                                      PL_COND_CLASS_CD3,
                                      PL_COND_CLASS_DESC3,
                                      PL_COND_CLASS_CD4,
                                      PL_COND_CLASS_DESC4,
                                      POA_CODE_STATUS,
                                      POA_CODE_CHANGE,
                                      POA_CODE_CHANGE_YEAR,
                                      VALID_START_DATE,
                                      VALID_END_DATE,
                                      INVALID_REASON,
                                      CREATE_DT,
                                      CLIENT_ID) VALUES (%s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s, %s, 
                                                         %s, %s, %s, %s)"""
    values = (concept['pxordx'],
              concept['old_pxordx'],
              concept['code_type'],
              concept['concept_class_id'],
              concept['concept_id'],
              'public',
              concept['vocabulary_id'],
              concept['domain_id'],
              concept['track'],
              concept['standard_concept'],
              concept['code'],
              concept['code_with_periods'],
              concept['code_scheme'],
              concept['long_description'],
              concept['short_description'],
              concept['code_status'],
              concept['code_change'],
              concept['code_change_year'],
              concept['code_planned_type'],
              concept['code_billing_status'],
              concept['code_cms_claim_status'],
              concept['sex_code'],
              concept['anatomy_or_condition'],
              concept['pl_condition_class_code1'],
              concept['pl_condition_class_description1'],
              concept['pl_condition_class_code2'],
              concept['pl_condition_class_description2'],
              concept['pl_condition_class_code3'],
              concept['pl_condition_class_description3'],
              concept['pl_condition_class_code4'],
              concept['pl_condition_class_description4'],              
              concept['poa_code_status'],
              concept['poa_code_change'],
              concept['poa_code_change_year'],
              concept['valid_start_date'],
              concept['valid_end_date'],
              concept['invalid_reason'],
              time.strftime('%Y-%m-%d %H:%M:%S'),
              0)
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()

def update_concept(concept_file, concept_id, cnx):
    sql = """UPDATE allconcepts SET oldpxordx = %s,
                                    concept_class_id = %s,
                                    type = %s,
                                    track = %s,
                                    standard_concept = %s,
                                    codewithperiods = %s,
                                    codescheme = %s,
                                    long_desc = %s,
                                    short_desc = %s,
                                    code_status = %s,
                                    code_change = %s,
                                    code_change_year = %s,
                                    code_planned_type = %s,
                                    code_billing_status = %s,
                                    code_cms_claim_status = %s,
                                    sex_cd = %s,
                                    anat_or_cond = %s,
                                    pl_cond_class_cd1 = %s,
                                    pl_cond_class_desc1 = %s,
                                    pl_cond_class_cd2 = %s,
                                    pl_cond_class_desc2 = %s,
                                    pl_cond_class_cd3 = %s,
                                    pl_cond_class_desc3 = %s,
                                    pl_cond_class_cd4 = %s,
                                    pl_cond_class_desc4 = %s,                                    
                                    poa_code_status = %s,
                                    poa_code_change = %s,
                                    poa_code_change_year = %s,
                                    valid_start_date = %s,
                                    valid_end_date = %s,
                                    invalid_reason = %s,
                                    client_id = 0) WHERE id = %d"""
    values = (concept_file['old_pxordx'],
              concept_file['concept_class_id'],
              'public',
              concept_file['track'],
              concept_file['standard_concept'],
              concept_file['code_with_periods'],
              concept_file['code_scheme'],
              concept_file['long_description'],
              concept_file['short_description'],
              concept_file['code_status'],
              concept_file['code_change'],
              concept_file['code_change_year'],
              concept_file['ode_planned_type'],
              concept_file['code_billing_status'],
              concept_file['code_cms_claim_status'],
              concept_file['sex_code'],
              concept_file['anatomy_or_condition'],
              concept_file['pl_condition_class_code1'],
              concept_file['pl_condition_class_description1'],
              concept_file['pl_condition_class_code2'],
              concept_file['pl_condition_class_description2'],
              concept_file['pl_condition_class_code3'],
              concept_file['pl_condition_class_description3'],
              concept_file['pl_condition_class_code4'],
              concept_file['pl_condition_class_description4'],              
              concept_file['poa_code_status'],
              concept_file['poa_code_change'],
              concept_file['poa_code_change_year'],
              concept_file['valid_start_date'],
              concept_file['valid_end_date'],
              concept_file['invalid_reason'],
              concept_id)
    cursor = cnx.cursor()
    cursor.execute(sql, values)
    cnx.commit()
