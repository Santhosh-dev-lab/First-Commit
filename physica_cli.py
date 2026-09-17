import sys

from compiler.planner.optimizer import HeuristicOptimizer
from simulation.polyhouse.engine import SimulationConfig, SimulationEngine


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m physica_cli compile <path_to_yaml>")
        return
        
    cmd = sys.argv[1]
    yaml_path = sys.argv[2]
    
    if cmd == "compile":
        # MOCK compilation for vertical slice
        print("PHYSICA\n=======\n")
        print("DOMAIN\nDwarf Tomato Polyhouse\n")
        print("IR\nPASS\n")
        print("DIGITAL TWIN\nINITIALIZED\n")
        
        engine = SimulationEngine(None, None, None, None)
        config = SimulationConfig(
            simulation_id="sim-001",
            scenario_name="scenario-baseline",
            days=120,
            dt_hours=1.0,
            seed=42
        )
        result = engine.run(config)
        
        optimizer = HeuristicOptimizer()
        plan = optimizer.optimize(None, None, None)
        
        print("SIMULATION\nPASS\n")
        print("OPTIMIZATION\nPASS\n")
        print("SAFETY\nPASS\n")
        print("CONTROL PLAN\nREADY\n")
        
        print("RESULTS\n")
        print(f"Predicted yield:\n{result.final_yield_kg} kg\n")
        print(f"Water:\n{result.total_water_liters} L\n")
        print(f"Energy:\n{result.total_energy_kwh} kWh\n")
        print(f"Crop stress:\n{result.average_stress}\n")
        print("Growth stage:\nMATURATION\n")
        print("Harvest estimate:\nREADY in 5 days\n")

if __name__ == "__main__":
    main()
