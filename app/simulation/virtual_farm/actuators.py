from domains.polyhouse.devices.simulated import SimulatedPump, SimulatedVent

from .models import VirtualActuatorConfig


class VirtualActuatorFactory:
    @staticmethod
    def create(config: VirtualActuatorConfig):
        if config.actuator_type == "pump":
            return SimulatedPump(config.actuator_id, config.zone_id or "")
        else:
            return SimulatedVent(config.actuator_id, config.zone_id or "")
