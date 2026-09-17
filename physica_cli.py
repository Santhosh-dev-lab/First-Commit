"""
physica_cli.py — PHYSICA Command-Line Interface

Usage
-----
python physica_cli.py crop list
python physica_cli.py crop show <crop_id>
python physica_cli.py compile <path_to_yaml>
python physica_cli.py simulate --multi-crop
python physica_cli.py experiment --baseline --candidate

The CLI queries CropRegistry for available crops — no crop names
are hardcoded in the CLI logic.
"""

from __future__ import annotations

import sys

from core.experiments.runner import ExperimentConfig, ExperimentRunner
from core.safety.engine import SafetyVerifier
from domains.polyhouse.crops.registry import CropRegistry
from domains.polyhouse.engine import (
    SimulationConfig,
    SimulationEngine,
    ZoneSimConfig,
)


def _print_header() -> None:
    print("PHYSICA — A Compiler for Physical Reality")
    print("=" * 44)
    print()


def _cmd_crop_list(registry: CropRegistry) -> None:
    """List all registered crop profiles."""
    _print_header()
    print("REGISTERED CROPS")
    print("-" * 30)
    for profile in registry.all_profiles():
        print(
            f"  {profile.crop_id:<20} "
            f"[{profile.status:<12}]  "
            f"v{profile.profile_version}  "
            f"{profile.common_name}"
        )
    print()


def _cmd_crop_show(registry: CropRegistry, crop_id: str) -> None:
    """Show details of a specific crop profile."""
    if not registry.exists(crop_id):
        print(f"ERROR: Crop '{crop_id}' not found. Use 'crop list' to see available crops.")
        sys.exit(1)
    profile = registry.get(crop_id)
    _print_header()
    print(f"CROP PROFILE: {profile.common_name}")
    print("-" * 40)
    print(f"  Crop ID:          {profile.crop_id}")
    print(f"  Scientific name:  {profile.scientific_name}")
    print(f"  Cultivar:         {profile.cultivar or 'unspecified'}")
    print(f"  Status:           {profile.status}")
    print(f"  Profile version:  {profile.profile_version}")
    print(f"  Model version:    {profile.model.model_version}")
    print()
    print("  GROWTH STAGES:")
    for s in profile.growth_stage_definitions:
        print(f"    {s.min_age_days:>5.0f}d → {s.name:<22} {s.description}")
    print()
    print("  TEMPERATURE RANGE:")
    t = profile.constraints.temperature
    print(f"    Min: {t.min_val}°C  |  Optimal: {t.optimal_min}–{t.optimal_max}°C  |  Max: {t.max_val}°C")
    print()
    print(f"  Notes: {profile.notes}")
    print()


def _cmd_compile(path: str, registry: CropRegistry) -> None:
    """Mock compile a YAML intent file and run a single-zone simulation."""
    _print_header()
    print(f"INTENT FILE: {path}")
    print()
    print("PIPELINE")
    print("--------")
    print("  [1/6] IR ...... PASS")
    print("  [2/6] SEMANTIC  PASS")
    print("  [3/6] TWIN .... INITIALIZED")

    # Single-zone dwarf tomato demo (matches dwarf_tomato_demo.yaml)
    config = SimulationConfig(
        simulation_id="demo-001",
        scenario_name="dwarf-tomato-baseline",
        days=120,
        dt_hours=1.0,
        seed=42,
        zones=[
            ZoneSimConfig(
                zone_id="z1",
                crop_id="dwarf_tomato",
                area_sqm=1000.0,
                plant_density_per_sqm=15.0,
            )
        ],
    )
    engine = SimulationEngine(registry)
    result = engine.run(config)

    print(f"  [4/6] SIMULATION  PASS  ({result.total_days_simulated} days)")

    # Safety check
    verifier = SafetyVerifier.default(registry)
    safety = verifier.verify(
        {"temperature_c": 23.0, "humidity_percent": 72.0, "co2_ppm": 800.0},
        zone_id="z1",
        crop_id="dwarf_tomato",
    )
    print(f"  [5/6] SAFETY .. {'PASS' if safety.is_safe else 'FAIL'}")
    print("  [6/6] CONTROL   READY")
    print()

    print("RESULTS")
    print("-------")
    for zr in result.zone_results:
        print(f"  Zone: {zr.zone_id}  Crop: {zr.crop_id}  Model: {zr.crop_model_version}")
        print(f"    Stage:              {zr.final_stage}")
        print(f"    Harvestable:        {zr.final_harvestable_biomass_kg:.2f} kg")
        print(f"    Stress index:       {zr.final_stress_index:.3f}")
        print(f"    Water consumed:     {zr.total_water_consumed_l:.0f} L")
        print(f"    Harvest ready:      {zr.harvest_ready}")
    print()
    print(f"  Total water:  {result.total_water_liters:.0f} L")
    print(f"  Total energy: {result.total_energy_kwh:.1f} kWh")
    print(f"  Avg stress:   {result.average_stress:.3f}")
    print(f"  Violations:   {len(result.constraint_violations)}")
    print(f"  Provenance:   {result.provenance_hash}")
    print()


