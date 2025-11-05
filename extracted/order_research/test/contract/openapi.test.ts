import { matchers } from 'jest-openapi';
import request from 'supertest';
import { app } from '../../src/app';
import * as path from 'path';
expect.extend(matchers);
const apiSpecPath = path.join(__dirname, '../../contracts/openapi.yaml');

describe('OpenAPI contract', () => {
  beforeAll(() => {
    // @ts-ignore
    jestOpenAPI(apiSpecPath);
  });

  test('POST /orders matches contract', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: '11111111-1111-1111-1111-111111111111', items: [
        { sku: 'ABC123', qty: 1 }
      ] });
    // @ts-ignore
    expect(res).toSatisfyApiSpec();
  });
});
