"""
domains/polyhouse/crops/registry.py

CropRegistry — the single source of truth for registered crop profiles.

The simulation engine, optimizer, safety verifier, and experiment runner
resolve crops exclusively through this registry. They never import
individual crop implementations directly.

Usage
-----
from domains.polyhouse.crops.registry import CropRegistry

registry = CropRegistry.default()        # returns singleton with built-in crops
profile  = registry.get("lettuce")      # CropProfile
"""

from __future__ import annotations

import builtins
import threading

from .base import CropProfile


class CropNotFoundError(KeyError):
    def __init__(self, crop_id: str) -> None:
        super().__init__(f"Crop '{crop_id}' is not registered in CropRegistry.")


class CropValidationError(ValueError):
    pass


class CropRegistry:
    """
    Thread-safe registry of CropProfile objects.

    Lifecycle
    ---------
    Obtain the singleton instance populated with all built-in crops via
    ``CropRegistry.default()``.

    For tests or isolated experiments, create a fresh instance with
    ``CropRegistry()`` and register only the crops you need.
    """

    _singleton: CropRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._profiles: dict[str, CropProfile] = {}

    # ------------------------------------------------------------------
    # Singleton helpers
    # ------------------------------------------------------------------

    @classmethod
    def default(cls) -> CropRegistry:
        """
        Return the singleton instance populated with all built-in crops.
        Lazy-initialised on first call.
        """
        if cls._singleton is None:
            with cls._lock:
                if cls._singleton is None:
                    instance = cls()
                    instance._register_builtins()
                    cls._singleton = instance
        return cls._singleton

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton — useful in tests to avoid state leakage."""
        with cls._lock:
            cls._singleton = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, profile: CropProfile, *, overwrite: bool = False) -> None:
        """
        Register a CropProfile.

        Parameters
        ----------
        profile:   The complete crop profile to register.
        overwrite: If False (default) raises ValueError on duplicate crop_id.
        """
        issues = profile.validate()
        if issues:
            raise CropValidationError(
                f"CropProfile '{profile.crop_id}' failed validation:\n"
                + "\n".join(f"  - {i}" for i in issues)
            )
        if profile.crop_id in self._profiles and not overwrite:
            raise ValueError(
                f"Crop '{profile.crop_id}' is already registered. "
                "Pass overwrite=True to replace it."
            )
        self._profiles[profile.crop_id] = profile

    def get(self, crop_id: str) -> CropProfile:
        """Return the CropProfile for crop_id, or raise CropNotFoundError."""
        if crop_id not in self._profiles:
            raise CropNotFoundError(crop_id)
        return self._profiles[crop_id]

    def exists(self, crop_id: str) -> bool:
        """Return True if crop_id is registered."""
        return crop_id in self._profiles

    def list(self) -> builtins.list[str]:
        """Return sorted list of registered crop_ids."""
        return sorted(self._profiles.keys())

    def all_profiles(self) -> builtins.list[CropProfile]:
        """Return all registered CropProfile objects."""
        return [self._profiles[k] for k in self.list()]

    # ------------------------------------------------------------------
    # Built-in crop registration
    # ------------------------------------------------------------------

    def _register_builtins(self) -> None:
        """
        Register all built-in crop profiles.

        This is the only place in the registry that references specific
        crop modules. Adding a new built-in crop means adding one import
        and one register() call here.
        """
        # Import here to avoid circular dependency at module load time
        from domains.polyhouse.crops.cucumber import build_profile as cucumber_profile
        from domains.polyhouse.crops.dwarf_tomato import build_profile as dt_profile
        from domains.polyhouse.crops.lettuce import build_profile as lettuce_profile

        for builder in [dt_profile, lettuce_profile, cucumber_profile]:
            profile = builder()
            self.register(profile)
