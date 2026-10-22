# Model boundaries and falsification rules

Status: experimental methodology for Earth Forensic Model v0.1.

This document separates measurable Earth-system processes from exploratory hypotheses. It is a guardrail for interpretation, not a claim that every listed process is coupled at every timescale.

## Resolution domains

| Domain | Typical archives | Permitted inference |
|---|---|---|
| Annual to decadal | Tree rings, annually resolved ice cores, instruments, satellites | Event synchronization, short-lived forcing, regional response |
| Centennial to millennial | Varves, corals, speleothems, lake and marine sediments, proxy networks | Hydroclimate states, routing changes, circulation transitions |
| MIS and deep time | Marine isotope stacks, dated shorelines, GIA solutions, sediment cores, geomorphology | Ice-volume and sea-level scenarios, paleogeography, long-timescale circulation |

An archive must not be extrapolated outside its demonstrated temporal resolution or preservation window. Annual tree-ring evidence, for example, can calibrate observation methods but cannot supply continuous coverage across Marine Isotope Stages.

## Causal hierarchy

1. Orbital geometry and lunar forcing alter insolation and tides.
2. Atmosphere, ocean, cryosphere, and biosphere redistribute heat and water.
3. Ice and water redistribution changes surface loading, gravity, local relative sea level, polar motion, and length of day.
4. Mantle convection and plate tectonics set long-lived topography, gateways, volcanism, and geothermal boundary conditions.
5. Surface loading may modulate local crustal stress and volcanism; it is not treated as the primary driver of global plate motion.

Mass redistribution changes Earth's inertia tensor and can measurably affect polar motion and rotation rate. It does not, without a sufficiently large external torque, appreciably reset astronomical obliquity.

## Required distinctions

### Sea level

Every shoreline result must identify which quantity is shown:

- global mean eustatic sea level;
- local relative sea level;
- present-day bathymetric threshold;
- GIA-corrected paleoshoreline;
- grounded or floating ice margin.

A present bathymetry contour is not a dated shoreline. Exposure is not equivalent to ice-free terrain.

### Ocean circulation

AMOC and other overturning systems are not encoded as binary on/off switches. The model distinguishes strength, depth, source-water mixture, formation site, and gateway geometry. Candidate constraints include protactinium/thorium, neodymium isotopes, sortable silt, radiocarbon ventilation age, benthic carbon isotopes, oxygen-isotope/temperature pairs, and ice-rafted debris.

### Hydrothermal forcing

Hydrothermal and geothermal fluxes are local-to-regional heat, chemical, and tracer terms unless observations justify broader influence. They are not assumed to be the primary control of basin-scale overturning.

### Abrupt impulses

Impact, atmospheric burst, rapid ice-shelf collapse, jökulhlaup, landslide, and volcanic scenarios are optional impulse terms. They are evaluated only after a no-impulse baseline is fit and must have independent chronological and physical evidence.

## Observation model

For observation (i):

[
y_i = H_i[X(mathbf{x},t),	heta_i] + epsilon_i
]

where (X) is the latent Earth-system state, (H_i) maps that state into the archive actually measured, (	heta_i) contains archive-specific parameters and age uncertainty, and (epsilon_i) represents analytical and unresolved process error.

No proxy is treated as a direct reading of the full state. Each requires an observation operator and documented confounders.

## Falsification criteria

A scenario must be downgraded or rejected when one or more of the following applies:

- predicted timing falls outside independent age-model uncertainty;
- predicted flow direction conflicts with topographic or stratigraphic evidence;
- required discharge, heat, momentum, or mass exceeds bounded sources;
- tracer ratios cannot be reproduced after transport, mixing, decay, and archive filtering;
- the signal fails replication in independent archives expected to record it;
- a simpler baseline explains the observations with comparable or better predictive performance;
- posterior predictions fail held-out sites or time intervals.

Absence of evidence is informative only where archive sensitivity and preservation probability are sufficient.

## Uncertainty policy

All published outputs must propagate, at minimum:

- chronology and age-model uncertainty;
- elevation/bathymetry and vertical-datum uncertainty;
- ice thickness and GIA uncertainty;
- proxy calibration and analytical uncertainty;
- transport and mixing uncertainty;
- preservation and sampling bias;
- structural uncertainty among competing model families.

Results should be ensembles or probability fields, not single deterministic coastlines or flow paths. Model assumptions, priors, code version, input versions, and random seeds must accompany each result.
