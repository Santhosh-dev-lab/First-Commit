from __future__ import annotations

from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    text: str = Field(description="Natural language instruction for the farm")
    zone_id: str | None = Field(default=None, description="Optional target zone identifier")

class IntentResponse(BaseModel):
    objective: str
    constraints: list[str]
    target_zones: list[str]
    plan_id: str | None = None

class SimulationRequest(BaseModel):
    scenario_name: str
    days: int
    dt_hours: float = 1.0
    zone_ids: list[str]

class SimulationResponse(BaseModel):
    simulation_id: str
    scenario_name: str
    provenance_hash: str
    total_days_simulated: float
    total_water_used_l: float
    violations: int
    stress_index: float
    requested_water_l: float
    delivered_water_l: float
    unmet_water_demand_l: float
    remaining_water_l: float
    final_yield_kg: float

class WhatIfRequest(BaseModel):
    days: int
    zone_ids: list[str]
    water_availability_l: float | None = None
    temperature_bias_c: float | None = None

class WhatIfResponse(BaseModel):
    baseline: SimulationResponse
    scenario: SimulationResponse
    delta_yield_kg: float
    delta_water_used_l: float
    delta_stress_index: float

class ActionResponse(BaseModel):
    zone_id: str
    actuator_id: str
    action_type: str
    target_value: float
    duration_s: float
    reason: str

class PlanResponse(BaseModel):
    plan_id: str
    actions: list[ActionResponse]
    execution_status: str
    created_by: str

class ApprovalRequest(BaseModel):
    approved: bool
    reason: str | None = None

class ExecutionResponse(BaseModel):
    execution_id: str
    plan_id: str
    status: str
    dispatched_at: float | None = None
    acknowledged_at: float | None = None

class ZoneResponse(BaseModel):
    zone_id: str
    crop_id: str
    area_sqm: float

class TwinResponse(BaseModel):
    polyhouse_id: str
    zones: list[ZoneResponse]
    temperature_c: float
    humidity_percent: float
    substrate_moisture_percent: float
    crop_stress_index: float
    tank_volume_l: float
    tank_capacity_l: float
    pump_state: str
    sensor_health: str
    timestamp: float

class ResourceResponse(BaseModel):
    tank_volume_l: float
    energy_kwh: float | None = None

class TelemetryResponse(BaseModel):
    device_id: str
    zone_id: str
    measurement_type: str
    value: float
    unit: str
    timestamp: float
    quality: float

class EvidenceResponse(BaseModel):
    observed: list[str]
    computed: list[str]
    assumed: list[str]
    configured: list[str]
    predicted: list[str]
    simulated: list[str]

class AgentTraceResponse(BaseModel):
    run_id: str
    agent_type: str
    status: str
    tools_called: list[str]
    evidence: EvidenceResponse | None
    decision: str
    execution_state: str

class SafetyResponse(BaseModel):
    plan_id: str
    is_safe: bool
    violations: list[str]

# Dashboard Unified Models
class SystemStatus(BaseModel):
    is_online: bool
    physical_mode: str
    agent_provider: str
    digital_twin: str
    safety: str
    last_sync_timestamp: float
    farm_name: str | None = None

class ZoneSummary(BaseModel):
    zone_id: str
    crop_id: str
    area_sqm: float
    growth_stage: str | None
    temperature_c: float | None
    humidity_percent: float | None
    moisture_percent: float | None
    stress_index: float | None
    irrigation_status: str | None
    sensor_health: str | None
    status: str

class ResourceSummary(BaseModel):
    tank_volume_l: float | None
    requested_water_l: float
    delivered_water_l: float
    unmet_water_demand_l: float
    remaining_water_l: float

class AlertSummary(BaseModel):
    id: str
    severity: str
    category: str
    message: str
    zone_id: str | None
    timestamp: float

class DashboardSnapshot(BaseModel):
    system: SystemStatus
    zones: list[ZoneSummary]
    resources: ResourceSummary
    telemetry: list[TelemetryResponse]
    alerts: list[AlertSummary]
    agent_trace: AgentTraceResponse | None
    active_plans: list[PlanResponse]
