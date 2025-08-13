#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4.12 — Crustal Memory & the Georesonant Archive
Computes a node survivability / memory lattice score from multi-layer inputs.

Inputs (rasters; any subset OK, normalized internally)
------
- faults.tif           : fault proximity/density (high = more faults)
- uplift.tif           : long-term vertical motion (mm/yr or index)
- hydro_resilience.tif : R from HydroMemory.py (0-1 preferred)
- minerals_qs.tif      : quartz/silicate resonance proxy (0-1 or %)
- stress_sigma.tif     : present-day stress magnitude (MPa or index)
- slope.tif            : terrain slope (radians or degrees)
- (optional) masks     : land/valid masks

Outputs
-------
- memory_score.tif     : ℒ (0..1) — higher implies better survivability/archival stability
- components.csv       : per-layer weights actually used
- quicklook.png        : (optional) composite visual

Model (transparent, monotonic)
------------------------------
ℒ = w1*(1 / (1 + Faults))  +
    w2*(1 / (1 + Stress))  +
    w3*(HydroResilience)   +
    w4*(MineralResonance)  +
    w5*(1 / (1 + |Uplift|))+
    w6*(1 / (1 + SlopeNorm))

Weights default to (0.20, 0.15, 0.20, 0.20, 0.15, 0.10) but can be set via CLI.
All layers are min-max normalized (except inversions as specified).

CLI
---
python v4/crustal_memory.py \
  --faults data/faults.tif \
  --uplift data/uplift.tif \
  --hydro data/R.tif \
  --minerals data/QS.tif \
  --stress data/stress.tif \
  --slope data/slope.tif \
  --out out/v412_memory --weights 0.2 0.15 0.2 0.2 0.15 0.1
"""

from __future__ import annotations
import os, csv, argparse
import numpy as np

try:
    import rasterio
except ImportError:
    rasterio = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def _read(path: str) -> tuple[np.ndarray, dict] | tuple[None, None]:
    if not path or rasterio is None:
        return None, None
    ds = rasterio.open(path)
    a = ds.read(1).astype("float64")
    profile = ds.profile
    ds.close()
    return a, profile


def _norm(a: np.ndarray) -> np.ndarray:
    a = a.astype("float64")
    m = np.nanmin(a); M = np.nanmax(a)
    if not np.isfinite(m) or not np.isfinite(M) or M <= m:
        return np.zeros_like(a)
    out = (a - m) / (M - m)
    out[~np.isfinite(out)] = 0.0
    return out


def compute_memory_score(
    faults=None, uplift=None, hydro=None, minerals=None, stress=None, slope=None,
    weights=(0.20, 0.15, 0.20, 0.20, 0.15, 0.10),
) -> np.ndarray:
    """
    Returns ℒ in [0,1]. Missing layers are treated as zeros (neutral after inversion/weights).
    """
    w1, w2, w3, w4, w5, w6 = weights
    shape = None
    for a in (faults, uplift, hydro, minerals, stress, slope):
        if isinstance(a, np.ndarray):
            shape = a.shape; break
    if shape is None:
        raise ValueError("No input arrays provided.")

    def nz(x):
        return x if isinstance(x, np.ndarray) else np.zeros(shape, dtype="float64")

    F = _norm(nz(faults))
    U = _norm(np.abs(nz(uplift)))
    H = _norm(nz(hydro))
    Q = _norm(nz(minerals))
    S = _norm(nz(stress))
    SL = _norm(nz(slope))

    inv = lambda x: 1.0 / (1.0 + x)  # monotonic decreasing
    L = (
        w1 * inv(F) +
        w2 * inv(S) +
        w3 * H +
        w4 * Q +
        w5 * inv(U) +
        w6 * inv(SL)
    )
    # normalize to 0..1 for presentation; preserves rank
    return _norm(L)


def quicklook(out_png: str, L: np.ndarray):
    if plt is None:
        return
    plt.figure(figsize=(6,5))
    plt.imshow(L, vmin=0, vmax=1)
    plt.title("V4.12 Crustal Memory / Survivability ℒ")
    plt.axis("off")
    plt.colorbar(label="ℒ (0..1)")
    plt.savefig(out_png, dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="V4.12 Crustal Memory score")
    ap.add_argument("--faults")
    ap.add_argument("--uplift")
    ap.add_argument("--hydro")
    ap.add_argument("--minerals")
    ap.add_argument("--stress")
    ap.add_argument("--slope")
    ap.add_argument("--out", required=True, help="output prefix, no suffix")
    ap.add_argument("--weights", nargs=6, type=float, default=[0.20,0.15,0.20,0.20,0.15,0.10])
    args = ap.parse_args()

    faults, prof = _read(args.faults)
    uplift, _ = _read(args.uplift)
    hydro, _ = _read(args.hydro)
    minerals, _ = _read(args.minerals)
    stress, _ = _read(args.stress)
    slope, _ = _read(args.slope)

    L = compute_memory_score(faults, uplift, hydro, minerals, stress, slope,
                             tuple(args.weights))

    if rasterio is not None and prof:
        prof = prof.copy(); prof.update(count=1, dtype="float32", nodata=0.0)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with rasterio.open(args.out + "_memory_score.tif", "w", **prof) as dst:
            dst.write(L.astype("float32"), 1)

    with open(args.out + "_components.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["component", "weight"])
        for name, val in zip(
            ["invFaults","invStress","HydroResilience","MineralResonance","invUplift","invSlope"],
            args.weights
        ):
            w.writerow([name, val])

    quicklook(args.out + "_quicklook.png", L)
    print("✓ V4.12 memory score written:", args.out)

if __name__ == "__main__":
    main()