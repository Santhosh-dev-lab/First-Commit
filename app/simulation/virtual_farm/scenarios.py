from .models import ScenarioType, VirtualFarmRuntimeConfig


class ScenarioEngine:
    """
    Modifies external/environmental conditions or communication behavior before a tick.
    """
    
    def apply(self, config: VirtualFarmRuntimeConfig, time_days: float) -> None:
        if config.scenario == ScenarioType.NORMAL:
            pass
        elif config.scenario == ScenarioType.WATER_SHORTAGE:
            # Maybe restrict tank volume artificially for actuators, or modify outside temp
            pass
        elif config.scenario == ScenarioType.HEAT_WAVE:
            config.outside_temperature_c = 40.0
            config.outside_humidity_percent = 30.0
        elif config.scenario == ScenarioType.HIGH_HUMIDITY:
            config.outside_humidity_percent = 95.0
        elif config.scenario == ScenarioType.LOW_TEMPERATURE:
            config.outside_temperature_c = 5.0
        elif config.scenario == ScenarioType.LOW_TANK:
            # We would need to set the tank volume in the engine state.
            # This class just modifies the config; runtime applies it.
            pass
        elif config.scenario == ScenarioType.SENSOR_FAILURE:
            # Applied in virtual sensors
            pass
        elif config.scenario == ScenarioType.GATEWAY_OFFLINE:
            # Applied in gateway
            pass
        elif config.scenario == ScenarioType.PUMP_FAILURE or config.scenario == ScenarioType.VALVE_FAILURE:
            # Applied in actuators
            pass
        elif config.scenario == ScenarioType.NETWORK_LATENCY or config.scenario == ScenarioType.PACKET_LOSS:
            # Applied in gateway
            pass
