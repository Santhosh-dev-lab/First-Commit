import time

import pytest

from domains.polyhouse.engine import SimulationConfig, SimulationEngine, ZoneSimConfig


def test_engine_run_vs_step():
    # Setup common config
    config = SimulationConfig(
        simulation_id="test_sim",
        scenario_name="normal",
        days=5,
        dt_hours=1.0,
        seed=123,
        zones=[
            ZoneSimConfig(
                zone_id="zone-1",
                crop_id="dwarf_tomato",
                area_sqm=10.0,
                plant_density_per_sqm=20.0,
                initial_substrate_moisture=65.0,
                initial_tank_volume_liters=1000.0,
            )
        ],
        initial_temperature_c=22.0,
        initial_humidity_percent=60.0,
        initial_co2_ppm=400.0,
        initial_par_umol_m2_s=300.0,
        outside_temperature_c=18.0,
        outside_humidity_percent=55.0,
    )
    
    # OLD run API (which internally loops step)
    engine = SimulationEngine()
    result_run = engine.run(config)
    
    # NEW step API repeated manually
    engine_step = SimulationEngine()
    state = engine_step.initialize_state(config)
    total_steps = int((config.days * 24.0) / config.dt_hours)
    
    for step_idx in range(total_steps):
        now = time.time() + (step_idx * config.dt_hours / 24.0) * 86400
        engine_step.step(state, timestamp=now)
        
    result_step = engine_step.finalize_state(state)
    
    # Compare
    assert result_run.total_water_liters == pytest.approx(result_step.total_water_liters)
    assert result_run.total_energy_kwh == pytest.approx(result_step.total_energy_kwh)
    assert result_run.final_yield_kg == pytest.approx(result_step.final_yield_kg)
    assert result_run.stress_index == pytest.approx(result_step.stress_index)
    
    z1_run = result_run.zone_results[0]
    z1_step = result_step.zone_results[0]
    
    assert z1_run.final_biomass_kg == pytest.approx(z1_step.final_biomass_kg)
    assert z1_run.final_stress_index == pytest.approx(z1_step.final_stress_index)
    assert z1_run.total_water_consumed_l == pytest.approx(z1_step.total_water_consumed_l)
    assert z1_run.total_water_unmet_l == pytest.approx(z1_step.total_water_unmet_l)

    # Check state comparison
    assert state.temp_c == pytest.approx(result_run.extra["final_twin"].current_state.environment["temperature"].value)
    assert state.hum_pct == pytest.approx(result_run.extra["final_twin"].current_state.environment["humidity"].value)
