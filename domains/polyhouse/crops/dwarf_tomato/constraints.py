"""
domains/polyhouse/crops/dwarf_tomato/constraints.py

Biological and operational constraints for dwarf tomato.

Used by:
  - SemanticValidator (pre-flight checks)
  - SafetyVerifier    (reject unsafe control plans)
  - SimulationEngine  (stress calculation inputs)
"""

from domains.polyhouse.crops.base import CropConstraints, EnvironmentalRange


def build_constraints() -> CropConstraints:
    return CropConstraints(
        temperature=EnvironmentalRange(
            min_val=8.0,
            max_val=38.0,
            optimal_min=20.0,
            optimal_max=26.0,
            unit="°C",
        ),
        humidity=EnvironmentalRange(
            min_val=40.0,
            max_val=95.0,
            optimal_min=60.0,
            optimal_max=80.0,
            unit="%RH",
        ),
        co2_ppm=EnvironmentalRange(
            min_val=300.0,
            max_val=1500.0,
            optimal_min=600.0,
            optimal_max=1000.0,
            unit="ppm",
        ),
        substrate_moisture=EnvironmentalRange(
            min_val=30.0,
            max_val=95.0,
            optimal_min=60.0,
            optimal_max=80.0,
            unit="%",
        ),
        max_water_l_per_day_per_plant=1.5,
        max_plant_density_per_sqm=25.0,
        min_plant_density_per_sqm=5.0,
    )
