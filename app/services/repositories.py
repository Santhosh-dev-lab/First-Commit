from __future__ import annotations

from typing import Any

from schemas.tools import AgentTrace, ControlPlanProposal


class InMemoryPlanRepository:
    def __init__(self) -> None:
        self._plans: dict[str, ControlPlanProposal] = {}

    def save(self, plan_id: str, plan: ControlPlanProposal) -> None:
        self._plans[plan_id] = plan

    def get(self, plan_id: str) -> ControlPlanProposal | None:
        return self._plans.get(plan_id)

    def get_all(self) -> dict[str, ControlPlanProposal]:
        return self._plans

class InMemoryExecutionRepository:
    def __init__(self) -> None:
        self._executions: dict[str, dict[str, Any]] = {}

    def save(self, execution_id: str, execution_data: dict[str, Any]) -> None:
        self._executions[execution_id] = execution_data

    def get(self, execution_id: str) -> dict[str, Any] | None:
        return self._executions.get(execution_id)

class InMemoryAgentTraceRepository:
    def __init__(self) -> None:
        self._traces: dict[str, AgentTrace] = {}

    def save(self, trace_id: str, trace: AgentTrace) -> None:
        self._traces[trace_id] = trace

    def get(self, trace_id: str) -> AgentTrace | None:
        return self._traces.get(trace_id)

    def list_all(self) -> list[AgentTrace]:
        return list(self._traces.values())

# Global in-memory repositories for the local API demo
plan_repo = InMemoryPlanRepository()
execution_repo = InMemoryExecutionRepository()
agent_trace_repo = InMemoryAgentTraceRepository()
