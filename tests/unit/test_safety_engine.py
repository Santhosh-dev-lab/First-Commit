"""
tests/unit/test_safety_engine.py

Tests for the crop-independent safety verification engine.
"""

import pytest

from core.safety.engine import SafetyVerifier
from domains.polyhouse.crops.registry import CropRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    CropRegistry.reset_singleton()
    yield
    CropRegistry.reset_singleton()


@pytest.fixture
def registry():
    return CropRegistry.default()


@pytest.fixture
def verifier(registry):
    return SafetyVerifier.default(registry)


class TestGlobalSafetyRules:
    def test_safe_nominal_state(self, verifier):
        result = verifier.verify({
            "temperature_c": 22.0,
            "humidity_percent": 72.0,
            "co2_ppm": 800.0,
            "tank_volume_liters": 5000.0,
        })
        assert result.is_safe
        assert result.violations == []

    def test_critical_over_max_temp(self, verifier):
        result = verifier.verify({"temperature_c": 50.0})
        assert not result.is_safe
        ids = [v.rule_id for v in result.violations]
        assert "GLOBAL_MAX_TEMP" in ids

    def test_critical_below_frost(self, verifier):
        result = verifier.verify({"temperature_c": 0.0})
        assert not result.is_safe
        assert any(v.rule_id == "GLOBAL_MIN_TEMP" for v in result.violations)

    def test_critical_co2_over_limit(self, verifier):
        result = verifier.verify({"co2_ppm": 6000.0})
        assert not result.is_safe
        assert any(v.rule_id == "GLOBAL_MAX_CO2" for v in result.violations)

    def test_warning_high_humidity(self, verifier):
        result = verifier.verify({"humidity_percent": 99.0})
        # Should be a warning, not a critical violation (is_safe = True)
        assert result.is_safe
        assert any(v.rule_id == "GLOBAL_MAX_HUMIDITY" for v in result.warnings)

    def test_warning_low_water(self, verifier):
        result = verifier.verify({"tank_volume_liters": 50.0})
        assert result.is_safe  # warning only
        assert any(v.rule_id == "LOW_WATER" for v in result.warnings)


class TestCropSpecificRules:
    def test_crop_max_temp_warning_tomato(self, verifier):
        # 40°C exceeds tomato max (38°C) → warning
        result = verifier.verify(
            {"temperature_c": 40.0},
            zone_id="z1",
            crop_id="dwarf_tomato",
        )
        assert result.is_safe   # not critical globally at 40°C
        assert any(v.rule_id == "CROP_MAX_TEMP" for v in result.warnings)

    def test_crop_min_temp_warning_cucumber(self, verifier):
        # 8°C is below cucumber min (10°C) → crop warning
        result = verifier.verify(
            {"temperature_c": 8.0},
            zone_id="z3",
            crop_id="cucumber",
        )
        assert any(v.rule_id == "CROP_MIN_TEMP" for v in result.warnings)

    def test_unknown_crop_id_does_not_crash(self, verifier):
        # Should not raise — just skip crop rules
        result = verifier.verify(
            {"temperature_c": 22.0},
            crop_id="nonexistent_crop",
        )
        assert result is not None

    def test_verifier_is_crop_independent(self, verifier):
        """
        The same verifier instance handles any crop correctly —
        crop logic comes from the registry, not from the verifier code.
        """
        for crop_id in ["dwarf_tomato", "lettuce", "cucumber"]:
            result = verifier.verify(
                {"temperature_c": 22.0, "humidity_percent": 70.0},
                zone_id="z1",
                crop_id=crop_id,
            )
            assert result is not None  # No crash for any crop


class TestSafetyResultStructure:
    def test_multiple_violations_collected(self, verifier):
        result = verifier.verify({
            "temperature_c": 50.0,  # GLOBAL_MAX_TEMP
            "co2_ppm": 6000.0,      # GLOBAL_MAX_CO2
        })
        assert not result.is_safe
        assert len(result.violations) >= 2

    def test_violation_has_context(self, verifier):
        result = verifier.verify({"temperature_c": 50.0}, zone_id="z1", crop_id="lettuce")
        v = next(v for v in result.violations if v.rule_id == "GLOBAL_MAX_TEMP")
        assert v.actual_value == 50.0
        assert v.limit_value == 45.0
