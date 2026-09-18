"""
domains/polyhouse/crops/cucumber/profile.py

Assembles the CropProfile for cucumber.
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

from .model import CucumberHarvestModel, CucumberModel, CucumberStressModel


def build_profile() -> CropProfile:
    parameters = CropParameters(
        params={
            "initial_biomass_kg": ParameterMeta(
                value=0.002, unit="kg/plant", provenance=Provenance.ASSUMED,
                confidence="low",
            ),
            "base_growth_rate_kg_per_day": ParameterMeta(
                value=0.012, unit="kg/plant/day", provenance=Provenance.ASSUMED,
                confidence="low",
                notes="Cucumber grows faster vegetatively than tomato (ASSUMED)",
            ),
            "temp_optimum_celsius": ParameterMeta(
                value=25.0, unit="°C", provenance=Provenance.LITERATURE,
                reference="General greenhouse cucumber literature",
                confidence="medium",
            ),
            "light_optimum_par": ParameterMeta(
                value=500.0, unit="µmol/m²/s", provenance=Provenance.ASSUMED,
                confidence="low",
            ),
            "water_optimum_l_per_day": ParameterMeta(
                value=0.5, unit="L/plant/day", provenance=Provenance.ASSUMED,
                confidence="low",
                notes="Cucumber has high water demand (ASSUMED)",
            ),
        }
    )

    constraints = CropConstraints(
        temperature=EnvironmentalRange(
            min_val=10.0, max_val=35.0,
            optimal_min=22.0, optimal_max=28.0,
            unit="°C",
        ),
        humidity=EnvironmentalRange(
            min_val=50.0, max_val=90.0,
            optimal_min=70.0, optimal_max=85.0,
            unit="%RH",
        ),
        co2_ppm=EnvironmentalRange(
            min_val=300.0, max_val=1500.0,
            optimal_min=700.0, optimal_max=1100.0,
            unit="ppm",
        ),
        substrate_moisture=EnvironmentalRange(
            min_val=40.0, max_val=90.0,
            optimal_min=65.0, optimal_max=80.0,
            unit="%",
        ),
        max_water_l_per_day_per_plant=2.0,
        max_plant_density_per_sqm=4.0,
        min_plant_density_per_sqm=1.5,
    )

    return CropProfile(
        crop_id="cucumber",
        common_name="Cucumber",
        scientific_name="Cucumis sativus",
        cultivar=None,
        status="prototype",
        profile_version="1.0.0",
        growth_stage_definitions=[
            GrowthStageDefinition("GERMINATION",  0.0,  "Seed germination"),
            GrowthStageDefinition("VEGETATIVE",   7.0,  "Rapid vine growth"),
            GrowthStageDefinition("FLOWERING",   20.0,  "Flower initiation"),
            GrowthStageDefinition("FRUITING",    30.0,  "Fruit set — continuous harvest begins"),
            GrowthStageDefinition("HARVESTING",  38.0,  "Peak harvest period"),
        ],
        constraints=constraints,
        model=CucumberModel(parameters, constraints),
        harvest_model=CucumberHarvestModel(),
        stress_model=CucumberStressModel(),
        notes=(
            "Architecture prototype — not agronomically calibrated. "
            "Demonstrates continuous-harvest fruiting model "
            "distinct from tomato (staged) and lettuce (vegetative)."
        ),
    )
