from pydantic import BaseModel

class IrrigationState(BaseModel):
    substrate_moisture_percent: float
    tank_volume_liters: float
    cumulative_water_consumed_liters: float

class IrrigationModel:
    def step(self, current: IrrigationState, pump_on: bool, crop_uptake_liter_per_day: float, dt_days: float) -> IrrigationState:
        flow_rate_l_per_day = 100.0 if pump_on else 0.0
        
        water_added = flow_rate_l_per_day * dt_days
        water_removed = crop_uptake_liter_per_day * dt_days
        
        # Simplified moisture conversion (assume 100L substrate capacity)
        moisture_change = (water_added - water_removed) / 100.0 * 100.0
        new_moisture = max(0.0, min(100.0, current.substrate_moisture_percent + moisture_change))
        
        return IrrigationState(
            substrate_moisture_percent=new_moisture,
            tank_volume_liters=max(0.0, current.tank_volume_liters - water_added),
            cumulative_water_consumed_liters=current.cumulative_water_consumed_liters + water_added
        )
