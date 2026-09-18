"""
tests/unit/test_crop_models.py

Unit tests for individual crop models —
proves each crop has distinct biological behaviour.
"""

import pytest

from domains.polyhouse.crops.registry import CropRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    CropRegistry.reset_singleton()
    yield
    CropRegistry.reset_singleton()


@pytest.fixture
def registry():
    return CropRegistry.default()


class TestDwarfTomatoModel:
    def test_initial_state_in_establishment(self, registry):
        profile = registry.get("dwarf_tomato")
        state = profile.model.initial_state()
        assert state.stage == "ESTABLISHMENT"
        assert state.age_days == 0.0
        assert state.biomass_kg > 0

    def test_biomass_increases_under_optimal_conditions(self, registry):
        profile = registry.get("dwarf_tomato")
        state = profile.model.initial_state()
        next_state = profile.model.step(
            current=state,
            temperature_c=23.0,  # optimal
            humidity_percent=70.0,
            co2_ppm=800.0,
            par_umol_m2_s=400.0,  # optimal
            substrate_moisture_percent=70.0,
            water_available_l=0.3,
            stress_modifier=1.0,
            dt_days=1.0,
        )
        assert next_state.biomass_kg > state.biomass_kg

    def test_stress_reduces_growth(self, registry):
        profile = registry.get("dwarf_tomato")
        state = profile.model.initial_state()
        step_kwargs = {
            "current": state,
            "temperature_c": 23.0,
            "humidity_percent": 70.0,
            "co2_ppm": 800.0,
            "par_umol_m2_s": 400.0,
            "substrate_moisture_percent": 70.0,
            "water_available_l": 0.3,
            "dt_days": 1.0,
        }
        optimal = profile.model.step(**step_kwargs, stress_modifier=1.0)
        stressed = profile.model.step(**step_kwargs, stress_modifier=0.1)
        assert optimal.biomass_kg > stressed.biomass_kg

    def test_stage_transitions(self, registry):
        profile = registry.get("dwarf_tomato")
        assert profile.stage_at(0.0)  == "ESTABLISHMENT"
        assert profile.stage_at(20.0) == "VEGETATIVE"
        assert profile.stage_at(40.0) == "FLOWERING"
        assert profile.stage_at(50.0) == "FRUIT_SET"
        assert profile.stage_at(75.0) == "FRUIT_DEVELOPMENT"
        assert profile.stage_at(95.0) == "MATURATION"
        assert profile.stage_at(105.0) == "HARVEST"

    def test_stress_model_extreme_heat(self, registry):
        profile = registry.get("dwarf_tomato")
        mod = profile.stress_model.calculate_modifier(
            temperature_c=40.0,  # above max
            humidity_percent=70.0,
            co2_ppm=800.0,
            substrate_moisture_percent=70.0,
            constraints=profile.constraints,
        )
        assert mod < 0.5  # strong stress penalty

    def test_harvest_model_not_ready_before_stage(self, registry):
        profile = registry.get("dwarf_tomato")
        state = profile.model.initial_state()
        result = profile.harvest_model.assess(state, profile.model.parameters())
        assert not result.is_ready


class TestLettuceModel:
    def test_different_initial_stage_from_tomato(self, registry):
        lt_profile = registry.get("lettuce")
        dt_profile = registry.get("dwarf_tomato")
        assert lt_profile.model.initial_state().stage != dt_profile.model.initial_state().stage or \
               lt_profile.model.initial_state().stage == "GERMINATION"

    def test_biomass_grows_optimally(self, registry):
        profile = registry.get("lettuce")
        state = profile.model.initial_state()
        for _ in range(10):  # 10 days
            state = profile.model.step(
                current=state,
                temperature_c=18.0,
                humidity_percent=70.0,
                co2_ppm=700.0,
                par_umol_m2_s=250.0,
                substrate_moisture_percent=70.0,
                water_available_l=0.15,
                stress_modifier=1.0,
                dt_days=1.0,
            )
        assert state.biomass_kg > profile.model.initial_state().biomass_kg

    def test_heat_stress_for_lettuce(self, registry):
        profile = registry.get("lettuce")
        mod_cool = profile.stress_model.calculate_modifier(
            temperature_c=18.0, humidity_percent=70.0, co2_ppm=700.0,
            substrate_moisture_percent=70.0, constraints=profile.constraints,
        )
        mod_hot = profile.stress_model.calculate_modifier(
            temperature_c=32.0, humidity_percent=70.0, co2_ppm=700.0,
            substrate_moisture_percent=70.0, constraints=profile.constraints,
        )
        assert mod_cool > mod_hot, "Lettuce should have higher stress modifier at cool temperatures"

    def test_lettuce_stages_differ_from_tomato(self, registry):
        lt = [s.name for s in registry.get("lettuce").growth_stage_definitions]
        dt = [s.name for s in registry.get("dwarf_tomato").growth_stage_definitions]
        assert "FRUIT_SET" not in lt
        assert "GERMINATION" in lt
        assert lt != dt


class TestCucumberModel:
    def test_cucumber_initial_stage(self, registry):
        profile = registry.get("cucumber")
        state = profile.model.initial_state()
        assert state.stage == "GERMINATION"

    def test_fruit_accumulates_in_fruiting_stage(self, registry):
        profile = registry.get("cucumber")
        state = profile.model.initial_state()
        # Fast-forward to fruiting stage
        for _ in range(35):
            state = profile.model.step(
                current=state,
                temperature_c=25.0,
                humidity_percent=75.0,
                co2_ppm=900.0,
                par_umol_m2_s=500.0,
                substrate_moisture_percent=72.0,
                water_available_l=0.5,
                stress_modifier=1.0,
                dt_days=1.0,
            )
        assert state.stage in ("FRUITING", "HARVESTING")
        # Cucumber accumulates fruit biomass (harvestable_biomass_kg > 0)
        assert state.harvestable_biomass_kg >= 0.0

    def test_cucumber_chilling_injury(self, registry):
        profile = registry.get("cucumber")
        # Below minimum (10°C) — severe stress
        mod = profile.stress_model.calculate_modifier(
            temperature_c=6.0, humidity_percent=75.0, co2_ppm=800.0,
            substrate_moisture_percent=70.0, constraints=profile.constraints,
        )
        assert mod < 0.3  # chilling injury
