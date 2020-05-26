import http.client
import logging
import json

def execute_request(method, url, path, body=None, token=None):
    logging.info("method: {0}, path: {1}, body: {2}, endpoint_url_http: {3}".format(method, path, body, url))
    conn = http.client.HTTPConnection(url)

    content_type = 'application/json'
    if token == None:
        headers = {
            'content-type': content_type
        }
    else:
        headers = {
            'content-type': content_type,
            'authorization': token
        }

    if body != None:
        json_data_post = json.dumps(body)
        conn.request(method, path, json_data_post, headers=headers)
    else:
        conn.request(method, path, headers=headers)

    response = conn.getresponse()
    data = response.read().decode("utf-8")
    status = response.status
    return data, status