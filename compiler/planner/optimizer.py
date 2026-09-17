from .baseline import BaselineController


class Policy(str):
    BASELINE_STANDARD = "BASELINE_STANDARD"
    BASELINE_WATER_SAVER = "BASELINE_WATER_SAVER"
    BASELINE_ENERGY_SAVER = "BASELINE_ENERGY_SAVER"

class ControlPlan:
    def __init__(self, policy: str, metrics: dict[str, float]):
        self.policy = policy
        self.metrics = metrics
        self.is_safe = True

class HeuristicOptimizer:
    def optimize(self, initial_state, physical_ir, simulator) -> ControlPlan:
        # Simplistic heuristic: evaluate multiple baseline controllers
        policies = {
            Policy.BASELINE_STANDARD: BaselineController(target_temp_c=24.0, trigger_moisture_percent=60.0),
            Policy.BASELINE_WATER_SAVER: BaselineController(target_temp_c=24.0, trigger_moisture_percent=40.0),
            Policy.BASELINE_ENERGY_SAVER: BaselineController(target_temp_c=26.0, trigger_moisture_percent=60.0)
        }
        
        best_policy = ""
        best_score = float('-inf')
        best_metrics = {}
        
        weights = {
            "yield": 1.0,
            "water": -0.1,
            "energy": -0.05
        }
        
        for name, controller in policies.items():
            # In a real engine, we'd run a fast forward simulation
            # Here we mock the metric evaluation
            metrics = self._mock_simulate_policy(name)
            
            score = (metrics["predicted_yield_kg"] * weights["yield"] + 
                     metrics["water_used_liters"] * weights["water"] +
                     metrics["energy_kwh"] * weights["energy"])
                     
            if score > best_score:
                best_score = score
                best_policy = name
                best_metrics = metrics
                
        return ControlPlan(policy=best_policy, metrics=best_metrics)

    def _mock_simulate_policy(self, name: str) -> dict[str, float]:
        if name == Policy.BASELINE_STANDARD:
            return {"predicted_yield_kg": 1000.0, "water_used_liters": 5000.0, "energy_kwh": 1000.0}
        elif name == Policy.BASELINE_WATER_SAVER:
            return {"predicted_yield_kg": 900.0, "water_used_liters": 3000.0, "energy_kwh": 1000.0}
        else:
            return {"predicted_yield_kg": 950.0, "water_used_liters": 5000.0, "energy_kwh": 500.0}
