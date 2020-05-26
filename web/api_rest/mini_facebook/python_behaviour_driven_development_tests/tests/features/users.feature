@logging
@capture
Feature: Login user

Scenario Outline: Login
    Given The <user> user log in the API with password <password>
    then It should get the <response>
    and if the login is successful you should return the jwt token

Examples: good users
    | user | password | response |
    | blue | 123456   | 200      |

Examples: bad users
    | user | password | response |
    | blue | 12       | 401      |
    | red  | 123456   | 401      |

Scenario: Get user by id
    Given The user logs successfully into the api
    then It can get one user per id, for example the id "1"
