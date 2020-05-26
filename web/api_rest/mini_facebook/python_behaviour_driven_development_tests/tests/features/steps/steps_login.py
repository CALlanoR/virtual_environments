from behave import *
from config import endpoint_url_http
from utils.common import execute_request
from hamcrest import assert_that, equal_to, starts_with
import json
import logging
import http.client

@step('The {user} user log in the API with password {password}')
def send_login_request(context, user, password):
    logging.info("user: {0}, password: {1}".format(user, password))
    login_post = {
        'username': user,
        'password': password
    }
    data, status = execute_request("POST",
                                   endpoint_url_http,
                                   "/users/login",
                                   login_post,
                                   token=None)
    logging.info("data: {0}, status: {1}".format(data, status))
    context.data = data
    context.status = status

@step('if the login is successful you should return the jwt token')
def get_jwt_token(context):
    if context.status == 200:
        data_json = json.loads(context.data)
        jwt_token = data_json['token']
        assert_that(jwt_token, starts_with("Bearer"))


@step('The user logs successfully into the api')
def send_login_request(context):
    login_post = {
        'username': 'blue',
        'password': '123456'
    }
    data, status = execute_request("POST",
                                   endpoint_url_http,
                                   "/users/login",
                                   login_post,
                                   token=None)
    data_json = json.loads(data)
    jwt_token = data_json['token']
    assert_that(jwt_token, starts_with("Bearer"))
    assert_that(status, equal_to(200))
    context.token = jwt_token
