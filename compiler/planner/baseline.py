from simulation.polyhouse.models.environment import ActuatorState, EnvironmentState
from simulation.polyhouse.models.irrigation import IrrigationState


class BaselineController:
    def __init__(self, target_temp_c: float = 24.0, trigger_moisture_percent: float = 60.0):
        self.target_temp = target_temp_c
        self.trigger_moisture = trigger_moisture_percent
        
    def determine_actions(self, env: EnvironmentState, irri: IrrigationState) -> tuple[ActuatorState, bool]:
        # Temp triggers
        actuators = ActuatorState()
        if env.temperature_celsius > self.target_temp + 2.0:
            actuators.vent_open_percent = 100.0
            actuators.fan_on = True
        elif env.temperature_celsius > self.target_temp:
            actuators.vent_open_percent = 50.0
            
        if env.temperature_celsius < self.target_temp - 2.0:
            actuators.heater_on = True
            actuators.vent_open_percent = 0.0
            
        if env.humidity_percent < 50.0:
            actuators.fogger_on = True
            
        # Irrigation trigger
        pump_on = irri.substrate_moisture_percent < self.trigger_moisture
            
        return actuators, pump_on
