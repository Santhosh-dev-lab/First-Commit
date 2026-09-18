from agents.base import MockAgentProvider
from schemas.tools import StructuredIntent


def test_mock_intent_agent() -> None:
    provider = MockAgentProvider()
    intent = provider.run_intent_agent("Reduce water use")
    assert isinstance(intent, StructuredIntent)
    assert intent.objective == "Reduce water use"
    assert "z1" in intent.target_zones

def test_mock_planning_agent() -> None:
    provider = MockAgentProvider()
    intent = provider.run_intent_agent("Reduce water use")
    plan = provider.run_planning_agent(intent)
    assert "recommendation" in plan
    assert plan["control_plan"] is not None

def test_mock_operations_agent() -> None:
    provider = MockAgentProvider()
    response = provider.run_operations_agent("Why isn't Zone 2 being irrigated?")
    assert "Zone 2" in response
    assert "stale" in response
