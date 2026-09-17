"""
domains/polyhouse/crops/cucumber/model.py

Cucumber (Cucumis sativus) growth model — PROTOTYPE.

Key differences from tomato and lettuce
----------------------------------------
- Indeterminate vining growth habit (more rapid vegetative expansion)
- Continuous-harvest fruiting model (fruit continuously set and removed)
- More sensitive to temperature extremes than lettuce
- Requires higher humidity than tomato
- Different growth stages: GERMINATION → VEGETATIVE → FLOWERING
                           → FRUITING → HARVESTING

PROVENANCE DISCLAIMER
---------------------
All parameters are ASSUMED. This is an architecture prototype.
Cucumber responses differ substantially from tomato; the equations
here are deliberately simplified placeholders.
"""

from __future__ import annotations

from domains.polyhouse.crops.base import (
    CropConstraints,
    CropHarvestModel,
    CropModel,
    CropParameters,
    CropState,
    CropStressModel,
    HarvestResult,
)

STAGE_GERMINATION = "GERMINATION"
STAGE_VEGETATIVE  = "VEGETATIVE"
STAGE_FLOWERING   = "FLOWERING"
STAGE_FRUITING    = "FRUITING"
STAGE_HARVESTING  = "HARVESTING"

_STAGE_THRESHOLDS: list[tuple[float, str]] = [
    (0.0,  STAGE_GERMINATION),
    (7.0,  STAGE_VEGETATIVE),
    (20.0, STAGE_FLOWERING),
    (30.0, STAGE_FRUITING),
    (38.0, STAGE_HARVESTING),
]


def _determine_stage(age_days: float) -> str:
    stage = STAGE_GERMINATION
    for threshold, name in _STAGE_THRESHOLDS:
        if age_days >= threshold:
            stage = name
    return stage


def _temp_response(temp_c: float, t_opt: float) -> float:
    return max(0.0, 1.0 - ((temp_c - t_opt) / 10.0) ** 2)


def _light_response(par: float, l_opt: float) -> float:
    if par <= 0.0:
        return 0.0
    return par / (par + l_opt * 0.5)


def _water_response(water_avail_l: float, w_opt: float) -> float:
    if w_opt <= 0.0:
        return 1.0
    return min(1.0, water_avail_l / w_opt)


class CucumberStressModel(CropStressModel):
    """
    Cucumber stress — high-temperature and low-humidity penalties.
    Cucumber is less heat-tolerant at night (chilling injury below 10°C).
    """

    def calculate_modifier(
        self,
        temperature_c: float,
        humidity_percent: float,
        co2_ppm: float,
        substrate_moisture_percent: float,
        constraints: CropConstraints,
    ) -> float:
        modifier = 1.0
        t = temperature_c
        if t > constraints.temperature.max_val:
            modifier *= 0.2
        elif t > constraints.temperature.optimal_max:
            excess = t - constraints.temperature.optimal_max
            modifier *= max(0.3, 1.0 - excess / 8.0)
        elif t < constraints.temperature.min_val:
            modifier *= 0.05   # chilling injury
        elif t < constraints.temperature.optimal_min:
            deficit = constraints.temperature.optimal_min - t
            modifier *= max(0.2, 1.0 - deficit / 10.0)

        # Cucumber is sensitive to low humidity (powdery mildew risk above 90%)
        if humidity_percent < 50.0:
            deficit = 50.0 - humidity_percent
            modifier *= max(0.4, 1.0 - deficit / 40.0)

        m = substrate_moisture_percent
        if m < constraints.substrate_moisture.min_val:
            modifier *= 0.15
        elif m < constraints.substrate_moisture.optimal_min:
            modifier *= max(0.4, m / constraints.substrate_moisture.optimal_min)

        return max(0.0, min(1.0, modifier))


