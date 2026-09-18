"""
domains/polyhouse/crops/lettuce/model.py

Lettuce (Lactuca sativa) growth model — PROTOTYPE.

Lettuce is a purely vegetative crop. Unlike tomato, it has no
flowering or fruiting stages. Growth is driven by leaf-area expansion.

Model approach
--------------
Simplified exponential-linear biomass accumulation (vegetative only).

  vegetative_growth = base_rate × temp_resp × light_resp × water_resp
                    × stress_modifier × dt_days

Harvest is assessed by accumulated biomass reaching a minimum
marketable head weight threshold.

PROVENANCE DISCLAIMER
---------------------
All parameter values in this prototype are ASSUMED unless stated.
This model is intended to demonstrate crop-agnostic architecture,
NOT to produce agronomically accurate predictions.

Growth stages (lettuce-specific, not tomato stages)
----------------------------------------------------
  GERMINATION  → SEEDLING → VEGETATIVE → MATURATION → HARVEST
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
STAGE_SEEDLING = "SEEDLING"
STAGE_VEGETATIVE = "VEGETATIVE"
STAGE_MATURATION = "MATURATION"
STAGE_HARVEST = "HARVEST"

_STAGE_THRESHOLDS: list[tuple[float, str]] = [
    (0.0,  STAGE_GERMINATION),
    (5.0,  STAGE_SEEDLING),
    (12.0, STAGE_VEGETATIVE),
    (32.0, STAGE_MATURATION),
    (38.0, STAGE_HARVEST),
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


class LettuceStressModel(CropStressModel):
    """
    Lettuce is sensitive to heat and drought.
    Bolting (stress-induced premature flowering) is simplified
    as a multiplicative growth penalty at high temperatures.
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
        if t > 28.0:   # bolting risk zone
            excess = t - 28.0
            modifier *= max(0.1, 1.0 - excess / 8.0)
        elif t < constraints.temperature.min_val:
            modifier *= 0.1
        elif t < constraints.temperature.optimal_min:
            deficit = constraints.temperature.optimal_min - t
            modifier *= max(0.3, 1.0 - deficit / 8.0)

        m = substrate_moisture_percent
        if m < 30.0:
            modifier *= 0.2
        elif m < constraints.substrate_moisture.optimal_min:
            modifier *= max(0.4, m / constraints.substrate_moisture.optimal_min)

        return max(0.0, min(1.0, modifier))


class LettuceHarvestModel(CropHarvestModel):
    """
    Lettuce is harvested as a whole head when it reaches minimum weight.
    Marketable fresh weight threshold: ~200 g / head (ASSUMED).
    """

    MIN_HARVEST_BIOMASS_KG = 0.200  # ASSUMED — marketable head weight

    def assess(self, state: CropState, parameters: CropParameters) -> HarvestResult:
        is_ready = (
            state.stage == STAGE_HARVEST
            or state.harvestable_biomass_kg >= self.MIN_HARVEST_BIOMASS_KG
        )
        days_remaining = max(0.0, 38.0 - state.age_days)
        return HarvestResult(
            is_ready=is_ready,
            harvestable_biomass_kg=state.harvestable_biomass_kg,
            estimated_days_to_harvest=days_remaining if not is_ready else 0.0,
            confidence="low",
            notes="Prototype — assumed 200 g marketable head weight threshold.",
        )


class LettuceModel(CropModel):
    """
    Simplified vegetative growth model for lettuce.
    Prototype — not agronomically validated.
    """

    _VERSION = "lettuce-v1.0.0-prototype"

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
            extra={"leaf_biomass_kg": self._parameters.value("initial_biomass_kg")},
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
        leaf_biomass = current.extra.get("leaf_biomass_kg", 0.0) + actual_growth

        # Lettuce: harvestable = all leaf biomass above seedling weight
        harvestable = max(0.0, leaf_biomass - p.value("initial_biomass_kg"))
        water_uptake = water_resp * w_opt

        return CropState(
            age_days=new_age,
            stage=new_stage,
            biomass_kg=new_biomass,
            harvestable_biomass_kg=harvestable,
            crop_stress_index=1.0 - stress_modifier,
            water_uptake_l_per_day=water_uptake,
            extra={
                "leaf_biomass_kg": leaf_biomass,
                "temp_response": temp_resp,
                "light_response": light_resp,
                "water_response": water_resp,
            },
        )
