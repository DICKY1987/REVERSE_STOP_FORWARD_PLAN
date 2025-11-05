# Contract-first for Order Service

*Status:* Accepted  
*Date:* 2025-11-05  

*Context*
We require parallel development and traceable interfaces.

*Decision*
Define OpenAPI before implementing endpoints; enforce via jest-openapi in CI.

*Consequences (Positive/Negative)*
+ Enables client stubs & validation; – adds spec maintenance overhead.

*Alternatives Considered*
Code-first (annotations), gRPC/proto, GraphQL SDL.

*Related ADRs / Links to contracts, DDS, RTM*
`contracts/openapi.yaml`, `deliverables/DEL-002.yaml`, `docs/rtm.csv`
