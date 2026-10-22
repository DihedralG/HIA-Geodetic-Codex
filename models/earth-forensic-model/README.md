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

Every record has two independent labels.

**Evidence class** describes what the record is:

- **Observed** — a reported measurement with provenance and uncertainty.
- **Derived** — calculated from observations using a documented transformation.
- **Modeled** — produced by an explicit numerical or statistical model.
- **Hypothesis** — a testable proposed explanation.

**Support status** describes how testing currently bears on a claim or hypothesis:

- **Untested**
- **Provisionally supported**
- **Mixed**
- **Not supported**
- **Falsified**
- **Not applicable** — normally used for observations that are not themselves explanatory claims.

This two-axis system prevents a modeled hypothesis from being mistaken for either evidence
or confirmation. “Provisionally supported” means it has survived declared tests against the
available evidence; it never means settled or proven. A minority or novel model may advance
if it changes assumptions explicitly, remains physically and chronologically coherent,
generates distinguishable predictions, and survives attempted falsification.

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
- Treat consensus as weighted evidence, not an inviolable premise; document departures and test both the conventional and alternative formulations.
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

## Runnable baseline

The first executable is a deliberately transparent shoreline kernel. It computes the
probability that a point was above local relative sea level while keeping three uncertain
terms separate:

```text
local RSL = global mean sea level + local RSL anomaly
exposure margin = present elevation - local RSL
```

The local anomaly is where a GIA solution, gravitational fingerprint, hydro-isostatic
term, tectonic correction, and datum transformation enter. A zero anomaly is explicitly
an **eustatic-only control**, not a reconstructed paleoshoreline.

Run from this directory with Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v

python -m earth_forensic_model.cli \
  --scenarios scenarios/mis-lowstands.json \
  --sites examples/synthetic_sites.csv \
  --output outputs/synthetic-exposure.csv
```

The bundled sites are synthetic and test the mathematics; they are not geographic claims.
The six MIS inputs are representative samples from the Spratt-Lisiecki sea-level stack
version 2 and retain the reported uncertainty. Regional Arctic and Antarctic runs require
gridded bathymetry/topography plus an independently sourced local GIA field.
