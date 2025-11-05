Feature: Order creation
  In order to track purchases
  As a customer
  I want to create an order

  Scenario: valid order is created
    Given a valid CreateOrderRequest payload
    When I POST it to /orders
    Then I receive 201 with an Order payload with status "CREATED"
