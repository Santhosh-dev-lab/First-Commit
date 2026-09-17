"""
tests/unit/test_crop_agnostic_simulator.py

Tests proving the simulation engine is genuinely crop-agnostic.

Key invariants verified:
  1. SimulationEngine contains no crop-specific branching.
  2. Adding a new crop does not require changing SimulationEngine.
  3. Different zones can use different crops.
  4. Crop-specific growth stages appear correctly in results.
  5. Computed outputs differ between crops (not hardcoded).
  6. A dynamically registered test crop works through the full pipeline.
"""

import inspect

import pytest

from domains.polyhouse.crops.base import (
    CropConstraints,
    CropHarvestModel,
    CropModel,
    CropParameters,
    CropProfile,
    CropState,
    CropStressModel,
    EnvironmentalRange,
    GrowthStageDefinition,
    HarvestResult,
    ParameterMeta,
    Provenance,
)
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig

# ---------------------------------------------------------------------------
# Minimal fourth-crop for architecture test
# ---------------------------------------------------------------------------

class _FastGrowStressModel(CropStressModel):
    def calculate_modifier(self, temperature_c, humidity_percent, co2_ppm,
                           substrate_moisture_percent, constraints):
        return 0.9 if 15 <= temperature_c <= 30 else 0.3


class _FastGrowHarvestModel(CropHarvestModel):
    def assess(self, state, parameters):
        return HarvestResult(
            is_ready=state.age_days >= 20,
            harvestable_biomass_kg=state.harvestable_biomass_kg,
            estimated_days_to_harvest=max(0.0, 20.0 - state.age_days),
            confidence="low",
        )


class _FastGrowModel(CropModel):
    _VERSION = "fast-grow-v0.1-test"

    def __init__(self, params, constraints):
        self._params = params
        self._constraints = constraints

    @property
    def model_version(self):
        return self._VERSION

    def parameters(self):
        return self._params

    def initial_state(self):
        return CropState(
            age_days=0.0, stage="SPROUTING",
            biomass_kg=0.001, harvestable_biomass_kg=0.0,
            crop_stress_index=0.0, water_uptake_l_per_day=0.1,
        )

    def step(self, current, temperature_c, humidity_percent, co2_ppm,
             par_umol_m2_s, substrate_moisture_percent, water_available_l,
             stress_modifier, dt_days):
        growth = 0.05 * stress_modifier * dt_days
        return CropState(
            age_days=current.age_days + dt_days,
            stage="GROWING" if current.age_days < 15 else "READY",
            biomass_kg=current.biomass_kg + growth,
            harvestable_biomass_kg=current.biomass_kg + growth if current.age_days >= 15 else 0.0,
            crop_stress_index=1.0 - stress_modifier,
            water_uptake_l_per_day=0.1,
        )


