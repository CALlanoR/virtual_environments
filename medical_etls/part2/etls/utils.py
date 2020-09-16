import os
import csv
import requests

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = {'id': id}, stream = True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

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