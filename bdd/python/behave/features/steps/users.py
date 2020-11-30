from behave import *
import http.client
import json
from hamcrest import assert_that, equal_to

@given('a user is logged into the system')
def loggin_user(context):
    conn = http.client.HTTPConnection("localhost:8080")
    login_post = {
        'username': 'blue',
        'password': '123456'
    }
    json_data_post = json.dumps(login_post)
    conn.request("POST", "/login", json_data_post, headers={'Content-type': 'application/json'})
    res = conn.getresponse()
    data = res.read()
    data_json = json.loads(data.decode("utf-8"))
    if "token" in data_json:
        token = data_json['token']
        context.response = token
        pass
    else:
        assert False

@when('the user tries to get a user by id')
def get_users(context):
    token = context.response
    conn = http.client.HTTPConnection("localhost:8080")
    headers = {
        'Content-type': 'application/json',
        'authorization': token
    }
    conn.request("GET", "/users/1", headers=headers)
    res = conn.getresponse()
    context.response = res.status
    pass

@then('the user get as a result {code}')
def valid_users(context, code):
    status = context.response
    assert_that(str(status), equal_to(code))