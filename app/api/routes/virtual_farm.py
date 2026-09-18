import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_authorized_farm
from app.simulation.virtual_farm.models import (
    VirtualFarmRuntimeConfig, 
    RuntimeStatusResponse, 
    ScenarioType,
    ClockMode,
    RuntimeStatus
)
from app.simulation.virtual_farm.runtime import VirtualFarmRuntime

router = APIRouter(prefix="/simulation/runtime", tags=["Virtual Farm"])

# For this milestone, we hold instances in memory since this is a demonstration of the orchestration.
# A real implementation could persist runtime state strictly in DB and restore from it.
_active_runtimes: dict[str, VirtualFarmRuntime] = {}

def get_runtime(farm_id: str) -> VirtualFarmRuntime:
    if farm_id not in _active_runtimes:
        raise HTTPException(status_code=404, detail=f"No active Virtual Farm Runtime for farm {farm_id}")
    return _active_runtimes[farm_id]

@router.post("/start")
def start_runtime(
    config: VirtualFarmRuntimeConfig,
    farm: dict = Depends(get_authorized_farm)
) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    if config.farm_id != farm_id:
        raise HTTPException(status_code=403, detail="Unauthorized farm_id")
        
    if config.farm_id in _active_runtimes:
        raise HTTPException(status_code=400, detail="Runtime already exists for this farm")
        
    runtime = VirtualFarmRuntime(config)
    runtime.start()
    _active_runtimes[config.farm_id] = runtime
    
    return _build_response(runtime)

@router.post("/stop")
def stop_runtime(farm: dict = Depends(get_authorized_farm)) -> dict[str, str]:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    runtime.stop()
    del _active_runtimes[farm_id]
    return {"status": "STOPPED"}

@router.post("/pause")
def pause_runtime(farm: dict = Depends(get_authorized_farm)) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    runtime.pause()
    return _build_response(runtime)

@router.post("/resume")
def resume_runtime(farm: dict = Depends(get_authorized_farm)) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    runtime.resume()
    return _build_response(runtime)

@router.post("/step")
def step_runtime(farm: dict = Depends(get_authorized_farm)) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    runtime.step()
    return _build_response(runtime)

@router.get("/status")
def get_status(farm: dict = Depends(get_authorized_farm)) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    return _build_response(runtime)

@router.post("/scenario")
def set_scenario(scenario: ScenarioType, farm: dict = Depends(get_authorized_farm)) -> RuntimeStatusResponse:
    farm_id = farm["farm"]["id"]
    runtime = get_runtime(farm_id)
    runtime.config.scenario = scenario
    return _build_response(runtime)


def _build_response(runtime: VirtualFarmRuntime) -> RuntimeStatusResponse:
    return RuntimeStatusResponse(
        run_id=runtime.config.run_id,
        farm_id=runtime.config.farm_id,
        status=runtime.status,
        simulation_time=runtime.clock.current_sim_time,
        scenario=runtime.config.scenario,
        clock_mode=runtime.config.clock_mode,
        current_step=runtime.engine_state.current_step_idx if runtime.engine_state else 0,
        last_telemetry_timestamp=runtime.last_telemetry_timestamp,
        gateway_status=runtime.gateway.status,
        sensor_summary={s_id: "OK" for s_id in runtime.sensors},
        actuator_summary={a_id: "OK" for a_id in runtime.actuators},
        failure_summary=[]
    )
