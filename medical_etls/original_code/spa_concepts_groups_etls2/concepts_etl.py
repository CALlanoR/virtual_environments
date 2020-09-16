import mysql.connector
import logging.config
import database
import utils
import concepts_file_parser
import os
import sys

_files_read = 0
_concepts_read = 0
_concepts_inserted = 0
_concepts_updated = 0
_concepts_errors = 0
_results_file = None
_errors_file = None

def _get_logger():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    dir_name, filename = os.path.split(os.path.abspath(__file__))
    output_file = dir_name + "/concepts_etl.log"
    handler = logging.FileHandler(output_file)
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

_logger = _get_logger()

def run(file_path, domains, vocabularies, concepts, cnx):
    global _concepts_read
    global _concepts_inserted
    global _concepts_updated
    global _concepts_errors
    global _errors_file
    vocabulary = utils.extract_vocabulary_data_from_filename(file_path)
    if vocabulary['name'] not in vocabularies:
        vocabulary_id = database.add_vocabulary(vocabulary['name'],
                                                vocabulary['version'],
                                                cnx)
        vocabularies[vocabulary['name']] = vocabulary_id

    row = 2
    for line in utils.read_csv_file(file_path, delimiter='\t'):
        concept = concepts_file_parser.get_concept(line)
        _concepts_read += 1
        try:
            if (len(concept['pxordx']) != 0 and
                len(concept['code_type']) != 0 and
                len(concept['code']) != 0 and
                len(concept['concept_id']) != 0 and
                len(concept['vocabulary_id']) != 0 and 
                len(concept['domain_id']) != 0):

                # Add new domain to dictionary
                domain_name = concept['domain_id'].strip()
                if domain_name not in domains:
                    domains[domain_name] = database.add_domain(domain_name,
                                                               cnx)

                # Create key to identify uniquely the concept
                key = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}'.format(concept['pxordx'], 
                                                       concept['code_type'], 
                                                       concept['code'],
                                                       concept['concept_id'], 
                                                       concept['vocabulary_id'],
                                                       concept['domain_id'],
                                                       'public',
                                                       0)
                concept = filters(concept)

                if key not in concepts:
                    _logger.info("Adding new concept_id {0} to dictionary...".format(concept['concept_id']))

                    concepts[key] = {
                        "oldpxordx": concept['old_pxordx'],
                        "concept_class_id": concept['concept_class_id'],
                        "track": concept['track'],
                        "standard_concept": concept['standard_concept'],
                        "codewithperiods": concept['code_with_periods'],
                        "codescheme": concept['code_scheme'],
                        "long_desc": concept['long_description'],
                        "short_desc": concept['short_description'],
                        "code_status": concept['code_status'],
                        "code_change": concept['code_change'],
                        "code_change_year": concept['code_change_year'],
                        "code_planned_type": concept['code_planned_type'],
                        "code_billing_status": concept['code_billing_status'],
                        "code_cms_claim_status": concept['code_cms_claim_status'],
                        "sex_cd": concept['sex_code'],
                        "anat_or_cond": concept['anatomy_or_condition'],
                        "pl_cond_class_cd1": concept['pl_condition_class_code1'],
                        "pl_cond_class_desc1": concept['pl_condition_class_description1'],
                        "pl_cond_class_cd2": concept['pl_condition_class_code2'],
                        "pl_cond_class_desc2": concept['pl_condition_class_description2'],
                        "pl_cond_class_cd3": concept['pl_condition_class_code3'],
                        "pl_cond_class_desc3": concept['pl_condition_class_description3'],
                        "poa_code_status": concept['poa_code_status'],
                        "poa_code_change": concept['poa_code_change'],
                        "poa_code_change_year": concept['poa_code_change_year'],
                        "valid_start_date": concept['valid_start_date'],
                        "valid_end_date": concept['valid_end_date'],
                        "invalid_reason": concept['invalid_reason']
                    }
                    _logger.info("Inserting concept_id {0} in database.".format(concept['concept_id']))
                    database.add_concept(concept, cnx)
                    _concepts_inserted += 1
                else:
                    _logger.info("Updating concept_id {0}".format(concept['concept_id']))
                    database.update_concept(concept, concepts['id'], cnx)
                    _concepts_updated += 1
            else:
                message = "Error in row: %d, missing fields to create the key." % row
                _logger.error(message)
                print(message)
                _concepts_errors += 1
                _errors_file.write(message)
        except Exception as e:
            message = str(e) + " file: {0} - row: {1}".format(file_path, row)
            _logger.error(message)
            print(message)
            _concepts_errors += 1
            _errors_file.write(message)
        row += 1

def filters(concept):
    if concept['standard_concept'] == 'Standard':
        concept['standard_concept'] = 'S'
    elif concept['standard_concept'] == 'Non-standard':
        concept['standard_concept'] = 'N'

    if concept['invalid_reason'] == 'Valid':
        concept['invalid_reason'] = 'V'
    elif concept['invalid_reason'] == 'Invalid':
        concept['invalid_reason'] = 'I'
    return concept      

def main():
    global _concepts_read
    global _concepts_inserted
    global _concepts_updated
    global _concepts_errors
    global _errors_file
    global _files_read
    global _results_file
    global _errors_file

    config = {
      'user': 'dev',
      'password': '4g83ytxKJvb1y8p4',
      'host': '35.231.30.58',
      'database': 'allconcepts_omop_api',
      'raise_on_warnings': True
    }

    cnx = mysql.connector.connect(**config)

    _logger.info('Getting all current domains from database')
    domains = database.get_current_domains(cnx)
    _logger.info('Getting all current vocabularies from database')
    vocabularies = database.get_current_vocabularies(cnx)
    _logger.info('Getting all current concepts from database')
    concepts = database.get_current_concepts(cnx)

    _errors_file = open('concepts_etl_errors.log', 'a')

    dir_path = '/home/callanor/Dropbox/my_works/oiga/spa_concepts_groups_etls2/allconcepts_files/'
    list_files = map(lambda file_name: os.path.join(dir_path, file_name), os.listdir(dir_path))
    for file_path in list_files:
         print("*********** processing file %s *****************" % file_path)
         _logger.info('processing file %s' % file_path)
         run(file_path, domains, vocabularies, concepts, cnx)
         _files_read += 1
    print("completed processing of the concepts")
    _logger.info('Completed processing of the concepts')

    _errors_file.close()

    _results_file = open('concepts_etl_results.log', 'a')
    _results_file.write("Total files read: {0}".format(files_read))
    _results_file.write("Total concepts read: {0}".format(concepts_read))
    _results_file.write("Total concepts inserted: {0}".format(concepts_inserted))
    _results_file.write("Total concepts updated: {0}".format(concepts_updated))
    _results_file.write("Total concepts with errors: {0}".format(concepts_errors))
    _results_file.close()

if __name__ == "__main__":
    main()
