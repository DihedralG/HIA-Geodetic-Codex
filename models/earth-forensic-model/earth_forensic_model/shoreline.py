"""Uncertainty-aware first-order paleoshoreline calculations.

The kernel deliberately separates global mean sea level from the local
relative-sea-level anomaly produced by GIA, gravitational fingerprints,
hydro-isostasy, tectonics, and datum conversion.

Sign convention
---------------
All elevations are metres relative to present mean sea level.

* present_elevation_m: positive above, negative below present sea level.
* global_mean_sea_level_m: past global mean sea level relative to present.
* local_rsl_anomaly_m: local RSL minus global mean sea level. Positive means
  water stood higher locally relative to the present bed than the eustatic
  value alone would imply.

The first-order exposure margin is:

    margin = present_elevation - (global_mean_sea_level + local_rsl_anomaly)

A positive margin indicates exposure. Ice cover is a separate state and is
not inferred by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist


@dataclass(frozen=True)
class SeaLevelScenario:
    scenario_id: str
    age_ka_bp: float
    global_mean_sea_level_m: float
    standard_deviation_m: float

    def __post_init__(self) -> None:
        if self.age_ka_bp < 0:
            raise ValueError("age_ka_bp must be non-negative")
        if self.standard_deviation_m < 0:
            raise ValueError("standard_deviation_m must be non-negative")


@dataclass(frozen=True)
class Site:
    site_id: str
    present_elevation_m: float
    elevation_standard_deviation_m: float = 0.0
    local_rsl_anomaly_m: float = 0.0
    local_rsl_standard_deviation_m: float = 0.0

    def __post_init__(self) -> None:
        if self.elevation_standard_deviation_m < 0:
            raise ValueError("elevation_standard_deviation_m must be non-negative")
        if self.local_rsl_standard_deviation_m < 0:
            raise ValueError("local_rsl_standard_deviation_m must be non-negative")


@dataclass(frozen=True)
class ExposureResult:
    scenario_id: str
    site_id: str
    age_ka_bp: float
    mean_local_rsl_m: float
    mean_exposure_margin_m: float
    combined_standard_deviation_m: float
    probability_exposed: float
    margin_ci95_lower_m: float
    margin_ci95_upper_m: float
    classification: str


def classify_probability(probability: float) -> str:
    """Return a deliberately conservative exposure classification."""
    if probability >= 0.95:
        return "likely_exposed"
    if probability <= 0.05:
        return "likely_submerged"
    return "indeterminate"


def calculate_exposure(
    scenario: SeaLevelScenario,
    site: Site,
) -> ExposureResult:
    """Calculate exposure probability under independent Gaussian errors.

    This is a transparent baseline, not a replacement for a spatial GIA model.
    Independence and Gaussian error are explicit v0.1 assumptions.
    """
    mean_local_rsl = (
        scenario.global_mean_sea_level_m + site.local_rsl_anomaly_m
    )
    mean_margin = site.present_elevation_m - mean_local_rsl
    combined_sd = sqrt(
        scenario.standard_deviation_m**2
        + site.elevation_standard_deviation_m**2
        + site.local_rsl_standard_deviation_m**2
    )

    if combined_sd == 0:
        probability = 1.0 if mean_margin > 0 else 0.0
        lower = upper = mean_margin
    else:
        probability = NormalDist(mu=mean_margin, sigma=combined_sd).cdf(0)
        # P(margin > 0), correcting the lower-tail CDF above.
        probability = 1.0 - probability
        z975 = NormalDist().inv_cdf(0.975)
        lower = mean_margin - z975 * combined_sd
        upper = mean_margin + z975 * combined_sd

    return ExposureResult(
        scenario_id=scenario.scenario_id,
        site_id=site.site_id,
        age_ka_bp=scenario.age_ka_bp,
        mean_local_rsl_m=mean_local_rsl,
        mean_exposure_margin_m=mean_margin,
        combined_standard_deviation_m=combined_sd,
        probability_exposed=probability,
        margin_ci95_lower_m=lower,
        margin_ci95_upper_m=upper,
        classification=classify_probability(probability),
    )