class CucumberHarvestModel(CropHarvestModel):
    """
    Cucumber has continuous harvesting once in FRUITING/HARVESTING stage.
    Accumulated fruit biomass is partially harvested each assessment.
    """

    def assess(self, state: CropState, parameters: CropParameters) -> HarvestResult:
        is_ready = state.stage in (STAGE_FRUITING, STAGE_HARVESTING)
        fruit_kg = state.extra.get("fruit_biomass_kg", 0.0)
        days_remaining = max(0.0, 38.0 - state.age_days)
        return HarvestResult(
            is_ready=is_ready and fruit_kg > 0.05,
            harvestable_biomass_kg=fruit_kg,
            estimated_days_to_harvest=days_remaining if not is_ready else 0.0,
            confidence="low",
            notes=(
                "Prototype continuous-harvest model. "
                "Fruit biomass accumulates from FRUITING stage."
            ),
        )


class CucumberModel(CropModel):
    """
    Simplified vegetative + fruiting model for cucumber.
    Prototype — not agronomically calibrated.
    """

    _VERSION = "cucumber-v1.0.0-prototype"

    def __init__(self, parameters: CropParameters, constraints: CropConstraints) -> None:
        self._parameters = parameters
        self._constraints = constraints

    @property
    def model_version(self) -> str:
        return self._VERSION

    def parameters(self) -> CropParameters:
        return self._parameters

    def initial_state(self) -> CropState:
        return CropState(
            age_days=0.0,
            stage=STAGE_GERMINATION,
            biomass_kg=self._parameters.value("initial_biomass_kg"),
            harvestable_biomass_kg=0.0,
            crop_stress_index=0.0,
            water_uptake_l_per_day=0.0,
            extra={
                "vegetative_biomass_kg": self._parameters.value("initial_biomass_kg"),
                "fruit_biomass_kg": 0.0,
                "cumulative_fruit_harvested_kg": 0.0,
            },
        )

    def step(
        self,
        current: CropState,
        temperature_c: float,
        humidity_percent: float,
        co2_ppm: float,
        par_umol_m2_s: float,
        substrate_moisture_percent: float,
        water_available_l: float,
        stress_modifier: float,
        dt_days: float,
    ) -> CropState:
        p = self._parameters
        t_opt = p.value("temp_optimum_celsius")
        l_opt = p.value("light_optimum_par")
        w_opt = p.value("water_optimum_l_per_day")
        base_rate = p.value("base_growth_rate_kg_per_day")

        temp_resp = _temp_response(temperature_c, t_opt)
        light_resp = _light_response(par_umol_m2_s, l_opt)
        water_resp = _water_response(water_available_l, w_opt)

        actual_growth = (
            base_rate * temp_resp * light_resp * water_resp * stress_modifier * dt_days
        )

        new_age = current.age_days + dt_days
        new_stage = _determine_stage(new_age)
        new_biomass = current.biomass_kg + actual_growth

        # Partitioning: vegetative-only until FRUITING
        in_fruiting = new_stage in (STAGE_FRUITING, STAGE_HARVESTING)
        fruit_frac = 0.6 if in_fruiting else 0.0
        veg_frac = 1.0 - fruit_frac

        prev_veg = current.extra.get("vegetative_biomass_kg", 0.0)
        prev_fruit = current.extra.get("fruit_biomass_kg", 0.0)
        prev_harvested = current.extra.get("cumulative_fruit_harvested_kg", 0.0)

        new_veg = prev_veg + actual_growth * veg_frac
        fruit_added = actual_growth * fruit_frac

        # Simulate partial harvest each day (continuous harvest crop)
        harvest_rate = 0.3 if in_fruiting else 0.0
        new_fruit = prev_fruit + fruit_added - (prev_fruit * harvest_rate * dt_days)
        new_fruit = max(0.0, new_fruit)
        newly_harvested = (prev_fruit + fruit_added) * harvest_rate * dt_days
        new_harvested = prev_harvested + newly_harvested

        water_uptake = water_resp * w_opt

        return CropState(
            age_days=new_age,
            stage=new_stage,
            biomass_kg=new_biomass,
            harvestable_biomass_kg=new_fruit,
            crop_stress_index=1.0 - stress_modifier,
            water_uptake_l_per_day=water_uptake,
            extra={
                "vegetative_biomass_kg": new_veg,
                "fruit_biomass_kg": new_fruit,
                "cumulative_fruit_harvested_kg": new_harvested,
                "temp_response": temp_resp,
                "light_response": light_resp,
                "water_response": water_resp,
            },
        )
