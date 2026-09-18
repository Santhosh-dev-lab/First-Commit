import re
from typing import Any

from schemas.experiments import FarmObjective, ObjectiveWeights
from app.services.experiment_service import ExperimentService


class DecisionAgent:
    """
    Translates natural-language intent into a FarmObjective + explicit weights.
    Explains the deterministic results of the ExperimentService.
    Does NOT invent numerical metrics or execute actuators directly.
    """
    def __init__(self):
        self.experiment_service = ExperimentService()

    def _parse_intent(self, text: str) -> tuple[FarmObjective, ObjectiveWeights]:
        text = text.lower()
        
        # Simple heuristic mapping since we don't have an LLM here
        if "water" in text and "reduce" in text:
            return FarmObjective.WATER_MINIMIZATION, ObjectiveWeights(
                water_weight=1.0,
                stress_weight=0.5,
                energy_weight=0.1,
                yield_weight=0.2
            )
        elif "stress" in text and "min" in text:
            return FarmObjective.STRESS_MINIMIZATION, ObjectiveWeights(
                water_weight=0.1,
                stress_weight=1.0,
                energy_weight=0.1,
                yield_weight=0.5
            )
        elif "energy" in text and "reduce" in text:
            return FarmObjective.ENERGY_MINIMIZATION, ObjectiveWeights(
                water_weight=0.2,
                stress_weight=0.5,
                energy_weight=1.0,
                yield_weight=0.5
            )
        elif "yield" in text and "max" in text:
            return FarmObjective.YIELD_MAXIMIZATION, ObjectiveWeights(
                water_weight=0.2,
                stress_weight=0.8,
                energy_weight=0.1,
                yield_weight=1.0
            )
        else:
            return FarmObjective.BALANCED_OPERATION, ObjectiveWeights(
                water_weight=0.5,
                stress_weight=0.5,
                energy_weight=0.5,
                yield_weight=0.5
            )

    def evaluate_intent(self, farm_id: str, text: str, scenario: str, days: int = 7) -> dict[str, Any]:
        """
        Runs the autonomous experiment pipeline based on the intent.
        """
        objective, weights = self._parse_intent(text)
        
        # Experiment orchestration is entirely deterministic and relies on physics
        experiment = self.experiment_service.run_experiment(
            farm_id=farm_id,
            objective=objective,
            weights=weights,
            scenario=scenario,
            days=days
        )
        
        return self._explain_result(experiment)

    def _explain_result(self, experiment: Any) -> dict[str, Any]:
        """
        Generates an explanation without fabricating metrics.
        Returns a dict exposing only reason_summary, evidence, metrics, constraints, decision, uncertainty.
        """
        if not experiment.selected_strategy:
            return {
                "decision": "NO_SAFE_STRATEGY",
                "reason_summary": "All evaluated candidates violated safety constraints.",
                "evidence": "SimulationEngine and SafetyVerifier rejected all candidates.",
                "metrics": {},
                "constraints": ["Safety verification failed for all candidates."],
                "uncertainty": "High. Farm requires manual intervention.",
                "experiment_id": experiment.experiment_id
            }

        selected_res = next(c for c in experiment.candidates if c.candidate_id == experiment.selected_candidate_id)
        
        baseline_res = experiment.baseline
        baseline_water = baseline_res.metrics["water_used_l"] if baseline_res else 0.0
        selected_water = selected_res.metrics["water_used_l"]
        
        reason = (
            f"Selected {experiment.selected_strategy.name} because it achieved a score of {selected_res.score:.2f} "
            f"while remaining within safety constraints."
        )
        
        return {
            "decision": experiment.selected_strategy.name,
            "reason_summary": reason,
            "evidence": "Derived directly from physical simulation comparison against the baseline.",
            "metrics": {
                "selected_score": selected_res.score,
                "baseline_water": baseline_water,
                "selected_water": selected_water,
                "water_saved_l": baseline_water - selected_water
            },
            "constraints": [
                "Strategy verified by SafetyEngine.",
                "Deterministic scoring rule applied."
            ],
            "uncertainty": "Low. Relies on validated physics model.",
            "experiment_id": experiment.experiment_id
        }
