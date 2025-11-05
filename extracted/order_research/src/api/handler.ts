export interface CreateOrderRequest {
  customerId: string;
  items: Array<{ sku: string; qty: number }>;
}

export interface Order {
  id: string;
  status: 'CREATED' | 'REJECTED';
}

// Implementation stub
export async function createOrder(req: CreateOrderRequest): Promise<Order> {
  return { id: 'generated-id', status: 'CREATED' };
}
// Express handler or Fastify handler would wrap this function in the real implementation
