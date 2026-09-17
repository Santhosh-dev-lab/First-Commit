"""
core/experiments/runner.py

PHYSICA Experiment Framework.

An Experiment pairs a SimulationConfig with metadata needed for
research reproducibility. The ExperimentRunner executes one or more
experiments and compares their results.

Design principles
-----------------
- Crop-independent: works with any registered crop.
- Every experiment records git SHA, model versions, parameters, seed.
- Results are comparable across different crops using crop-appropriate
  normalised metrics (e.g. kg/m² rather than raw kg).
"""

from __future__ import annotations

import datetime
import hashlib
import subprocess
from dataclasses import dataclass
from datetime import timezone

from pydantic import BaseModel

from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationResult,
)

# ---------------------------------------------------------------------------
# Reproducibility metadata
# ---------------------------------------------------------------------------


def _get_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        return result.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


# ---------------------------------------------------------------------------
# Experiment config
# ---------------------------------------------------------------------------


class ExperimentConfig(BaseModel):
    """
    Complete description of a reproducible PHYSICA experiment.

    Every field that affects the simulation outcome is recorded.
    """
    experiment_id: str
    description: str
    simulation_config: SimulationConfig

    # Metadata for reproducibility
    researcher: str = "unknown"
    tags: list[str] = []

    class Config:
        arbitrary_types_allowed = True


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@dataclass
class ZoneMetrics:
    zone_id: str
    crop_id: str
    total_harvestable_kg: float
    area_sqm: float
    yield_kg_per_sqm: float
    total_water_l: float
    water_efficiency_kg_per_l: float
    average_stress_index: float
    final_stage: str
    harvest_ready: bool


@dataclass
class ExperimentMetrics:
    total_harvestable_kg: float
    total_water_l: float
    total_energy_kwh: float
    average_stress: float
    constraint_violations: int
    zone_metrics: list[ZoneMetrics]
    water_efficiency_kg_per_l: float


# ---------------------------------------------------------------------------
# Experiment result
# ---------------------------------------------------------------------------


@dataclass
class ExperimentResult:
    experiment_id: str
    description: str
    git_sha: str
    timestamp: str
    simulation_result: SimulationResult
    metrics: ExperimentMetrics
    model_versions: dict[str, str]   # zone_id → model version
    parameter_fingerprint: str       # hash of all parameter values


# ---------------------------------------------------------------------------
# Comparison result
# ---------------------------------------------------------------------------


@dataclass
class ComparisonResult:
    baseline: ExperimentResult
    candidate: ExperimentResult
    water_delta_l: float
    water_delta_pct: float
    energy_delta_kwh: float
    energy_delta_pct: float
    yield_delta_kg: float
    yield_delta_pct: float
    stress_delta: float
    summary: str


# ---------------------------------------------------------------------------
# ExperimentRunner
# ---------------------------------------------------------------------------


class ExperimentRunner:
    """
    Runs experiments against the canonical simulation engine.

    The runner is crop-independent; it calls SimulationEngine which
    resolves crops through CropRegistry.
    """

    def __init__(self, registry: CropRegistry | None = None) -> None:
        self._registry = registry or CropRegistry.default()
        self._engine = SimulationEngine(self._registry)

    def run(self, experiment: ExperimentConfig) -> ExperimentResult:
        """Execute a single experiment and return a reproducible result."""
        sim_result = self._engine.run(experiment.simulation_config)

        # Build per-zone metrics
        zone_metrics: list[ZoneMetrics] = []
        config_zones = {z.zone_id: z for z in experiment.simulation_config.zones}
        for zr in sim_result.zone_results:
            area = config_zones[zr.zone_id].area_sqm
            water_eff = (
                zr.final_harvestable_biomass_kg / zr.total_water_consumed_l
                if zr.total_water_consumed_l > 0 else 0.0
            )
            zone_metrics.append(ZoneMetrics(
                zone_id=zr.zone_id,
                crop_id=zr.crop_id,
                total_harvestable_kg=zr.final_harvestable_biomass_kg,
                area_sqm=area,
                yield_kg_per_sqm=zr.final_harvestable_biomass_kg / max(area, 1.0),
                total_water_l=zr.total_water_consumed_l,
                water_efficiency_kg_per_l=water_eff,
                average_stress_index=zr.final_stress_index,
                final_stage=zr.final_stage,
                harvest_ready=zr.harvest_ready,
            ))

        water_eff_total = (
            sim_result.final_yield_kg / sim_result.total_water_liters
            if sim_result.total_water_liters > 0 else 0.0
        )
        metrics = ExperimentMetrics(
            total_harvestable_kg=sim_result.final_yield_kg,
            total_water_l=sim_result.total_water_liters,
            total_energy_kwh=sim_result.total_energy_kwh,
            average_stress=sim_result.average_stress,
            constraint_violations=len(sim_result.constraint_violations),
            zone_metrics=zone_metrics,
            water_efficiency_kg_per_l=water_eff_total,
        )

        # Model versions
        model_versions = {
            zr.zone_id: zr.crop_model_version
            for zr in sim_result.zone_results
        }

        # Parameter fingerprint
        cfg_json = experiment.simulation_config.model_dump_json()
        param_fp = hashlib.sha256(cfg_json.encode()).hexdigest()[:12]

        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            description=experiment.description,
            git_sha=_get_git_sha(),
            timestamp=datetime.datetime.now(tz=timezone.utc).isoformat(),
            simulation_result=sim_result,
            metrics=metrics,
            model_versions=model_versions,
            parameter_fingerprint=param_fp,
        )

    def compare(
        self,
        baseline: ExperimentConfig,
        candidate: ExperimentConfig,
    ) -> ComparisonResult:
        """Run two experiments and produce a structured comparison."""
        base_result = self.run(baseline)
        cand_result = self.run(candidate)

        bm = base_result.metrics
        cm = cand_result.metrics

        def pct(a: float, b: float) -> float:
            return ((b - a) / a * 100.0) if a != 0 else 0.0

        water_delta = cm.total_water_l - bm.total_water_l
        energy_delta = cm.total_energy_kwh - bm.total_energy_kwh
        yield_delta = cm.total_harvestable_kg - bm.total_harvestable_kg
        stress_delta = cm.average_stress - bm.average_stress

        lines = [
            f"Experiment Comparison: {baseline.experiment_id} vs {candidate.experiment_id}",
            f"  Water: {water_delta:+.1f} L ({pct(bm.total_water_l, cm.total_water_l):+.1f}%)",
            f"  Energy: {energy_delta:+.1f} kWh ({pct(bm.total_energy_kwh, cm.total_energy_kwh):+.1f}%)",
            f"  Yield: {yield_delta:+.3f} kg ({pct(bm.total_harvestable_kg, cm.total_harvestable_kg):+.1f}%)",
            f"  Avg Stress: {stress_delta:+.3f}",
        ]

        return ComparisonResult(
            baseline=base_result,
            candidate=cand_result,
            water_delta_l=water_delta,
            water_delta_pct=pct(bm.total_water_l, cm.total_water_l),
            energy_delta_kwh=energy_delta,
            energy_delta_pct=pct(bm.total_energy_kwh, cm.total_energy_kwh),
            yield_delta_kg=yield_delta,
            yield_delta_pct=pct(bm.total_harvestable_kg, cm.total_harvestable_kg),
            stress_delta=stress_delta,
            summary="\n".join(lines),
        )
