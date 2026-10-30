# Planetary Chronometer Lab

An interactive, hardware-neutral analytic-model and scale harness for Planetary Chronometer workloads. Version 0.2 is a scientific-hardening release: it makes model authority, coordinate conventions, rotation context, accounting assumptions, and unresolved validation gates visible in the interface and exports.

## Scientific boundary

- P001 Earth remains a separate frozen validation protocol with public residual tests still pending.
- This lab may eventually consume a validated P001 truth bundle; it cannot alter or fit that bundle.
- Classical CPU, GPU, and distributed baselines must be completed before any alternate-compute claim.
- Quantum advantage is unclaimed and would require matched resource accounting and independent verification.
- Null, negative, and contradictory results remain part of the evidence ledger.

## Version 0.2 authority boundaries

- Earth/reference output is a deterministic two-body analytic approximation, not a dated ephemeris.
- The built-in Earth check verifies only the expected analytic declination and equation-of-time envelope; it is not a Horizons residual test.
- Mars is a seasonal-frame preview with an explicit perihelion solar longitude. Its body-frame residual validation remains pending.
- Other planetary plots are illustrative coordinate studies. Retrograde rotation, pole orientation, body-fixed seasonal zero, atmospheric refraction, differential rotation, and cloud-top reference conventions are explicitly identified where relevant but not yet fully modeled.
- The deep-time control is restricted to Earth and is a simplified periodic sensitivity proxy, not a long-term orbital solution.
- Benchmark sizes and payloads are unbenchmarked projections. The payload estimate assumes 11 float64 values per sample and excludes serialization and storage overhead.
- K-01 is a proposed kernel. No HPC requirement, quantum utility, or alternate-compute advantage is claimed.

## Public build

The static application is contained in `dist/`:

- `index.html` — interface and research framing
- `styles.css` — responsive presentation layer
- `app.js` — orbital model, plots, exports, and benchmark manifest generator

The public GitHub Pages copy is published under `planetary-chronometer-lab/` in the HIA Geodetic Codex repository.
