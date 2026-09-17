from .engine import SimulationConfig


class ScenarioEngine:
    def generate_scenarios(self, base_config: SimulationConfig) -> list[SimulationConfig]:
        scenarios = []
        
        # Baseline
        scenarios.append(base_config)
        
        # High temp
        high_temp = base_config.copy(deep=True)
        high_temp.scenario_name = "scenario-high-temperature"
        scenarios.append(high_temp)
        
        # Low water
        low_water = base_config.copy(deep=True)
        low_water.scenario_name = "scenario-low-water"
        scenarios.append(low_water)
        
        return scenarios
