import { Given, When, Then, setDefaultTimeout } from '@cucumber/cucumber';
import assert from 'assert';
import { createOrderHandler } from '../../../src/api/handler'; // In-memory test

setDefaultTimeout(5 * 1000);

let requestPayload: any;
let response: any;

Given('I have a valid "CreateOrderRequest" payload', function () {
  requestPayload = {
    body: {
      customerId: 'a2b7b5f0-6c39-4d29-aa4a-4b07f0f443e4',
      items: [{ sku: 'PROD-123', quantity: 2 }],
    },
  };
});

When('I send a POST request to "/orders" with the payload', function () {
  // In a real scenario, this would be an HTTP request to a running service.
  // For this exemplar, we call the handler directly for simplicity.
  response = createOrderHandler(requestPayload);
});

Then('the response status should be {int}', function (expectedStatus) {
  assert.strictEqual(response.statusCode, expectedStatus);
});

Then('the response body should be a valid "Order" payload with status {string}', function (expectedStatus) {
  const body = JSON.parse(response.body);
  assert.ok(body.id, 'Response should have an ID');
  assert.strictEqual(body.status, expectedStatus, `Expected status to be ${expectedStatus}`);
  assert.deepStrictEqual(body.items, requestPayload.body.items);
});