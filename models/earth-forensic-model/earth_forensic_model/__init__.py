"""Earth Forensic Model: reproducible Earth-system hypothesis testing."""

from .shoreline import (
    ExposureResult,
    SeaLevelScenario,
    Site,
    calculate_exposure,
    classify_probability,
)

__all__ = [
    "ExposureResult",
    "SeaLevelScenario",
    "Site",
    "calculate_exposure",
    "classify_probability",
]

__version__ = "0.1.0"
