# PHYSICA

A Compiler for Physical Reality.

## Problem
Modern polyhouse farming requires complex control logic, precise physical modeling, and strict safety validation. Currently, farmers rely on disjointed systems or manual configuration.

## Architecture
Human Intent
     ↓
Physical Compiler
     ↓
Physical IR
     ↓
Simulation
     ↓
Optimization
     ↓
Safety Verification
     ↓
Executable Workflow
     ↓
Polyhouse

## Core concept
PHYSICA acts as a compiler that translates high-level natural language intent (e.g., "Grow 1000 kg of tomatoes in 120 days while minimizing water") into validated, simulated, and safe control plans for a physical polyhouse environment.

## Physical IR
The Physical Intermediate Representation (Physical IR) serves as the domain model for the entire farm, expressing configurations, resources, sensors, actuators, and the objective safely.

## Polyhouse simulation
Provides deterministic physics-based simulation of environmental parameters (temperature, humidity, CO2, soil moisture) based on state and control actions. 
*Note: Current implementation uses a simulated polyhouse.*

## Edge architecture
Abstracts the real-world communication layer. 
*Note: Current implementation uses a simulated edge gateway.*

## AWS architecture
Targeting an event-driven setup using AWS IoT Core, API Gateway, DynamoDB, and Step Functions.

## Local setup
```bash
# Clone the repository
git clone https://github.com/mrsub/physica.git
cd physica

# Install dependencies (Python)
# pip install ...

# Install dependencies (Node)
# npm install ...
```

## Development commands
```bash
make install
make test
make dev
```

## CI/CD
Fully automated pipeline using GitHub Actions (Lint, Typecheck, Test, CDK Synth).

## Future physical hardware integration
The platform is designed to cleanly separate the physical constraints from the AI/simulation core, ensuring real sensors and actuators can be integrated seamlessly in the future.
