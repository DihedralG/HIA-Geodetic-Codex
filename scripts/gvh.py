"""
ChiR G-Matrix Calculator
G = V * H**2

This module provides:
- A simple compute_g function.
- A Domain enum for key application categories.
- A basic registry describing how V and H are interpreted per domain.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Domain(Enum):
    GEOPHYSICAL = auto()
    HYDROLOGICAL = auto()
    MINERALOGICAL = auto()
    BIOLOGICAL = auto()
    ARCHITECTURAL = auto()
    CIVILIZATIONAL = auto()


@dataclass
class GHarmonicContext:
    domain: Domain
    v_description: str
    h_description: str
    notes: str = ""


def compute_g(v: float, h: float) -> float:
    """
    Compute the ChiR constant G given V and H.

    Parameters
    ----------
    v : float
        Dynamic term (velocity, volume flow, or intensity).
    h : float
        Structural / harmonic term (height, head, or amplitude).

    Returns
    -------
    float
        G = V * H^2
    """
    return v * (h ** 2)


# Registry of example domain interpretations
G_MATRIX_REGISTRY = {
    Domain.GEOPHYSICAL: GHarmonicContext(
        domain=Domain.GEOPHYSICAL,
        v_description="Flow velocity of crust, ice, or meltwater (m/s).",
        h_description="Elevation difference between nodes (m).",
        notes="G expresses planetary stability or hazard potential."
    ),
    Domain.HYDROLOGICAL: GHarmonicContext(
        domain=Domain.HYDROLOGICAL,
        v_description="Volume flow rate (m^3/s).",
        h_description="Hydraulic head (m).",
        notes="G measures harmonic flood potential and basin resilience."
    ),
    Domain.MINERALOGICAL: GHarmonicContext(
        domain=Domain.MINERALOGICAL,
        v_description="Lattice or vibrational velocity / energy density.",
        h_description="Crystal height or mode-defining dimension (m).",
        notes="G maps to resonant frequency bands and Q-factors in minerals."
    ),
    Domain.BIOLOGICAL: GHarmonicContext(
        domain=Domain.BIOLOGICAL,
        v_description="Neural wave velocity or effective coupling.",
        h_description="EEG amplitude or biofield harmonic strength.",
        notes="G is a coherence index between organism and environment."
    ),
    Domain.ARCHITECTURAL: GHarmonicContext(
        domain=Domain.ARCHITECTURAL,
        v_description="Throughput of occupants, air, or water.",
        h_description="Story height, vault span, or harmonic spacing (m).",
        notes="G relates to structural longevity and experiential resonance."
    ),
    Domain.CIVILIZATIONAL: GHarmonicContext(
        domain=Domain.CIVILIZATIONAL,
        v_description="Network throughput of energy, information, goods.",
        h_description="Hierarchical harmonic depth (infrastructure, governance layers).",
        notes="G expresses system-level resonance stability or fragility."
    ),
}


def describe_domain(domain: Domain) -> GHarmonicContext:
    """
    Return the V/H interpretation for a given domain.
    """
    return G_MATRIX_REGISTRY[domain]


if __name__ == "__main__":
    # Example usage
    example_v = 3.0   # e.g., m/s
    example_h = 10.0  # e.g., meters
    g_value = compute_g(example_v, example_h)
    print(f"G = {g_value} for V={example_v}, H={example_h}")