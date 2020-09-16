import os
import csv

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