"""
domains/polyhouse/crops/lettuce/profile.py

Assembles the CropProfile for lettuce.
"""

from domains.polyhouse.crops.base import (
    CropConstraints,
    CropParameters,
    CropProfile,
    EnvironmentalRange,
    GrowthStageDefinition,
    ParameterMeta,
    Provenance,
)

from .model import LettuceHarvestModel, LettuceModel, LettuceStressModel


def build_profile() -> CropProfile:
    parameters = CropParameters(
        params={
            "initial_biomass_kg": ParameterMeta(
                value=0.001, unit="kg/plant", provenance=Provenance.ASSUMED,
                confidence="low", notes="Seedling weight at transplant",
            ),
            "base_growth_rate_kg_per_day": ParameterMeta(
                value=0.006, unit="kg/plant/day", provenance=Provenance.ASSUMED,
                confidence="low",
                notes="~200 g head over ~33 growing days under optimal conditions",
            ),
            "temp_optimum_celsius": ParameterMeta(
                value=18.0, unit="°C", provenance=Provenance.LITERATURE,
                reference="General greenhouse lettuce literature",
                confidence="medium",
            ),
            "light_optimum_par": ParameterMeta(
                value=250.0, unit="µmol/m²/s", provenance=Provenance.ASSUMED,
                confidence="low",
                notes="Lettuce is shade-tolerant vs tomato",
            ),
            "water_optimum_l_per_day": ParameterMeta(
                value=0.15, unit="L/plant/day", provenance=Provenance.ASSUMED,
                confidence="low",
            ),
        }
    )

    constraints = CropConstraints(
        temperature=EnvironmentalRange(
            min_val=4.0, max_val=30.0,
            optimal_min=15.0, optimal_max=22.0,
            unit="°C",
        ),
        humidity=EnvironmentalRange(
            min_val=40.0, max_val=90.0,
            optimal_min=60.0, optimal_max=80.0,
            unit="%RH",
        ),
        co2_ppm=EnvironmentalRange(
            min_val=300.0, max_val=1200.0,
            optimal_min=500.0, optimal_max=900.0,
            unit="ppm",
        ),
        substrate_moisture=EnvironmentalRange(
            min_val=40.0, max_val=90.0,
            optimal_min=60.0, optimal_max=80.0,
            unit="%",
        ),
        max_water_l_per_day_per_plant=0.5,
        max_plant_density_per_sqm=30.0,
        min_plant_density_per_sqm=10.0,
    )

    return CropProfile(
        crop_id="lettuce",
        common_name="Lettuce",
        scientific_name="Lactuca sativa",
        cultivar=None,
        status="prototype",
        profile_version="1.0.0",
        growth_stage_definitions=[
            GrowthStageDefinition("GERMINATION",  0.0,  "Seed germination"),
            GrowthStageDefinition("SEEDLING",     5.0,  "First true leaves"),
            GrowthStageDefinition("VEGETATIVE",  12.0,  "Rapid leaf expansion"),
            GrowthStageDefinition("MATURATION",  32.0,  "Head formation / weight gain"),
            GrowthStageDefinition("HARVEST",     38.0,  "Marketable head weight reached"),
        ],
        constraints=constraints,
        model=LettuceModel(parameters, constraints),
        harvest_model=LettuceHarvestModel(),
        stress_model=LettuceStressModel(),
        notes=(
            "Architecture prototype — not agronomically calibrated. "
            "Demonstrates crop-agnostic design: different stages, "
            "vegetative-only biomass, heat-bolting stress logic."
        ),
    )
