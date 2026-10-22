# Earth Forensic Model

**Status:** Experimental scientific scaffold, version 0.1  
**Parent project:** Harmonic Intelligence & the Geodetic Codex  
**Author:** Glenn Andersen, The Dihedral Group | ChiR Labs

## Purpose

The Earth Forensic Model is a reproducible framework for testing how orbital forcing,
ice-sheet mass, relative sea level, glacial isostatic adjustment, ocean circulation,
salinity, sediment transport, geochemical tracers, and Earth rotation interact across
annual, centennial, and Marine Isotope Stage time scales.

The framework treats natural archives as incomplete witnesses. It does not assign an
event or causal interpretation to an observation until the transport, preservation,
chronology, and uncertainty models have been evaluated.

## Evidence classes

Every claim and observation must be labeled as one of:

- **Observed** — a reported measurement with provenance and uncertainty.
- **Derived** — calculated from observations using a documented transformation.
- **Modeled** — produced by an explicit numerical or statistical model.
- **Hypothesis** — a testable proposed explanation.
- **Unsupported** — presently lacking sufficient evidence or violating a physical constraint.

These labels describe epistemic status, not importance.

## Model state

The evolving Earth state is represented conceptually as:

```text
X(x,t) = [
  ice thickness,
  bed elevation and deformation,
  relative sea level,
  water velocity and discharge,
  ocean temperature and salinity,
  atmospheric and hydrologic isotope fields,
  dissolved and particulate tracers,
  sediment transport,
  gravity and rotation
]
```

An archive observation is represented as:

```text
y_i = H_i[X(x,t), theta_i] + epsilon_i
```

where `H_i` is the observation operator for archive `i`, `theta_i` contains
archive-specific parameters, and `epsilon_i` represents measurement and model error.

## First calibration ladder

1. **774–775 CE:** synchronize tree-ring carbon-14 with polar-ice beryllium-10 and
   chlorine-36 as a high-resolution test of chronology and archive response.
2. **Regional hydroclimate:** evaluate tree-ring oxygen-18, carbon-13, hydrogen
   isotopes, ring width, and density against instrumental and independent archives.
3. **MIS backbone:** model MIS 2, 4, 6, 8, 10, and 12 using ice volume, bathymetry,
   GIA, circulation, salinity, rotation, and sediment provenance.

The 774–775 CE event is used as a synchronization and transport calibration. It is not
treated as evidence of a flood, a global climatic catastrophe, or a change in ordinary
atmospheric oxygen concentration.

## Model modules

- `chronology/` — age models and cross-archive synchronization
- `orbital/` — precession, obliquity, eccentricity, and insolation
- `ice_mass/` — accumulation, flow, melt, calving, and mass balance
- `sea_level_gia/` — eustasy, deformation, gravity, and shoreline migration
- `hydrology/` — drainage routing, outburst floods, and hydraulic stress
- `circulation/` — heat, salinity, water-mass provenance, and AMOC state
- `rotation/` — inertia tensor, polar motion, and length-of-day response
- `tracers/` — isotopes, minerals, sediment, and biological material
- `observation/` — archive-specific forward models and likelihoods

## Reproducibility rules

- Preserve mass, energy, chronology, and angular momentum within declared tolerances.
- Store source citations, licenses, units, coordinate reference systems, and checksums.
- Keep raw or licensed datasets outside Git; commit only metadata and retrieval scripts.
- Propagate age and measurement uncertainty instead of plotting central estimates alone.
- Run ordinary-process baselines before adding impact, airburst, volcanic, or other
  impulse scenarios.
- Register falsification conditions before interpreting outputs.
- Keep archaeological and cultural interpretations in a separately dated evidence layer.

## Repository boundary

This directory contains methods, schemas, scenarios, tests, and lightweight outputs.
Sensitive locations, embargoed material, credentials, and non-redistributable datasets
must remain outside the public repository.

## Initial deliverables

- Machine-readable observation schema
- 774–775 CE calibration scenario
- Six MIS scenario definitions
- Source and license ledger
- Modern geodetic calibration plan
- Uncertainty-aware polar and global visualizations

See [model boundaries](methodology/model-boundaries.md) and the
[observation schema](schemas/observation.schema.json).
