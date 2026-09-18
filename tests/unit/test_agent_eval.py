from agents.base import MockAgentProvider
from domains.polyhouse.crops.registry import CropRegistry
from schemas.tools import Evidence, StructuredIntent


def test_intent_agent_eval() -> None:
    registry = CropRegistry.default()
    provider = MockAgentProvider(registry)
    
    intent = provider.run_intent_agent("reduce water")
    assert isinstance(intent, StructuredIntent)
    assert intent.objective == "Reduce water use"

def test_planning_agent_eval() -> None:
    registry = CropRegistry.default()
    provider = MockAgentProvider(registry)
    
    intent = provider.run_intent_agent("reduce water")
    result = provider.run_planning_agent(intent)
    
    assert "recommendation" in result
    assert "evidence" in result
    assert isinstance(result["evidence"], Evidence)
    assert len(result["evidence"].computed) > 0
    assert result["is_safe"] is not None

def test_operations_agent_eval() -> None:
    registry = CropRegistry.default()
    provider = MockAgentProvider(registry)
    
    result = provider.run_operations_agent("stale sensor")
    assert isinstance(result, str)
    # The mock returns nominal if it doesn't match the specific demo string,
    # but the evaluation verifies the structure succeeds.
