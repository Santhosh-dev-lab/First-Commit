from domains.edge.models import TelemetryEnvelope, TelemetrySource
from domains.polyhouse.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationEngineState,
)
from twin.core import SensorQuality

from .actuators import VirtualActuatorFactory
from .clock import SimulationClock
from .gateway import VirtualEdgeGateway
from .models import RuntimeStatus, VirtualFarmRuntimeConfig
from .scenarios import ScenarioEngine
from .sensors import VirtualSensor


class VirtualFarmRuntime:
    def __init__(self, config: VirtualFarmRuntimeConfig):
        self.config = config
        self.clock = SimulationClock(config.clock_mode)
        self.scenario_engine = ScenarioEngine()
        self.gateway = VirtualEdgeGateway(config.farm_id)
        self.status = RuntimeStatus.STOPPED
        
        # We use a NoOp controller so the SimulationEngine doesn't overwrite manually injected commands
        from domains.polyhouse.controllers.base import (
            Controller,
            ControlPlan,
        )
        class NoOpController(Controller):
            def plan(self, simulation_id, timestep, time_days, zone_contexts):
                return ControlPlan(plan_id="noop", simulation_id=simulation_id, timestep=timestep, time_days=time_days, actions=[])
                
        self.engine = SimulationEngine(controller=NoOpController())
        self.engine_state: SimulationEngineState | None = None
        
        self.sensors = {}
        for s_cfg in config.sensors:
            self.sensors[s_cfg.sensor_id] = VirtualSensor(s_cfg)
            
        self.actuators = {}
        for a_cfg in config.actuators:
            self.actuators[a_cfg.actuator_id] = VirtualActuatorFactory.create(a_cfg)
            
        self.last_telemetry_timestamp = None
        self._sequence_number = 0

    def start(self):
        if self.status != RuntimeStatus.STOPPED:
            return
            
        # Build standard simulation config for engine
        sim_config = SimulationConfig(
            simulation_id=self.config.run_id,
            scenario_name=self.config.scenario.value,
            days=999, # run indefinitely, runtime controls steps
            dt_hours=self.config.step_size_hours,
            seed=self.config.seed,
            zones=self.config.zones,
            initial_temperature_c=self.config.initial_temperature_c,
            initial_humidity_percent=self.config.initial_humidity_percent,
            initial_co2_ppm=self.config.initial_co2_ppm,
            initial_par_umol_m2_s=self.config.initial_par_umol_m2_s,
            outside_temperature_c=self.config.outside_temperature_c,
            outside_humidity_percent=self.config.outside_humidity_percent,
        )
        self.engine_state = self.engine.initialize_state(sim_config)
        self.gateway.connect()
        self.status = RuntimeStatus.RUNNING

    def pause(self):
        if self.status == RuntimeStatus.RUNNING:
            self.status = RuntimeStatus.PAUSED

    def resume(self):
        if self.status == RuntimeStatus.PAUSED:
            self.status = RuntimeStatus.RUNNING

    def stop(self):
        self.status = RuntimeStatus.STOPPED
        self.gateway.disconnect()

    def step(self):
        if self.status != RuntimeStatus.RUNNING:
            return
            
        # 1. Advance Clock
        sim_time = self.clock.advance(self.config.step_size_hours)
        
        # 2. Process pending commands from Gateway
        pending_commands = self.gateway.get_pending_commands()
        if pending_commands and self.engine_state:
            for cmd in pending_commands:
                act = self.engine_state.device_registry.get_actuator(cmd.device_id)
                if act:
                    ctype = cmd.command_type.value
                    if ctype.endswith(("_ON", "_OPEN")):
                        act.execute(1.0)
                    elif ctype.endswith(("_OFF", "_CLOSE")):
                        act.execute(0.0)
                    else:
                        act.execute(cmd.parameters.get("value", 1.0))
                
        # 3. Apply Scenario
        self.scenario_engine.apply(self.config, self.engine_state.current_time_days if self.engine_state else 0)
        
        # Sync external parameters to engine state if scenario modified them
        if self.engine_state:
            self.engine_state.config.outside_temperature_c = self.config.outside_temperature_c
            self.engine_state.config.outside_humidity_percent = self.config.outside_humidity_percent
            
            # 4. Advance Simulation Engine
            self.engine.step(self.engine_state, timestamp=sim_time)
            
            # 5. Read Virtual Sensors and emit Telemetry
            self._emit_telemetry(sim_time)

    def _emit_telemetry(self, sim_time: float):
        if not self.engine_state: return
        
        for s_cfg in self.config.sensors:
            sensor = self.sensors[s_cfg.sensor_id]
            
            # Extract ground truth from engine_state based on sensor type
            true_val = 0.0
            if s_cfg.sensor_type == "temperature": true_val = self.engine_state.temp_c
            elif s_cfg.sensor_type == "humidity": true_val = self.engine_state.hum_pct
            elif s_cfg.sensor_type == "co2": true_val = self.engine_state.co2_ppm
            elif s_cfg.sensor_type == "par": true_val = self.engine_state.par
            elif s_cfg.sensor_type == "moisture" and s_cfg.zone_id and s_cfg.zone_id in self.engine_state.zone_moisture:
                true_val = self.engine_state.zone_moisture[s_cfg.zone_id]
                    
            obs_val, qual = sensor.read(true_val)
            if qual == SensorQuality.MISSING:
                continue
                
            self._sequence_number += 1
            measurements = {
                s_cfg.sensor_type: obs_val
            }
            metadata = {
                "unit": s_cfg.unit,
                "quality": qual.value,
                "_sequence_number": self._sequence_number
            }
            
            envelope = TelemetryEnvelope(
                farm_id=self.config.farm_id,
                gateway_id="virtual-gateway",
                device_id=s_cfg.sensor_id,
                zone_id=s_cfg.zone_id,
                timestamp=sim_time,
                measurements=measurements,
                metadata=metadata,
                source=TelemetrySource.LOCAL_SIMULATION,
                signature=None
            )
            self.gateway.publish_telemetry(envelope)
            self.last_telemetry_timestamp = sim_time
