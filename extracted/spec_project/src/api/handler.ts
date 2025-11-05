/* DoFD:
deliverable: DEL-001
satisfies_acceptance: [ACR-101]
tests_must_pass:
  - tests/acceptance/user_creates_order.feature
contracts_must_pass:
  - contracts/openapi.yaml
*/
import { Request, Response } from 'express';
import { randomUUID } from 'crypto';

export const createOrder = (req: Request, res: Response) => {
  // Minimal validation; full JSON Schema validation can be added later
  if (!req.body?.customerId || !Array.isArray(req.body?.items) || req.body.items.length === 0) {
    return res.status(400).json({ error: 'Invalid payload' });
  }
  const id = randomUUID();
  return res.status(201).json({ id, status: 'CREATED' });
};
