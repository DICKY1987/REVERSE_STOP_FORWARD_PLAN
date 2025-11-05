# Contract‑First & Deliverables‑First Approach

*Status:* Accepted  
*Date:* 2025‑11‑05  

## Context
The project aims to deliver a generic order‑creation API.  Multiple teams may depend on the API, and we need clear contracts, testability and traceability.  
Past projects suffered from ad‑hoc task lists and undocumented decisions, leading to rework and inconsistent interfaces.

## Decision
We will adopt a **contract‑first** API design using OpenAPI 3.0.3, a **deliverables‑first** product breakdown, and an **acceptance‑first** development process.  ADRs will capture key decisions.  Every interface will have a formal contract and associated contract tests.  Deliverables will be defined via YAML sheets (DDS) linking acceptance criteria, evidence and files.  
A traceability matrix will map requirements to tests and artifacts.

## Consequences
Positive:  
• Enables parallel development and stakeholder alignment  
• Clear documentation of decisions improves maintainability and knowledge transfer  
• RTM supports compliance and change impact analysis
