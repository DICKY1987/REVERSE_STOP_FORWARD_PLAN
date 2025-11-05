Feature: Order Creation
  In order to track purchases
  As a platform client
  I want to create an order via the API

  @ACR-101
  Scenario: A valid order is created successfully
    Given I have a valid "CreateOrderRequest" payload
    When I send a POST request to "/orders" with the payload
    Then the response status should be 201
    And the response body should be a valid "Order" payload with status "CREATED"