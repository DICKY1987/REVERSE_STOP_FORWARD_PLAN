# Test Stack: Cucumber.js for ATDD; Jest + Supertest for contract/system

*Status:* Accepted  
*Date:* 2025-11-05  

*Context*
Business-readable scenarios with executable backing, plus fast Node test runner.

*Decision*
Use @cucumber/cucumber for acceptance; Jest with jest-openapi & Supertest for contract/system.

*Consequences*
+ Clear Given/When/Then; – two runners to configure.

*Alternatives*
Playwright BDD, Mocha/Chai.

*Related*
`tests/acceptance/*`, `tests/contract/*`, `deliverables/*.yaml`
