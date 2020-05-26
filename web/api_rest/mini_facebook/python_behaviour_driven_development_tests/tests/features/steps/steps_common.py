from behave import *
from hamcrest import assert_that, equal_to

@step('It should get the {response}')
def get_response(context, response):
    assert_that(context.status, equal_to(int(response)))