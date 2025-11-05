graph TD
  DEL-001[API Contract (openapi.yaml)] --> TEST-CT-001[Contract Tests]
  DEL-002[Acceptance Spec] --> TEST-ACPT-001[Acceptance Tests]
  DEL-003[Handler Implementation] --> TEST-UNIT-001[Unit Tests]
  DEL-003 --> TEST-CT-001
  DEL-003 --> TEST-ACPT-001
  TEST-CT-001 --> EVID-CT-001[Contract Test Evidence]
  TEST-UNIT-001 --> EVID-UNIT-001[Unit Test Evidence]
  TEST-ACPT-001 --> EVID-ACPT-001[Acceptance Test Evidence]
  FILE-src_api_handler[handler.ts] --> DEL-003
  FILE-contracts_openapi[openapi.yaml] --> DEL-001
  FILE-user_creates_order[user_creates_order.feature] --> DEL-002
