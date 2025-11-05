/* DoFD:
deliverable: DEL-002
satisfies_acceptance: [ACR-201]
tests_must_pass:
  - tests/contract/openapi.spec.ts
contracts_must_pass:
  - contracts/openapi.yaml
*/
import path from 'path';
import request from 'supertest';
import jestOpenAPI from 'jest-openapi';
import { app, start, stop } from '../../src/api/app';

beforeAll(async () => {
  const specPath = path.join(__dirname, '../../contracts/openapi.yaml');
  // Initialize jest-openapi with the OpenAPI spec
  // @ts-ignore
  jestOpenAPI(specPath);
  await start();
});

afterAll(async () => { await stop(); });

test('POST /orders satisfies OpenAPI spec', async () => {
  const res = await request(app)
    .post('/orders')
    .set('Content-Type', 'application/json')
    .send({ customerId: '11111111-1111-1111-1111-111111111111', items: [{ sku: 'SKU-1', qty: 1 }] });
  expect(res.status).toBe(201);
  // Validate response against the OpenAPI spec
  // @ts-ignore
  expect(res).toSatisfyApiSpec();
});
