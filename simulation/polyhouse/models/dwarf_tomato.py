from enum import Enum
from pydantic import BaseModel
from typing import Optional


class GrowthStage(str, Enum):
    ESTABLISHMENT = "ESTABLISHMENT"
    VEGETATIVE = "VEGETATIVE"
    FLOWERING = "FLOWERING"
    FRUIT_SET = "FRUIT_SET"
    FRUIT_DEVELOPMENT = "FRUIT_DEVELOPMENT"
    MATURATION = "MATURATION"
    HARVEST = "HARVEST"


class Provenance(str, Enum):
    ASSUMED = "ASSUMED"
    LITERATURE = "LITERATURE"
    DATA_FITTED = "DATA_FITTED"
    USER_CONFIGURED = "USER_CONFIGURED"
    CALIBRATED = "CALIBRATED"
    SIMULATION_DEFAULT = "SIMULATION_DEFAULT"


class ParameterMetadata(BaseModel):
    value: float
    provenance: Provenance
    reference: Optional[str] = None


class DwarfTomatoModelParameters(BaseModel):
    plant_density_per_sqm: ParameterMetadata
    initial_biomass_kg: ParameterMetadata
    base_growth_rate: ParameterMetadata
    temp_optimum_celsius: ParameterMetadata
    light_optimum_par: ParameterMetadata


class DwarfTomatoState(BaseModel):
    age_days: float
    stage: GrowthStage
    biomass_kg: float
    vegetative_biomass_kg: float
    reproductive_biomass_kg: float
    fruit_biomass_kg: float
    crop_stress_index: float
    water_uptake_liter_per_day: float


class DwarfTomatoModel:
    def __init__(self, parameters: DwarfTomatoModelParameters):
        self.parameters = parameters

    def step(self, current_state: DwarfTomatoState, temp_c: float, par: float, co2: float, water_avail: float, stress_modifier: float, dt_days: float) -> DwarfTomatoState:
        # Conceptual growth model based on Maree et al.
        # Potential Growth × Temp Resp × Light Resp × CO2 Resp × Water Resp × Stress Modifier
        
        # Temp response (simplified parabola)
        t_opt = self.parameters.temp_optimum_celsius.value
        temp_resp = max(0.0, 1.0 - ((temp_c - t_opt) / 10.0)**2)
        
        # Light response (simplified Michaelis-Menten)
        l_opt = self.parameters.light_optimum_par.value
        light_resp = par / (par + (l_opt * 0.5))

        # Basic water response
        water_resp = min(1.0, water_avail / 2.0)  # assumes 2.0 L/day optimal

        # Growth
        base_rate = self.parameters.base_growth_rate.value
        actual_growth = base_rate * temp_resp * light_resp * water_resp * stress_modifier * dt_days
        
        new_biomass = current_state.biomass_kg + actual_growth
        
        # Basic stage transition
        new_age = current_state.age_days + dt_days
        new_stage = self._determine_stage(new_age)
        
        # Partitioning (simplified)
        veg_fraction = 0.8 if new_stage in [GrowthStage.ESTABLISHMENT, GrowthStage.VEGETATIVE] else 0.4
        new_veg = current_state.vegetative_biomass_kg + (actual_growth * veg_fraction)
        new_rep = current_state.reproductive_biomass_kg + (actual_growth * (1.0 - veg_fraction))
        new_fruit = new_rep * 0.8  # Assume 80% of reproductive biomass goes to fruit eventually

        return DwarfTomatoState(
            age_days=new_age,
            stage=new_stage,
            biomass_kg=new_biomass,
            vegetative_biomass_kg=new_veg,
            reproductive_biomass_kg=new_rep,
            fruit_biomass_kg=new_fruit,
            crop_stress_index=1.0 - stress_modifier,
            water_uptake_liter_per_day=water_resp * 2.0
        )

    def _determine_stage(self, age_days: float) -> GrowthStage:
        if age_days < 14:
            return GrowthStage.ESTABLISHMENT
        elif age_days < 35:
            return GrowthStage.VEGETATIVE
        elif age_days < 45:
            return GrowthStage.FLOWERING
        elif age_days < 60:
            return GrowthStage.FRUIT_SET
        elif age_days < 90:
            return GrowthStage.FRUIT_DEVELOPMENT
        elif age_days < 100:
            return GrowthStage.MATURATION
        else:
            return GrowthStage.HARVEST
