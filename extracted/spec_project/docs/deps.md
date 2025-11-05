graph TD
  DEL-001[API Endpoint /orders] --> TEST-ACPT-42
  DEL-001 --> CT-API[OpenAPI Contract]
  CT-API --> TEST-CT-API[Contract Tests]
  TEST-ACPT-42 --> EVID-ACPT-42[CI Evidence]
  FILE-src_api_handler[handler.ts] --> DEL-001
