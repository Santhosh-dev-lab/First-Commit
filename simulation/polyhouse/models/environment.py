
from pydantic import BaseModel


class EnvironmentState(BaseModel):
    temperature_celsius: float
    humidity_percent: float
    co2_ppm: float
    par_umol_m2_s: float

class ActuatorState(BaseModel):
    vent_open_percent: float = 0.0
    fan_on: bool = False
    fogger_on: bool = False
    heater_on: bool = False

class ClimateModel:
    def step(self, current: EnvironmentState, outside: EnvironmentState, actuators: ActuatorState, dt_days: float) -> EnvironmentState:
        # Very simplified model for demonstration
        dt_hours = dt_days * 24.0
        
        # Temp change
        temp_rate = 0.0
        if actuators.heater_on:
            temp_rate += 2.0
        if actuators.vent_open_percent > 0:
            temp_rate += (outside.temperature_celsius - current.temperature_celsius) * (actuators.vent_open_percent / 100.0)
        if actuators.fan_on:
            temp_rate += (outside.temperature_celsius - current.temperature_celsius) * 0.5
        if actuators.fogger_on:
            temp_rate -= 1.0
            
        new_temp = current.temperature_celsius + (temp_rate * dt_hours)
        
        # Humidity change
        hum_rate = 0.0
        if actuators.fogger_on:
            hum_rate += 10.0
        if actuators.vent_open_percent > 0:
            hum_rate += (outside.humidity_percent - current.humidity_percent) * (actuators.vent_open_percent / 100.0)
            
        new_hum = current.humidity_percent + (hum_rate * dt_hours)
        new_hum = max(0.0, min(100.0, new_hum))

        return EnvironmentState(
            temperature_celsius=new_temp,
            humidity_percent=new_hum,
            co2_ppm=current.co2_ppm,  # Assumed constant for now
            par_umol_m2_s=outside.par_umol_m2_s  # Assuming perfectly transparent polyhouse for now
        )
