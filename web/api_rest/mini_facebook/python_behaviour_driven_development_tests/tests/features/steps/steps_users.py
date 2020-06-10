from behave import *
from config import endpoint_url_http
from utils.common import execute_request
from hamcrest import assert_that, equal_to, has_key, contains_string
import json
import logging
import http.client

@then('It can get one user per id, for example the id "{id}"')
def get_user_by_id(context, id):
    jwt_token = context.token

    data, status = execute_request("GET",
                                   endpoint_url_http,
                                   "/users?id={0}".format(int(id)),
                                   body=None,
                                   token=jwt_token)
    logging.info("data: {0}, status: {1}".format(data, status))

    assert_that(data, contains_string('email'))
    assert_that(data, contains_string('name'))
    assert_that(data, contains_string('username'))

    