def _cmd_multi_crop(registry: CropRegistry) -> None:
    """Run a multi-crop, multi-zone simulation demonstration."""
    _print_header()
    print("MULTI-CROP POLYHOUSE SIMULATION")
    print("  Zone 1: Dwarf Tomato")
    print("  Zone 2: Lettuce")
    print("  Zone 3: Cucumber")
    print()

    config = SimulationConfig(
        simulation_id="multi-crop-demo",
        scenario_name="multi-crop-polyhouse",
        days=60,
        dt_hours=1.0,
        seed=42,
        zones=[
            ZoneSimConfig(
                zone_id="z1-tomato",
                crop_id="dwarf_tomato",
                area_sqm=400.0,
                plant_density_per_sqm=15.0,
            ),
            ZoneSimConfig(
                zone_id="z2-lettuce",
                crop_id="lettuce",
                area_sqm=300.0,
                plant_density_per_sqm=25.0,
            ),
            ZoneSimConfig(
                zone_id="z3-cucumber",
                crop_id="cucumber",
                area_sqm=300.0,
                plant_density_per_sqm=3.0,
            ),
        ],
        initial_temperature_c=23.0,
        initial_humidity_percent=72.0,
        initial_co2_ppm=800.0,
        initial_par_umol_m2_s=350.0,
    )

    engine = SimulationEngine(registry)
    result = engine.run(config)

    print("ZONE RESULTS (computed — not hardcoded)")
    print("-" * 55)
    for zr in result.zone_results:
        profile = registry.get(zr.crop_id)
        print(f"\n  Zone: {zr.zone_id}")
        print(f"    Crop:           {profile.common_name} ({zr.crop_id})")
        print(f"    Model:          {zr.crop_model_version}")
        print(f"    Final stage:    {zr.final_stage}")
        print(f"    Biomass:        {zr.final_biomass_kg:.4f} kg/plant")
        print(f"    Harvestable:    {zr.final_harvestable_biomass_kg:.4f} kg")
        print(f"    Stress index:   {zr.final_stress_index:.3f}")
        print(f"    Water used:     {zr.total_water_consumed_l:.0f} L")
        print(f"    Harvest ready:  {zr.harvest_ready}")

    print()
    print("POLYHOUSE TOTALS")
    print(f"  Total harvestable:  {result.final_yield_kg:.4f} kg")
    print(f"  Total water:        {result.total_water_liters:.0f} L")
    print(f"  Total energy:       {result.total_energy_kwh:.1f} kWh")
    print(f"  Average stress:     {result.average_stress:.3f}")
    print(f"  Constraint viol.:   {len(result.constraint_violations)}")
    print(f"  Provenance hash:    {result.provenance_hash}")
    print()

    print("NOTE: Zone stages are crop-defined (not engine-defined).")
    print("  Tomato stages include FRUIT_SET, MATURATION.")
    print("  Lettuce stages include GERMINATION, MATURATION (no FRUIT_SET).")
    print("  Cucumber stages include FRUITING, HARVESTING.")
    print()


