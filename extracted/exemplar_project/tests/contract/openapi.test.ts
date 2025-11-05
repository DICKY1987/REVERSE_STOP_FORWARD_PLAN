import OpenAPIBackend from 'openapi-backend';
import path from 'path';

describe('OpenAPI Contract Validation', () => {
  let api: OpenAPIBackend;

  beforeAll(() => {
    api = new OpenAPIBackend({
      definition: path.join(__dirname, '../../contracts/openapi.yaml'),
      strict: true,
    });
    api.init();
  });

  it('should validate a valid request to POST /orders', () => {
    const validRequest = {
      customerId: 'c7b5f0e9-3c9a-4d2f-b0a6-1b07f0f443e4',
      items: [{ sku: 'SKU-001', quantity: 1 }],
    };

    const { valid } = api.validateRequestBody(
      validRequest,
      api.getOperation('createOrder')!
    );
    expect(valid).toBe(true);
  });

  it('should invalidate a request with missing required fields', () => {
    const invalidRequest = {
      items: [{ sku: 'SKU-001', quantity: 1 }], // missing customerId
    };
    const { errors } = api.validateRequestBody(
      invalidRequest,
      api.getOperation('createOrder')!
    );
    expect(errors).toBeDefined();
    expect(errors!.length).toBeGreaterThan(0);
    expect(errors![0].message).toContain("must have required property 'customerId'");
  });

  it('should validate a valid 201 response from POST /orders', () => {
    const validResponse = {
      id: 'd9c5e0a9-4b9a-4d3f-c1a7-2c08f1f554f5',
      status: 'CREATED',
      customerId: 'c7b5f0e9-3c9a-4d2f-b0a6-1b07f0f443e4',
      items: [{ sku: 'SKU-001', quantity: 1 }],
    };

    const { valid } = api.validateResponse(validResponse, api.getOperation('createOrder')!, 201);
    expect(valid).toBe(true);
  });
});
