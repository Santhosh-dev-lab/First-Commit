"""
tests/unit/test_crop_registry.py

Tests for CropRegistry — proves crop registration, lookup, isolation.
"""

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
from domains.polyhouse.crops.registry import CropNotFoundError, CropRegistry

# ---------------------------------------------------------------------------
# Minimal mock crop (used to test registry without real crop code)
# ---------------------------------------------------------------------------

class _MockStressModel(CropStressModel):
    def calculate_modifier(self, temperature_c, humidity_percent, co2_ppm,
                           substrate_moisture_percent, constraints):
        return 1.0


class _MockHarvestModel(CropHarvestModel):
    def assess(self, state, parameters):
        return HarvestResult(
            is_ready=state.age_days >= 30,
            harvestable_biomass_kg=state.harvestable_biomass_kg,
            estimated_days_to_harvest=max(0.0, 30.0 - state.age_days),
            confidence="low",
        )


class _MockCropModel(CropModel):
    _VERSION = "mock-crop-v0.1"

    def __init__(self, params: CropParameters, constraints: CropConstraints):
        self._params = params
        self._constraints = constraints

    @property
    def model_version(self):
        return self._VERSION

    def parameters(self):
        return self._params

    def initial_state(self):
        return CropState(
            age_days=0.0, stage="GERMINATION",
            biomass_kg=0.001, harvestable_biomass_kg=0.0,
            crop_stress_index=0.0, water_uptake_l_per_day=0.0,
        )

    def step(self, current, temperature_c, humidity_percent, co2_ppm,
             par_umol_m2_s, substrate_moisture_percent, water_available_l,
             stress_modifier, dt_days):
        return CropState(
            age_days=current.age_days + dt_days,
            stage="VEGETATIVE",
            biomass_kg=current.biomass_kg + 0.001 * stress_modifier * dt_days,
            harvestable_biomass_kg=0.0,
            crop_stress_index=1.0 - stress_modifier,
            water_uptake_l_per_day=0.05,
        )


def _build_mock_profile(crop_id: str = "mock_crop") -> CropProfile:
    params = CropParameters(params={
        "initial_biomass_kg": ParameterMeta(
            value=0.001, unit="kg", provenance=Provenance.ASSUMED, confidence="low",
        ),
    })
    constraints = CropConstraints(
        temperature=EnvironmentalRange(5.0, 35.0, 18.0, 25.0, "°C"),
        humidity=EnvironmentalRange(40.0, 90.0, 60.0, 80.0, "%"),
        co2_ppm=EnvironmentalRange(300.0, 1200.0, 500.0, 900.0, "ppm"),
        substrate_moisture=EnvironmentalRange(30.0, 90.0, 55.0, 75.0, "%"),
        max_water_l_per_day_per_plant=0.5,
        max_plant_density_per_sqm=20.0,
        min_plant_density_per_sqm=5.0,
    )
    return CropProfile(
        crop_id=crop_id,
        common_name="Mock Crop",
        scientific_name="Mockus croppus",
        cultivar=None,
        status="prototype",
        profile_version="0.1.0",
        growth_stage_definitions=[
            GrowthStageDefinition("GERMINATION", 0.0),
            GrowthStageDefinition("VEGETATIVE", 5.0),
            GrowthStageDefinition("HARVEST", 30.0),
        ],
        constraints=constraints,
        model=_MockCropModel(params, constraints),
        harvest_model=_MockHarvestModel(),
        stress_model=_MockStressModel(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture
def fresh_registry():
    """Always use an isolated registry instance — never the singleton."""
    return CropRegistry()


class TestCropRegistryBasics:
    def test_register_and_get(self, fresh_registry):
        profile = _build_mock_profile()
        fresh_registry.register(profile)
        assert fresh_registry.get("mock_crop") is profile

    def test_exists(self, fresh_registry):
        assert not fresh_registry.exists("mock_crop")
        fresh_registry.register(_build_mock_profile())
        assert fresh_registry.exists("mock_crop")

    def test_list_empty(self, fresh_registry):
        assert fresh_registry.list() == []

    def test_list_sorted(self, fresh_registry):
        fresh_registry.register(_build_mock_profile("zebra"))
        fresh_registry.register(_build_mock_profile("apple"))
        fresh_registry.register(_build_mock_profile("mango"))
        assert fresh_registry.list() == ["apple", "mango", "zebra"]

    def test_get_missing_raises(self, fresh_registry):
        with pytest.raises(CropNotFoundError):
            fresh_registry.get("nonexistent_crop")

    def test_duplicate_raises_without_overwrite(self, fresh_registry):
        fresh_registry.register(_build_mock_profile())
        with pytest.raises(ValueError):
            fresh_registry.register(_build_mock_profile())

    def test_overwrite_allowed(self, fresh_registry):
        fresh_registry.register(_build_mock_profile())
        fresh_registry.register(_build_mock_profile(), overwrite=True)
        assert fresh_registry.exists("mock_crop")


class TestBuiltinCrops:
    """Tests against the singleton with real built-in crops."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        CropRegistry.reset_singleton()
        yield
        CropRegistry.reset_singleton()

    def test_builtins_registered(self) -> None:
        registry = CropRegistry.default()
        assert registry.exists("dwarf_tomato")
        assert registry.exists("lettuce")
        assert registry.exists("cucumber")

    def test_three_distinct_crops(self) -> None:
        registry = CropRegistry.default()
        crops = registry.list()
        assert len(crops) >= 3

    def test_crops_have_different_stages(self) -> None:
        registry = CropRegistry.default()
        dt_stages = [s.name for s in registry.get("dwarf_tomato").growth_stage_definitions]
        lt_stages = [s.name for s in registry.get("lettuce").growth_stage_definitions]
        cu_stages = [s.name for s in registry.get("cucumber").growth_stage_definitions]
        # Each crop has unique stage names
        assert dt_stages != lt_stages
        assert lt_stages != cu_stages
        assert "FRUIT_SET" in dt_stages          # tomato-specific
        assert "GERMINATION" in lt_stages         # lettuce
        assert "FRUITING" in cu_stages            # cucumber-specific

    def test_dynamic_registration_of_new_crop(self) -> None:
        """
        Proves a test crop can be registered without modifying core code.
        This is the PHASE 23 'fourth-crop test'.
        """
        registry = CropRegistry.default()
        mock = _build_mock_profile("strawberry_test")
        registry.register(mock)
        assert registry.exists("strawberry_test")
        profile = registry.get("strawberry_test")
        assert profile.crop_id == "strawberry_test"
        # Remove it after test
        registry._profiles.pop("strawberry_test")
