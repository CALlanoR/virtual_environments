import os
import csv
import yaml
import logging.config
import distutils.dir_util
from datetime import datetime


# def setup_logging(default_path='logging.yaml', 
#                   default_level=logging.DEBUG, 
#                   env_key='LOG_CFG'):
#     path = default_path
#     value = os.getenv(env_key, None)
#     if value:
#         path = value
#     if os.path.exists(path):
#         with open(path, 'rt') as f:
#             config = yaml.safe_load(f.read())

#         logs_directories = {os.path.dirname(handler['filename'])
#                             for key, handler in config['handlers'].items()
#                             if handler.get('filename') is not None}

#         for directory in logs_directories:
#             distutils.dir_util.mkpath(directory)
#         logging.config.dictConfig(config)
#     else:
#         logging.basicConfig(level=default_level)

# def extract_vocabulary_data_from_filename(file_path):
#     base = os.path.basename(file_path)
#     basename = os.path.splitext(base)[0]
#     tokens = basename.split(' ')
#     return {'name' : tokens[2], 'version' : tokens[4]}

# def copy_without_keys(d, keys):
#     return {k: v for k, v in d.items() if k not in keys}

# def get_taxonomy_key(taxonomy):
#     return '{0}|{1}|{2}|{3}|{4}|{5}'.format(taxonomy['root_cd1'], 
#                                             taxonomy['root_cd2'], 
#                                             taxonomy['root_cd3'],
#                                             taxonomy['root_cd4'], 
#                                             taxonomy['root_cd5'], 
#                                             taxonomy['root_cd6']).strip()

# def get_domain_key(domain):
#     return domain['name']

# def get_concept_key(code):
#     if type(code) is dict:
#         return '{0}|{1}|{2}|{3}|{4}'.format(code['pxordx'], 
#                                             code['code_type'], 
#                                             code['code'],
#                                             code['concept_id'],
#                                             code['vocabulary_id']).strip()
#     else:
#         return '{0}|{1}|{2}|{3}|{4}'.format(getattr(code, 'pxordx'), 
#                                             getattr(code, 'code_type'), 
#                                             getattr(code, 'code'),
#                                             getattr(code, 'concept_id'),
#                                             getattr(code, 'vocabulary_id')).strip()

# def get_concept_key_for_conceptsgroups(code):
#     if type(code) is dict:
#         return '{0}|{1}|{2}'.format(code['pxordx'], 
#                                     code['code_type'], 
#                                     code['code']).strip()
#     else:
#         return '{0}|{1}|{2}'.format(getattr(code, 'pxordx'), 
#                                     getattr(code, 'code_type'), 
#                                     getattr(code, 'code')).strip()

# def get_class_code_key(class_code):
#     return class_code['condition_class_code']

# def get_concept_group_key(code_group):
#     if type(code_group) is dict:
#         return '{0}|{1}|{2}|{3}'.format(code_group['group_type'].strip(),
#                                         code_group['group_type_name'].strip(),
#                                         code_group['group_name'].strip(),
#                                         code_group['domain'].strip())
#     else:
#         return '{0}|{1}|{2}|{3}'.format(getattr(code_group, 'group_type').strip(),
#                                         getattr(code_group, 'group_type_name').strip(),
#                                         getattr(code_group, 'group_name').strip(),
#                                         getattr(code_group, 'domain').strip())

# def get_concept_group_permission_key(concept_group_permission):
#     return concept_group_permission['description']

def extract_vocabulary_data_from_filename(file_path):
    base = os.path.basename(file_path)
    basename = os.path.splitext(base)[0]
    tokens = basename.split(' ')
    return {'name' : tokens[2], 'version' : tokens[4]}

def try_convert_int(value):
    try:
        return int(value.strip())
    except ValueError:
        return None

def try_convert_bool(value):
    lower_value = value.strip().lower()
    if lower_value == 'yes' or lower_value == 'y':
        return True
    elif lower_value == 'no' or lower_value == 'n':
        return False
    else:
        return None

def try_convert_date(value, value_format):
    try:
        return datetime.strptime(value.strip(), value_format)
    except ValueError:
        return None

def get_value_or_default(value, default=None):
    result = value.strip()
    if len(result) == 0:
        result = default
    return result

def read_csv_file(csv_file_name, 
                  delimiter, 
                  quote_char='"', 
                  skip_header=True, 
                  encoding='latin-1'):
    print(csv_file_name)
    fd = open(file=csv_file_name, mode='r', encoding=encoding)
    csv_reader = csv.reader(fd, delimiter=delimiter, quotechar=quote_char)
    if skip_header:
        next(csv_reader)
    for row in csv_reader:
        yield row
    fd.close()

# def flatten_collection(seq):
#     return (items for sublist in seq for items in sublist)
