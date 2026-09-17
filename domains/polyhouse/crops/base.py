"""
domains/polyhouse/crops/base.py

Crop-agnostic abstractions for PHYSICA.

Every crop registered in the CropRegistry must conform to these
interfaces. The simulation engine, safety verifier, optimizer, and
experiment runner operate exclusively against these contracts.

No crop-specific logic (tomato, lettuce, cucumber, …) may appear in
this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


class Provenance(str, Enum):
    """Origin classification for a model parameter or measurement."""

    ASSUMED = "ASSUMED"
    LITERATURE = "LITERATURE"
    EXPERIMENTAL = "EXPERIMENTAL"
    CALIBRATED = "CALIBRATED"
    MEASURED = "MEASURED"
    USER_CONFIGURED = "USER_CONFIGURED"
    SIMULATED = "SIMULATED"


@dataclass(frozen=True)
class ParameterMeta:
    """Provenance metadata for a single numeric parameter."""

    value: float
    unit: str
    provenance: Provenance
    reference: str | None = None
    confidence: str = "low"  # low / medium / high
    notes: str | None = None


# ---------------------------------------------------------------------------
# Growth stages
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GrowthStageDefinition:
    """
    A named stage in a crop's development lifecycle.

    The stage name is crop-defined (e.g. "VEGETATIVE", "FRUITING").
    The engine understands only the abstract concept of *a stage*.
    """

    name: str
    min_age_days: float
    description: str = ""


# ---------------------------------------------------------------------------
# Crop state
# ---------------------------------------------------------------------------


@dataclass
class CropState:
    """
    Generic crop state passed between simulation timesteps.

    Crop models may subclass this or extend via `extra` to carry
    crop-specific computed values without polluting the generic API.
    """

    age_days: float
    stage: str                        # matches a GrowthStageDefinition.name
    biomass_kg: float                 # total above-ground dry biomass
    harvestable_biomass_kg: float     # fraction ready for harvest
    crop_stress_index: float          # 0.0 (no stress) – 1.0 (fully stressed)
    water_uptake_l_per_day: float
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Crop parameters
# ---------------------------------------------------------------------------


@dataclass
class CropParameters:
    """
    Parameterisation of a crop model.

    All values carry explicit provenance so the system never
    silently presents assumptions as validated science.
    """

    params: dict[str, ParameterMeta] = field(default_factory=dict)

    def get(self, name: str) -> ParameterMeta:
        if name not in self.params:
            raise KeyError(f"Crop parameter '{name}' not defined")
        return self.params[name]

    def value(self, name: str) -> float:
        return self.get(name).value


# ---------------------------------------------------------------------------
# Crop constraints
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvironmentalRange:
    """Acceptable environmental range for a crop."""

    min_val: float
    max_val: float
    optimal_min: float
    optimal_max: float
    unit: str


@dataclass
class CropConstraints:
    """
    Physical and biological limits specific to a crop.

    Used by the safety verifier and semantic validator.
    The simulation engine uses these to compute stress modifiers.
    """

    temperature: EnvironmentalRange
    humidity: EnvironmentalRange
    co2_ppm: EnvironmentalRange
    substrate_moisture: EnvironmentalRange
    max_water_l_per_day_per_plant: float
    max_plant_density_per_sqm: float
    min_plant_density_per_sqm: float
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Crop harvest model
# ---------------------------------------------------------------------------


@dataclass
class HarvestResult:
    """Output of the harvest assessment for a zone/crop."""

    is_ready: bool
    harvestable_biomass_kg: float
    estimated_days_to_harvest: float
    confidence: str  # low / medium / high
    notes: str = ""


class CropHarvestModel(ABC):
    """
    Determines harvest readiness from the current crop state.

    Crop-specific; must be provided by each crop implementation.
    """

    @abstractmethod
    def assess(self, state: CropState, parameters: CropParameters) -> HarvestResult:
        ...


# ---------------------------------------------------------------------------
# Crop stress model
# ---------------------------------------------------------------------------


class CropStressModel(ABC):
    """
    Computes a stress modifier in [0.0, 1.0] from environmental
    and root-zone conditions.

    1.0 = no stress (optimal).
    0.0 = lethal stress.

    The generic engine multiplies the base growth by this modifier.
    """

    @abstractmethod
    def calculate_modifier(
        self,
        temperature_c: float,
        humidity_percent: float,
        co2_ppm: float,
        substrate_moisture_percent: float,
        constraints: CropConstraints,
    ) -> float:
        ...


# ---------------------------------------------------------------------------
# Crop growth model
# ---------------------------------------------------------------------------


class CropModel(ABC):
    """
    Abstract interface for a crop growth model.

    The simulation engine calls `step()` once per timestep per zone.
    It must not import any crop-specific class directly.
    """

    @abstractmethod
    def initial_state(self) -> CropState:
        """Return the state at planting day 0."""
        ...

    @abstractmethod
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
        """Advance crop state by dt_days."""
        ...

    @abstractmethod
    def parameters(self) -> CropParameters:
        ...

    @property
    @abstractmethod
    def model_version(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Crop profile (top-level identity + metadata)
# ---------------------------------------------------------------------------


@dataclass
class CropProfile:
    """
    Complete description of a crop registered in the CropRegistry.

    This is the single object the registry holds.
    """

    crop_id: str                         # e.g. "dwarf_tomato", "lettuce"
    common_name: str
    scientific_name: str
    cultivar: str | None
    status: str                          # "research" | "prototype" | "production"
    profile_version: str
    growth_stage_definitions: list[GrowthStageDefinition]
    constraints: CropConstraints
    model: CropModel
    harvest_model: CropHarvestModel
    stress_model: CropStressModel
    notes: str = ""

    # ---- convenience helpers -----------------------------------------------

    def stage_at(self, age_days: float) -> str:
        """Return the stage name for a given crop age."""
        current = self.growth_stage_definitions[0].name
        for stage_def in self.growth_stage_definitions:
            if age_days >= stage_def.min_age_days:
                current = stage_def.name
        return current

    def validate(self) -> list[str]:
        """Lightweight self-consistency check. Returns list of issues."""
        issues: list[str] = []
        if not self.growth_stage_definitions:
            issues.append(f"[{self.crop_id}] No growth stages defined.")
        if self.constraints.max_plant_density_per_sqm <= 0:
            issues.append(f"[{self.crop_id}] max_plant_density_per_sqm must be > 0.")
        return issues
