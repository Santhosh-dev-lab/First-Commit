from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Any

from schemas.tools import ControlPlanProposal, AgentTrace

class InMemoryPlanRepository:
    def __init__(self) -> None:
        self._plans: Dict[str, ControlPlanProposal] = {}

    def save(self, plan_id: str, plan: ControlPlanProposal) -> None:
        self._plans[plan_id] = plan

    def get(self, plan_id: str) -> Optional[ControlPlanProposal]:
        return self._plans.get(plan_id)

class InMemoryExecutionRepository:
    def __init__(self) -> None:
        self._executions: Dict[str, Dict[str, Any]] = {}

    def save(self, execution_id: str, execution_data: Dict[str, Any]) -> None:
        self._executions[execution_id] = execution_data

    def get(self, execution_id: str) -> Optional[Dict[str, Any]]:
        return self._executions.get(execution_id)

class InMemoryAgentTraceRepository:
    def __init__(self) -> None:
        self._traces: Dict[str, AgentTrace] = {}

    def save(self, trace_id: str, trace: AgentTrace) -> None:
        self._traces[trace_id] = trace

    def get(self, trace_id: str) -> Optional[AgentTrace]:
        return self._traces.get(trace_id)

    def list_all(self) -> List[AgentTrace]:
        return list(self._traces.values())

# Global in-memory repositories for the local API demo
plan_repo = InMemoryPlanRepository()
execution_repo = InMemoryExecutionRepository()
agent_trace_repo = InMemoryAgentTraceRepository()
