# Architecture Principles

1. System overview: Monorepo with separated apps and packages
2. Frontend: Next.js + React + shadcn/ui
3. API: FastAPI + Uvicorn
4. Compiler: Validates and translates intent to Physical IR
5. Physical IR: Pydantic typed models defining the environment and constraints
6. Simulation engine: Deterministic modeling
7. Digital twin: Domain models for current physical state
8. Edge gateway: IoT abstraction layer
9. Safety engine: Rejects dangerous plans
10. AWS architecture: Lambda, API Gateway, DynamoDB, IoT Core
11. CI/CD: GitHub Actions based OIDC deployment
12. Data flow: unidirectional intent to execution
13. Security boundaries: Hardware never directly interfaces with the untrusted AI output.
14. Future physical hardware integration: Supported via explicit Edge protocols (MQTT/Modbus/OPC-UA).
