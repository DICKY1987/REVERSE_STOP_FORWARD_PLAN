import { Given, When, Then } from '@cucumber/cucumber';
import request from 'supertest';
import { app } from '../../../src/app';
let response: request.Response;
let payload: any;

Given('a valid CreateOrderRequest payload', function () {
  payload = {
    customerId: '11111111-1111-1111-1111-111111111111',
    items: [ { sku: 'ABC123', qty: 1 } ]
  };
});

When('I POST it to /orders', async function () {
  response = await request(app).post('/orders').send(payload);
});

Then('I receive {int} with an Order payload with status {string}', function (status: number, expectedStatus: string) {
  if (response.status !== status) throw new Error(`Expected ${status}, got ${response.status}`);
  if (response.body.status !== expectedStatus) throw new Error(`Expected status ${expectedStatus}, got ${response.body.status}`);
});
