from abc import ABC, abstractmethod
from typing import Any

from schemas.tools import StructuredIntent


class BaseAgentProvider(ABC):
    """
    Abstract base for Agent Providers.
    Allows swapping between StrandsAgentProvider and MockAgentProvider.
    """
    
    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
    
    @abstractmethod
    def run_intent_agent(self, text: str) -> StructuredIntent:
        """Run the Intent Agent to extract structured intent from natural language."""

    @abstractmethod
    def run_planning_agent(self, intent: StructuredIntent) -> dict[str, Any]:
        """Run the Planning Agent to propose a ControlPlan."""
        
    @abstractmethod
    def run_operations_agent(self, query: str) -> str:
        """Run the Operations Agent to diagnose telemetry and device issues."""

class MockAgentProvider(BaseAgentProvider):
    """
    Mock agent for deterministic CI testing without AWS Bedrock/Strands.
    """
    def run_intent_agent(self, text: str) -> StructuredIntent:
        # Deterministic mock response
        return StructuredIntent(
            objective="Reduce water use",
            constraints=["Keep temperature safe"],
            target_zones=["z1"]
        )
        
    def run_planning_agent(self, intent: StructuredIntent) -> dict[str, Any]:
        from compiler.planner.optimizer import ObjectiveWeights, ScenarioOptimizer
        from domains.polyhouse.engine import (
            SimulationConfig,
            SimulationEngine,
            ZoneSimConfig,
        )
        from schemas.tools import Evidence
        
        # 1. Agent formulates candidate scenarios based on intent (deterministically here for mock)
        base_config = SimulationConfig(
            simulation_id="agent-plan-001",
            scenario_name="agent-water-reduction",
            days=30,
            dt_hours=2.0,
            seed=42,
            zones=[
                ZoneSimConfig(
                    zone_id=intent.target_zones[0] if intent.target_zones else "z1",
                    crop_id="dwarf_tomato",
                    area_sqm=500.0,
                    plant_density_per_sqm=15.0,
                    initial_tank_volume_liters=500.0,
                )
            ],
            initial_temperature_c=22.0,
        )
        
        # 2. Agent invokes Simulation Engine (Tool: simulate_scenario)
        engine = SimulationEngine(self.registry)
        
        # 3. Agent invokes Optimizer (Tool: run_optimizer)
        weights = ObjectiveWeights(yield_kg=10.0, water_l=-0.05, energy_kwh=-0.01, stress_penalty=-100.0)
        optimizer = ScenarioOptimizer(engine, weights)
        plan = optimizer.optimize(base_config)
        
        # 4. Agent receives result and structures it as Evidence
        evidence = Evidence(
            computed=[
                f"predicted_yield_kg = {plan.metrics['yield_kg']:.2f}",
                f"predicted_water_l = {plan.metrics['water_l']:.2f}",
                f"predicted_stress = {plan.metrics['stress']:.3f}"
            ]
        )
        
        from schemas.tools import ControlActionProposal, ControlPlanProposal
        proposal = ControlPlanProposal(actions=[
            ControlActionProposal(
                zone_id=intent.target_zones[0] if intent.target_zones else "z1",
                actuator_id=f"pump-{intent.target_zones[0] if intent.target_zones else 'z1'}",
                action_type="SET_ON",
                target_value=1.0,
                duration_s=600.0,
                reason="Reduce irrigation based on optimizer recommendation"
            )
        ])
        
        return {
            "recommendation": f"To achieve '{intent.objective}', reduce irrigation. Evaluated score: {plan.score:.2f}",
            "control_plan": proposal,
            "evidence": evidence,
            "is_safe": plan.is_safe,
            "violations": plan.violations
        }
        
    def run_operations_agent(self, query: str) -> str:
        if "Zone 2" in query:
            return "Zone 2 irrigation was not executed because the moisture sensor was stale and the Edge safety policy rejected automatic irrigation."
        return "Everything is nominal."
