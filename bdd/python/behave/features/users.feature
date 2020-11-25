Feature: test users service

Scenario: Test user service
    Given a user is logged into the system
    When the user tries to get a user by id
    Then the user get as a result "200"

