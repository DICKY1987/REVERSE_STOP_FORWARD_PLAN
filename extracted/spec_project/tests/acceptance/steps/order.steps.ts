/* DoFD:
deliverable: DEL-001
satisfies_acceptance: [ACR-101]
tests_must_pass:
  - tests/acceptance/user_creates_order.feature
contracts_must_pass:
  - contracts/openapi.yaml
*/
import { Given, When, Then, BeforeAll, AfterAll } from '@cucumber/cucumber';
import request from 'supertest';
import { app, start, stop } from '../../../src/api/app';
import assert from 'assert';
let response: request.Response;
let payload: any;

BeforeAll(async () => { await start(); });
AfterAll(async () => { await stop(); });

Given('a valid CreateOrderRequest payload', function () {
  payload = { customerId: '11111111-1111-1111-1111-111111111111', items: [{
    sku: 'SKU-1', qty: 1 }] };
});

When('I POST it to /orders', async function () {
  response = await request(app)
    .post('/orders')
    .set('Content-Type', 'application/json')
    .send(payload);
});

Then('I receive 201 with an Order payload with status {string}', function (status: string) {
  assert.equal(response.status, 201);
  assert.equal(response.body.status, status);
  assert.ok(response.body.id);
});
