"""
domains/polyhouse/crops/dwarf_tomato/model.py

Dwarf Tomato growth model — research prototype.

Scientific basis
----------------
Conceptually based on the process-based growth modelling approach
described in:

  Maree et al. (2025). "Autonomous Greenhouse Cultivation of Dwarf Tomato:
  Performance Evaluation of Intelligent Algorithms for Multiple-Sensor
  Feedback." Sensors, 25(14), 4321.

  Fourth Autonomous Greenhouse Challenge (AGC4) — 2023.

PROVENANCE DISCLAIMER
---------------------
The growth model structure follows standard greenhouse crop modelling
conventions (radiation-use efficiency + environmental response functions).
Specific parameter values are ASSUMED unless explicitly labelled LITERATURE
or CALIBRATED. This model has NOT been validated against experimental data.
It is a research prototype intended for simulation architecture development.

Growth formula
--------------
  actual_growth = base_rate × temp_resp × light_resp × water_resp
                × stress_modifier × dt_days

  where each response function ∈ [0.0, 1.0].

Biomass partitioning
--------------------
Early (pre-FLOWERING): 80% vegetative, 20% reproductive
Late  (FLOWERING+):    40% vegetative, 60% reproductive
Fruit ≈ 80% of reproductive biomass at full maturity.
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

# Growth stage names (crop-defined, not engine-defined)
STAGE_ESTABLISHMENT = "ESTABLISHMENT"
STAGE_VEGETATIVE = "VEGETATIVE"
STAGE_FLOWERING = "FLOWERING"
STAGE_FRUIT_SET = "FRUIT_SET"
STAGE_FRUIT_DEVELOPMENT = "FRUIT_DEVELOPMENT"
STAGE_MATURATION = "MATURATION"
STAGE_HARVEST = "HARVEST"

# Stage transitions (age thresholds in days from transplant)
_STAGE_THRESHOLDS: list[tuple[float, str]] = [
    (0.0,  STAGE_ESTABLISHMENT),
    (14.0, STAGE_VEGETATIVE),
    (35.0, STAGE_FLOWERING),
    (45.0, STAGE_FRUIT_SET),
    (60.0, STAGE_FRUIT_DEVELOPMENT),
    (90.0, STAGE_MATURATION),
    (100.0, STAGE_HARVEST),
]


def _determine_stage(age_days: float) -> str:
    stage = STAGE_ESTABLISHMENT
    for threshold, name in _STAGE_THRESHOLDS:
        if age_days >= threshold:
            stage = name
    return stage


def _temp_response(temp_c: float, t_opt: float) -> float:
    """Simplified parabolic temperature response. Returns ∈ [0, 1]."""
    return max(0.0, 1.0 - ((temp_c - t_opt) / 10.0) ** 2)


def _light_response(par: float, l_opt: float) -> float:
    """Michaelis-Menten light response. Returns ∈ [0, 1]."""
    if par <= 0.0:
        return 0.0
    half_sat = l_opt * 0.5
    return par / (par + half_sat)


def _water_response(water_avail_l: float, water_opt_l: float) -> float:
    """Linear water response up to optimum. Returns ∈ [0, 1]."""
    if water_opt_l <= 0.0:
        return 1.0
    return min(1.0, water_avail_l / water_opt_l)


class DwarfTomatoStressModel(CropStressModel):
    """
    Computes multiplicative stress modifier for dwarf tomato.

    Applies temperature extremes and moisture extremes.
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
            modifier *= 0.3
        elif t > constraints.temperature.optimal_max:
            excess = t - constraints.temperature.optimal_max
            modifier *= max(0.3, 1.0 - excess / 10.0)
        elif t < constraints.temperature.min_val:
            modifier *= 0.1
        elif t < constraints.temperature.optimal_min:
            deficit = constraints.temperature.optimal_min - t
            modifier *= max(0.2, 1.0 - deficit / 10.0)

        m = substrate_moisture_percent
        if m < constraints.substrate_moisture.min_val:
            modifier *= 0.2
        elif m < constraints.substrate_moisture.optimal_min:
            deficit = constraints.substrate_moisture.optimal_min - m
            modifier *= max(0.3, 1.0 - deficit / 30.0)
        elif m > constraints.substrate_moisture.max_val:
            modifier *= 0.5

        return max(0.0, min(1.0, modifier))


class DwarfTomatoHarvestModel(CropHarvestModel):
    """
    Harvest readiness assessment for dwarf tomato.

    ASSUMED: harvest is ready when stage == HARVEST and fruit biomass
    represents ≥ 70% of theoretical maximum.
    """

    def assess(self, state: CropState, parameters: CropParameters) -> HarvestResult:
        is_ready = state.stage == STAGE_HARVEST and state.harvestable_biomass_kg > 0
        days_to_harvest = max(0.0, 100.0 - state.age_days) if not is_ready else 0.0
        return HarvestResult(
            is_ready=is_ready,
            harvestable_biomass_kg=state.harvestable_biomass_kg,
            estimated_days_to_harvest=days_to_harvest,
            confidence="low",
            notes="Prototype estimate — not validated against experimental data.",
        )


class DwarfTomatoModel(CropModel):
    """
    Process-based growth model for dwarf tomato.

    Research prototype — see module docstring for provenance disclaimer.
    """

    _VERSION = "dwarf-tomato-v1.0.0-prototype"

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
            stage=STAGE_ESTABLISHMENT,
            biomass_kg=self._parameters.value("initial_biomass_kg"),
            harvestable_biomass_kg=0.0,
            crop_stress_index=0.0,
            water_uptake_l_per_day=0.0,
            extra={
                "vegetative_biomass_kg": self._parameters.value("initial_biomass_kg"),
                "reproductive_biomass_kg": 0.0,
                "fruit_biomass_kg": 0.0,
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

        new_biomass = current.biomass_kg + actual_growth
        new_age = current.age_days + dt_days
        new_stage = _determine_stage(new_age)

        # Biomass partitioning
        if new_stage in (STAGE_ESTABLISHMENT, STAGE_VEGETATIVE):
            veg_frac = p.value("veg_fraction_early")
        else:
            veg_frac = p.value("veg_fraction_late")

        prev_veg = current.extra.get("vegetative_biomass_kg", 0.0)
        prev_rep = current.extra.get("reproductive_biomass_kg", 0.0)
        new_veg = prev_veg + actual_growth * veg_frac
        new_rep = prev_rep + actual_growth * (1.0 - veg_frac)
        new_fruit = new_rep * p.value("fruit_fraction_of_reproductive")

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
                "reproductive_biomass_kg": new_rep,
                "fruit_biomass_kg": new_fruit,
                "temp_response": temp_resp,
                "light_response": light_resp,
                "water_response": water_resp,
            },
        )
