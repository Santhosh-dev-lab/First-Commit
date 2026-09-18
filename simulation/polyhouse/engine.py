"""
simulation/polyhouse/engine.py — COMPATIBILITY WRAPPER

This module re-exports from the canonical implementation at
domains.polyhouse.engine so that existing code importing from this
path continues to work unchanged.

New code should import directly from domains.polyhouse.engine.
This wrapper will remain for backward compatibility.
"""

# Re-export everything from the canonical engine
from domains.polyhouse.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationResult,
    ZoneResult,
    ZoneSimConfig,
)

__all__ = [
    "SimulationConfig",
    "SimulationEngine",
    "SimulationResult",
    "ZoneResult",
    "ZoneSimConfig",
]