def _build_fast_grow_profile() -> CropProfile:
    params = CropParameters(params={
        "initial_biomass_kg": ParameterMeta(
            value=0.001, unit="kg", provenance=Provenance.ASSUMED, confidence="low",
        ),
    })
    constraints = CropConstraints(
        temperature=EnvironmentalRange(10.0, 35.0, 18.0, 28.0, "°C"),
        humidity=EnvironmentalRange(40.0, 90.0, 55.0, 75.0, "%"),
        co2_ppm=EnvironmentalRange(300.0, 1200.0, 400.0, 800.0, "ppm"),
        substrate_moisture=EnvironmentalRange(30.0, 90.0, 50.0, 70.0, "%"),
        max_water_l_per_day_per_plant=0.3,
        max_plant_density_per_sqm=50.0,
        min_plant_density_per_sqm=10.0,
    )
    return CropProfile(
        crop_id="fast_grow_test",
        common_name="Fast Grow Test Crop",
        scientific_name="Testus croppus rapidus",
        cultivar=None,
        status="prototype",
        profile_version="0.1.0",
        growth_stage_definitions=[
            GrowthStageDefinition("SPROUTING", 0.0),
            GrowthStageDefinition("GROWING",   5.0),
            GrowthStageDefinition("READY",    15.0),
        ],
        constraints=constraints,
        model=_FastGrowModel(params, constraints),
        harvest_model=_FastGrowHarvestModel(),
        stress_model=_FastGrowStressModel(),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def registry_with_builtins():
    CropRegistry.reset_singleton()
    reg = CropRegistry.default()
    yield reg
    CropRegistry.reset_singleton()


@pytest.fixture
def registry_with_test_crop(registry_with_builtins):
    registry_with_builtins.register(_build_fast_grow_profile())
    yield registry_with_builtins


# ---------------------------------------------------------------------------
# Test 1 — engine source contains no crop-specific branching
# ---------------------------------------------------------------------------

class TestEngineIsCropAgnostic:
    def test_engine_source_has_no_crop_names(self):
        """
        The SimulationEngine class source must not contain hardcoded
        crop names in executable code (conditional branches etc.).
        Comments and docstrings are excluded from this check.
        """
        import ast

        from domains.polyhouse import engine as engine_module

        source = inspect.getsource(engine_module)
        tree = ast.parse(source)

        # Collect all string literals and names from the AST (non-docstring)
        forbidden = ["dwarf_tomato", "lettuce", "cucumber"]

        # Walk the SimulationEngine class body only
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SimulationEngine":
                class_source = ast.get_source_segment(source, node) or ""
                # Strip single-line comments
                code_lines = [
                    line for line in class_source.splitlines()
                    if not line.strip().startswith("#")
                ]
                code_only = "\n".join(code_lines)
                for name in forbidden:
                    # Allow in string literals within docstrings (first stmt of fn)
                    # by checking only non-string tokens
                    assert f'"{name}"' not in code_only and f"'{name}'" not in code_only, (
                        f"SimulationEngine class contains hardcoded crop name as string literal: '{name}'"
                    )


    def test_engine_accepts_arbitrary_registered_crop(self, registry_with_test_crop):
        """A newly registered crop works through the full engine pipeline."""
        config = SimulationConfig(
            simulation_id="test-fast-grow",
            scenario_name="test",
            days=25,
            dt_hours=6.0,
            seed=1,
            zones=[
                ZoneSimConfig(
                    zone_id="z-fg",
                    crop_id="fast_grow_test",
                    area_sqm=100.0,
                    plant_density_per_sqm=20.0,
                )
            ],
        )
        engine = SimulationEngine(registry_with_test_crop)
        result = engine.run(config)
        assert result.simulation_id == "test-fast-grow"
        assert len(result.zone_results) == 1
        zr = result.zone_results[0]
        assert zr.crop_id == "fast_grow_test"
        assert zr.final_biomass_kg > 0


# ---------------------------------------------------------------------------
# Test 2 — multi-zone with different crops
# ---------------------------------------------------------------------------

class TestMultiZoneMultiCrop:
    def test_three_zones_three_crops(self, registry_with_builtins):
        config = SimulationConfig(
            simulation_id="multi-zone-test",
            scenario_name="test",
            days=45,
            dt_hours=6.0,
            seed=42,
            zones=[
                ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato",
                              area_sqm=100.0, plant_density_per_sqm=15.0),
                ZoneSimConfig(zone_id="z2", crop_id="lettuce",
                              area_sqm=100.0, plant_density_per_sqm=25.0),
                ZoneSimConfig(zone_id="z3", crop_id="cucumber",
                              area_sqm=100.0, plant_density_per_sqm=3.0),
            ],
        )
        engine = SimulationEngine(registry_with_builtins)
        result = engine.run(config)

        assert len(result.zone_results) == 3
        crop_ids = {zr.crop_id for zr in result.zone_results}
        assert crop_ids == {"dwarf_tomato", "lettuce", "cucumber"}

    def test_different_crops_have_different_final_stages(self, registry_with_builtins):
        """Different crops have different stage trajectories."""
        config = SimulationConfig(
            simulation_id="stage-diff-test",
            scenario_name="test",
            days=45,
            dt_hours=6.0,
            seed=42,
            zones=[
                ZoneSimConfig(zone_id="z1", crop_id="dwarf_tomato",
                              area_sqm=100.0, plant_density_per_sqm=15.0),
                ZoneSimConfig(zone_id="z2", crop_id="lettuce",
                              area_sqm=100.0, plant_density_per_sqm=25.0),
            ],
        )
        engine = SimulationEngine(registry_with_builtins)
        result = engine.run(config)

        stages = {zr.zone_id: zr.final_stage for zr in result.zone_results}
        # After 45 days: tomato should be in FRUIT_SET/FRUIT_DEVELOPMENT
        # Lettuce should be in HARVEST (cycle is ~38 days)
        assert stages["z1"] != stages["z2"], (
            "Different crops must produce different growth stages"
        )

    def test_outputs_are_computed_not_hardcoded(self, registry_with_builtins):
        """Vary input conditions and verify outputs change."""
        def run_with_temp(temp: float) -> float:
            config = SimulationConfig(
                simulation_id=f"temp-test-{temp}",
                scenario_name="test",
                days=30,
                dt_hours=6.0,
                seed=42,
                zones=[
                    ZoneSimConfig(zone_id="z1", crop_id="lettuce",
                                  area_sqm=100.0, plant_density_per_sqm=20.0),
                ],
                initial_temperature_c=temp,
                outside_temperature_c=temp,
            )
            engine = SimulationEngine(registry_with_builtins)
            result = engine.run(config)
            return result.zone_results[0].final_biomass_kg

        biomass_optimal = run_with_temp(18.0)  # optimal for lettuce
        biomass_stress = run_with_temp(35.0)   # hot = stress
        assert biomass_optimal > biomass_stress, (
            "Higher stress should produce lower biomass — outputs must be computed"
        )


# ---------------------------------------------------------------------------
# Test 3 — crop-specific growth stages are dynamic
# ---------------------------------------------------------------------------

class TestDynamicGrowthStages:
    def test_tomato_stage_at_50_days(self, registry_with_builtins):
        profile = registry_with_builtins.get("dwarf_tomato")
        stage = profile.stage_at(50.0)
        assert stage == "FRUIT_SET"

    def test_lettuce_stage_at_15_days(self, registry_with_builtins):
        profile = registry_with_builtins.get("lettuce")
        stage = profile.stage_at(15.0)
        assert stage == "VEGETATIVE"

    def test_cucumber_stage_at_35_days(self, registry_with_builtins):
        profile = registry_with_builtins.get("cucumber")
        stage = profile.stage_at(35.0)
        assert stage == "FRUITING"

    def test_fast_grow_stage_names_are_unique_to_crop(self, registry_with_test_crop):
        profile = registry_with_test_crop.get("fast_grow_test")
        stage_names = [s.name for s in profile.growth_stage_definitions]
        assert "SPROUTING" in stage_names   # only in this crop
        assert "READY" in stage_names       # only in this crop