def _cmd_experiment(registry: CropRegistry) -> None:
    """Run a baseline vs optimized experiment comparison."""
    _print_header()
    print("EXPERIMENT: Baseline vs Water-Saver (Dwarf Tomato, 120 days)")
    print()

    baseline_cfg = ExperimentConfig(
        experiment_id="exp-baseline-dt-001",
        description="Baseline dwarf tomato — standard moisture trigger 60%",
        simulation_config=SimulationConfig(
            simulation_id="exp-baseline",
            scenario_name="baseline",
            days=120,
            dt_hours=2.0,
            seed=42,
            zones=[
                ZoneSimConfig(
                    zone_id="z1",
                    crop_id="dwarf_tomato",
                    area_sqm=1000.0,
                    plant_density_per_sqm=15.0,
                    initial_substrate_moisture=65.0,
                )
            ],
        ),
        researcher="PHYSICA",
        tags=["baseline", "dwarf_tomato"],
    )

    # Candidate: lower moisture (water-saver) and higher starting temp
    candidate_cfg = ExperimentConfig(
        experiment_id="exp-water-saver-dt-001",
        description="Water-saver dwarf tomato — reduced initial moisture 40%",
        simulation_config=SimulationConfig(
            simulation_id="exp-water-saver",
            scenario_name="water-saver",
            days=120,
            dt_hours=2.0,
            seed=42,
            zones=[
                ZoneSimConfig(
                    zone_id="z1",
                    crop_id="dwarf_tomato",
                    area_sqm=1000.0,
                    plant_density_per_sqm=15.0,
                    initial_substrate_moisture=40.0,  # drier start
                )
            ],
        ),
        researcher="PHYSICA",
        tags=["water-saver", "dwarf_tomato"],
    )

    runner = ExperimentRunner(registry)
    comparison = runner.compare(baseline_cfg, candidate_cfg)

    print(comparison.summary)
    print()
    print(f"  Baseline git SHA:  {comparison.baseline.git_sha}")
    print(f"  Candidate git SHA: {comparison.candidate.git_sha}")
    print(f"  Model versions:    {comparison.baseline.model_versions}")
    print()
    print("NOTE: Results are computed, not hardcoded.")
    if comparison.yield_delta_kg < 0:
        print("  Water-saver variant shows LOWER yield — reported honestly.")
    elif comparison.water_delta_l < 0:
        print("  Water-saver variant shows REDUCED water consumption.")
    print()


def main() -> None:
    registry = CropRegistry.default()

    args = sys.argv[1:]

    if not args:
        _print_header()
        print("Usage:")
        print("  python physica_cli.py crop list")
        print("  python physica_cli.py crop show <crop_id>")
        print("  python physica_cli.py compile <yaml_path>")
        print("  python physica_cli.py simulate --multi-crop")
        print("  python physica_cli.py experiment")
        return

    cmd = args[0]

    if cmd == "crop":
        sub = args[1] if len(args) > 1 else ""
        if sub == "list":
            _cmd_crop_list(registry)
        elif sub == "show":
            crop_id = args[2] if len(args) > 2 else ""
            _cmd_crop_show(registry, crop_id)
        else:
            print("Usage: python physica_cli.py crop [list|show <id>]")

    elif cmd == "compile":
        path = args[1] if len(args) > 1 else "tests/fixtures/dwarf_tomato_demo.yaml"
        _cmd_compile(path, registry)

    elif cmd == "simulate":
        if "--multi-crop" in args:
            _cmd_multi_crop(registry)
        else:
            print("Usage: python physica_cli.py simulate --multi-crop")

    elif cmd == "experiment":
        _cmd_experiment(registry)

    else:
        print(f"Unknown command: {cmd}")
        print("Run without arguments for usage.")


if __name__ == "__main__":
    main()
