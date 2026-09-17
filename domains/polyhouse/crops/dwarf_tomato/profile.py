"""
domains/polyhouse/crops/dwarf_tomato/profile.py

Assembles the complete CropProfile for dwarf tomato and exposes
`build_profile()` — the function called by CropRegistry._register_builtins().
"""

from domains.polyhouse.crops.base import CropProfile, GrowthStageDefinition

from .constraints import build_constraints
from .model import (
    DwarfTomatoHarvestModel,
    DwarfTomatoModel,
    DwarfTomatoStressModel,
)
from .parameters import build_parameters


def build_profile() -> CropProfile:
    parameters = build_parameters()
    constraints = build_constraints()

    return CropProfile(
        crop_id="dwarf_tomato",
        common_name="Dwarf Tomato",
        scientific_name="Solanum lycopersicum var. cerasiforme (dwarf)",
        cultivar="AGC4 trial cultivar (unspecified)",
        status="research",
        profile_version="1.0.0",
        growth_stage_definitions=[
            GrowthStageDefinition("ESTABLISHMENT",    0.0,   "Transplant to root establishment"),
            GrowthStageDefinition("VEGETATIVE",      14.0,   "Rapid leaf and stem growth"),
            GrowthStageDefinition("FLOWERING",       35.0,   "Flower initiation and anthesis"),
            GrowthStageDefinition("FRUIT_SET",       45.0,   "Pollination and early fruit development"),
            GrowthStageDefinition("FRUIT_DEVELOPMENT", 60.0, "Rapid fruit cell expansion"),
            GrowthStageDefinition("MATURATION",      90.0,   "Fruit ripening and colour change"),
            GrowthStageDefinition("HARVEST",        100.0,   "Harvest-ready"),
        ],
        constraints=constraints,
        model=DwarfTomatoModel(parameters, constraints),
        harvest_model=DwarfTomatoHarvestModel(),
        stress_model=DwarfTomatoStressModel(),
        notes=(
            "Research prototype. Parameters derived from published literature "
            "(Maree et al. 2025, Sensors 25(14):4321) and assumptions. "
            "Not validated against independent experimental data. "
            "Do not use for production decision-making."
        ),
    )
