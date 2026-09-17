"""
domains/polyhouse/devices/registry.py

DeviceRegistry to discover sensors and actuators.
"""


from .base import Actuator, Sensor


class DeviceRegistry:
    def __init__(self) -> None:
        self.sensors: dict[str, Sensor] = {}
        self.actuators: dict[str, Actuator] = {}
        
    def register_sensor(self, sensor: Sensor) -> None:
        self.sensors[sensor.sensor_id] = sensor
        
    def register_actuator(self, actuator: Actuator) -> None:
        self.actuators[actuator.actuator_id] = actuator
        
    def get_sensor(self, sensor_id: str) -> Sensor | None:
        return self.sensors.get(sensor_id)
        
    def get_actuator(self, actuator_id: str) -> Actuator | None:
        return self.actuators.get(actuator_id)

    def get_zone_actuators(self, zone_id: str) -> list[Actuator]:
        return [a for a in self.actuators.values() if a.zone_id == zone_id]

    def get_zone_sensors(self, zone_id: str) -> list[Sensor]:
        return [s for s in self.sensors.values() if s.zone_id == zone_id]
