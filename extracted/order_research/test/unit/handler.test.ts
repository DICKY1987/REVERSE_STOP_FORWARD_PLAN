import { createOrder } from '../../src/api/handler';
describe('createOrder', () => {
  it('returns CREATED status for valid order', async () => {
    const result = await createOrder({ customerId: 'id', items: [{ sku: 'sku', qty: 1 }] });
    expect(result.status).toBe('CREATED');
  });
});
