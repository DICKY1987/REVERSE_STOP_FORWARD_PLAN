/* DoFD:
 * deliverable: DEL-001
 * satisfies_acceptance: [ACR-101]
 * tests_must_pass:
 *   - tests/acceptance/features/user_creates_order.feature
 *   - tests/contract/openapi.test.ts
 * contracts_must_pass:
 *   - contracts/openapi.yaml
 */

import { randomUUID } from 'crypto';

// This is a stub implementation. In a real app, this would involve
// business logic, database calls, etc.
export const createOrderHandler = (request: any) => {
  const { customerId, items } = request.body;

  // Basic validation (more would be in a real service)
  if (!customerId || !items || items.length === 0) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Invalid order data' }),
    };
  }

  const newOrder = {
    id: randomUUID(),
    customerId,
    items,
    status: 'CREATED',
  };

  return {
    statusCode: 201,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newOrder),
  };
};