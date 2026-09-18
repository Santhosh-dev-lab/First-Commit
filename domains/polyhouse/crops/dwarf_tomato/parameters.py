"""
domains/polyhouse/crops/dwarf_tomato/parameters.py

Dwarf Tomato model parameters with explicit provenance.

IMPORTANT: Values labelled LITERATURE are derived from published
research references (Maree et al., 2025; Fourth Autonomous Greenhouse
Challenge). They are NOT independently validated constants.

Values labelled ASSUMED are engineering placeholders pending
calibration against experimental data.

DO NOT treat these as universal agricultural truth.
"""

from domains.polyhouse.crops.base import CropParameters, ParameterMeta, Provenance


def build_parameters() -> CropParameters:
    return CropParameters(
        params={
            # ---------------------------------------------------------------
            # Plant density (plants / m²)
            # Reference: Maree et al. 2025 — AGC4 dwarf tomato trial
            # ---------------------------------------------------------------
            "plant_density_per_sqm": ParameterMeta(
                value=15.0,
                unit="plants/m²",
                provenance=Provenance.LITERATURE,
                reference="Maree et al. 2025 — Sensors 25(14):4321",
                confidence="medium",
                notes="AGC4 experimental configuration",
            ),
            # ---------------------------------------------------------------
            # Initial biomass at transplant (kg per plant)
            # ---------------------------------------------------------------
            "initial_biomass_kg": ParameterMeta(
                value=0.002,
                unit="kg/plant",
                provenance=Provenance.ASSUMED,
                confidence="low",
                notes="Typical transplant seedling fresh weight estimate",
            ),
            # ---------------------------------------------------------------
            # Base growth rate (kg dry biomass / plant / day under optimal)
            # ---------------------------------------------------------------
            "base_growth_rate_kg_per_day": ParameterMeta(
                value=0.010,
                unit="kg/plant/day",
                provenance=Provenance.ASSUMED,
                confidence="low",
                notes=(
                    "Placeholder pending calibration against AGC4 dataset. "
                    "Literature suggests dwarf tomato total biomass at harvest ~0.5-0.8 kg/plant "
                    "over ~90 growing days."
                ),
            ),
            # ---------------------------------------------------------------
            # Temperature optimum (°C)
            # ---------------------------------------------------------------
            "temp_optimum_celsius": ParameterMeta(
                value=23.0,
                unit="°C",
                provenance=Provenance.LITERATURE,
                reference="Maree et al. 2025",
                confidence="medium",
                notes="Day temperature setpoint in AGC4 trial",
            ),
            # ---------------------------------------------------------------
            # Light optimum (µmol/m²/s PAR)
            # ---------------------------------------------------------------
            "light_optimum_par": ParameterMeta(
                value=400.0,
                unit="µmol/m²/s",
                provenance=Provenance.LITERATURE,
                reference="Maree et al. 2025",
                confidence="medium",
            ),
            # ---------------------------------------------------------------
            # Optimal water supply (litres / plant / day)
            # ---------------------------------------------------------------
            "water_optimum_l_per_day": ParameterMeta(
                value=0.3,
                unit="L/plant/day",
                provenance=Provenance.ASSUMED,
                confidence="low",
                notes="Placeholder — AGC4 reports total water per m², not per plant",
            ),
            # ---------------------------------------------------------------
            # Vegetative partitioning fraction (pre-flowering)
            # ---------------------------------------------------------------
            "veg_fraction_early": ParameterMeta(
                value=0.80,
                unit="fraction",
                provenance=Provenance.ASSUMED,
                confidence="low",
            ),
            # ---------------------------------------------------------------
            # Vegetative partitioning fraction (post-flowering)
            # ---------------------------------------------------------------
            "veg_fraction_late": ParameterMeta(
                value=0.40,
                unit="fraction",
                provenance=Provenance.ASSUMED,
                confidence="low",
            ),
            # ---------------------------------------------------------------
            # Fruit biomass fraction of reproductive biomass at maturity
            # ---------------------------------------------------------------
            "fruit_fraction_of_reproductive": ParameterMeta(
                value=0.80,
                unit="fraction",
                provenance=Provenance.ASSUMED,
                confidence="low",
            ),
        }
    )
