# links to DDS-001
Feature: Secure Customer Onboarding
  As a Payment Gateway Operator,
  I want to securely onboard new customers via API,
  So that I can process transactions while maintaining PCI-DSS compliance.

  Scenario: Successful customer creation with valid, tokenized payment details
    Given the Onboarding API is running
    And I have a valid CustomerCreateRequest payload conforming to the contract
    When I send a POST request to "/customers" with the payload
    Then the response status should be 201 Created
    And the response body should conform to the CustomerCreateResponse contract
    And the database should contain a new Customer record linked to a tokenized payment ID
