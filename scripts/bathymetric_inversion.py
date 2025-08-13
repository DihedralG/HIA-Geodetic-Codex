#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bathymetric_inversion.py
ChiR Labs — Geodetic Codex V4.8 (Bathymetric Inversion & Lost Altitudes)

Purpose
-------
Treat the ocean floor as negative relief of vanished lands. This scaffold provides
reusable functions and a small CLI to:
  • invert present-day bathymetry into paleotopography for a given lowstand ΔSL
  • apply isostatic/flexural corrections U(x,y)
  • detect shelf terrace "ladders" and compute a terrace coherence proxy
  • extract inverted drainage on the reconstructed z*
  • correlate inverted drainage with observed echo-features (e.g., fans, amphitheaters)
  • compose an inversion confidence score IC as in the V4.8 spec

Dependencies (py ≥3.9)
----------------------
numpy, scipy, rasterio, scikit-image (skimage)
Optional: rich (nicer CLI progress), numba (speed-ups)

Install (example):
  pip install numpy scipy rasterio scikit-image rich

Usage (examples)
----------------
# Minimal: invert one ΔSL and write z* to GeoTIFF
python scripts/bathymetric_inversion.py \
  --bathy data/bathy.tif \
  --uplift data/uplift.tif \
  --dsl 120 \
  --out_zstar out/zstar_120m.tif

# Full: also detect terraces, extract inverted drainage and echo-match
python scripts/bathymetric_inversion.py \
  --bathy data/bathy.tif \
  --uplift data/uplift.tif \
  --dsl 120 \
  --echo data/echo_features.tif \
  --out_zstar out/zstar_120m.tif \
  --out_drain out/drain_120m.tif \
  --out_terr out/terraces_120m.tif \
  --out_ic out/ic_120m.tif
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
from scipy.ndimage import gaussian_filter, sobel
from skimage.morphology import remove_small_holes, remove_small_objects
from skimage.graph import route_through_array
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.feature import canny

try:
    from rich import print  # type: ignore
    from rich.progress import Progress  # type: ignore
    RICH = True
except Exception:
    RICH = False

try:
    import rasterio
    from rasterio import features
    from rasterio.transform import Affine
except Exception as e:
    raise SystemExit("rasterio is required for reading/writing GeoTIFFs. pip install rasterio") from e


# ----------------------------
# I/O utilities
# ----------------------------

def _read_tif(path: str) -> Tuple[np.ndarray, Affine, Dict]:
    with rasterio.open(path) as ds:
        arr = ds.read(1, masked=True).filled(np.nan)
        transform = ds.transform
        meta = ds.meta.copy()
    return arr, transform, meta


def _write_tif(path: str, arr: np.ndarray, transform: Affine, meta_like: Dict, nodata: float = np.nan) -> None:
    meta = meta_like.copy()
    meta.update({"count": 1, "dtype": "float32", "transform": transform, "nodata": nodata, "compress": "deflate"})
    with rasterio.open(path, "w", **meta) as ds:
        ds.write(arr.astype("float32"), 1)


# ----------------------------
# Core V4.8 hooks (public API)
# ----------------------------

def invert_bathy(
    zb: np.ndarray,
    U: Optional[np.ndarray],
    dSL: float,
    datum_offset: float = 0.0,
) -> np.ndarray:
    """
    Compute paleotopography z* from present bathymetry zb (<0 below MSL) with optional isostatic correction U.

    z*(x,y; ΔSL) = -( zb(x,y) + U(x,y) ) - ΔSL + C

    Parameters
    ----------
    zb : array
        Present-day bathymetry/topobathy (meters; negative below MSL).
    U : array or None
        Isostatic/flexural correction (meters; positive upward). If None, assumed 0.
    dSL : float
        Lowstand sea-level offset in meters (positive number, e.g., 120 for LGM-scale).
    datum_offset : float
        Constant datum adjustment C (meters).

    Returns
    -------
    zstar : array
        Reconstructed paleotopography at the given ΔSL.
    """
    if U is None:
        U = np.zeros_like(zb)
    zstar = -1.0 * (zb + U) - float(dSL) + float(datum_offset)
    return zstar


def detect_terraces(z_or_zstar: np.ndarray, min_step: float = 2.0) -> Dict[str, np.ndarray | float]:
    """
    Detect shelf terraces (stillstand 'steps') using slope/curvature heuristics.

    Returns
    -------
    dict with:
      mask : binary array of terrace-like cells
      steps: label raster of contiguous terraces
      TSR  : terrace spacing ratio proxy (higher = cleaner ladder)
    """
    z = z_or_zstar.copy()
    # Smooth to suppress noise but retain macro-steps
    zf = gaussian_filter(z, sigma=1.2)

    # First derivatives (slope proxy)
    gx = sobel(zf, axis=1)
    gy = sobel(zf, axis=0)
    slope = np.hypot(gx, gy)

    # Identify low-slope benches near shelf (auto threshold)
    slope[np.isnan(slope)] = np.nanmedian(slope)
    t = threshold_otsu(slope[~np.isnan(slope)])
    benches = slope < max(t * 0.7, 1e-6)

    # Remove tiny specks, fill pinholes
    benches = remove_small_objects(benches, 200)
    benches = remove_small_holes(benches, 200)

    # Label benches as candidate steps
    lbl = label(benches)
    props = regionprops(lbl)

    # Estimate vertical spacing between step medians
    z_meds = []
    for p in props:
        r, c = np.transpose(np.nonzero(lbl == p.label))
        if r.size < 100:
            continue
        z_meds.append(np.nanmedian(z[r, c]))
    z_meds = np.sort(np.array(z_meds)) if len(z_meds) else np.array([])

    if z_meds.size >= 3:
        dz = np.diff(z_meds)
        dz = dz[dz >= min_step] if dz.size else dz
        if dz.size:
            tsr = float(np.median(dz) / (np.percentile(dz, 75) - np.percentile(dz, 25) + 1e-6))
        else:
            tsr = 0.0
    else:
        tsr = 0.0

    return {"mask": benches.astype(bool), "steps": lbl.astype(np.int32), "TSR": tsr}


def extract_inverted_drainage(
    zstar: np.ndarray,
    pit_fill: bool = True,
    flow_thresh: float = 0.005,
) -> np.ndarray:
    """
    Very simple MFD-style flow accumulation over z* (DEM in meters).
    This is a light placeholder; swap with your preferred flowlib if needed.

    Returns a float array of flow accumulation (0..1 normalized).
    """
    z = zstar.copy()
    # Tiny monotonic carve to discourage flats
    z = z + np.random.RandomState(42).normal(0, 1e-3, size=z.shape)

    # Finite differences to 8 neighbors
    h, w = z.shape
    acc = np.ones_like(z, dtype=float)

    # Iterate a few relaxations (placeholder for a proper flow routing)
    for _ in range(200):
        acc_old = acc.copy()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                shifted = np.roll(np.roll(z, dr, axis=0), dc, axis=1)
                flow_mask = shifted > z  # flow from higher neighbor to this cell (downhill on z*)
                acc += 0.12 * acc_old * flow_mask
        if np.nanmax(np.abs(acc - acc_old)) < 1e-3:
            break

    acc = acc - np.nanmin(acc)
    if np.nanmax(acc) > 0:
        acc = acc / np.nanmax(acc)

    # Threshold to main stems if requested
    if flow_thresh is not None:
        return (acc >= float(flow_thresh)).astype(np.float32)
    return acc.astype(np.float32)


def echo_match(Dstar: np.ndarray, E: np.ndarray) -> float:
    """
    Hydraulic Echo match HE = corr(D*, E) in [0,1].
    Inputs should be normalized/binary masks in the same grid.

    If arrays are constant, returns 0.
    """
    a = np.ravel(Dstar.astype(float))
    b = np.ravel(E.astype(float))
    msk = np.isfinite(a) & np.isfinite(b)
    if msk.sum() < 10:
        return 0.0
    a = a[msk]
    b = b[msk]
    if np.all(a == a[0]) or np.all(b == b[0]):
        return 0.0
    r = np.corrcoef(a, b)[0, 1]
    return float(max(0.0, min(1.0, (r + 1) / 2)))  # map [-1,1] → [0,1]


def paleoshore_continuity(zstar: np.ndarray, tol: float = 2.0) -> float:
    """
    PC: connected fraction of near‑zero contour. Approximate by edge density/cohesion
    within a ±tol band around z*=0.
    """
    band = (zstar > -tol) & (zstar < tol)
    if band.sum() < 100:
        return 0.0
    edges = canny(band.astype(float), sigma=1.0)
    lbl = label(edges)
    if lbl.max() == 0:
        return 0.0
    sizes = np.array([np.sum(lbl == i) for i in range(1, lbl.max() + 1)])
    pc = float(np.max(sizes) / (np.sum(sizes) + 1e-6))
    return pc


def score_IC(
    TSR: float,
    PC: float,
    HE: float,
    CF: float,
    TIO: float,
    sigma_tio: float = 10.0,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Inversion Confidence:
      IC = Σ w_i C_i, where ϕ(TIO) = exp(-TIO / sigma_tio)

    Defaults: wTC=0.25, wPC=0.20, wHE=0.25, wCF=0.15, wTIO=0.15
    """
    w = dict(wTC=0.25, wPC=0.20, wHE=0.25, wCF=0.15, wTIO=0.15)
    if weights:
        w.update(weights)
    phi = math.exp(-float(TIO) / float(sigma_tio))
    IC = (
        w["wTC"] * float(TSR)
        + w["wPC"] * float(PC)
        + w["wHE"] * float(HE)
        + w["wCF"] * float(CF)
        + w["wTIO"] * float(phi)
    )
    return float(max(0.0, min(1.0, IC)))


# ----------------------------
# CLI
# ----------------------------

@dataclass
class Args:
    bathy: str
    uplift: Optional[str]
    dsl: float
    out_zstar: Optional[str]
    echo: Optional[str]
    out_drain: Optional[str]
    out_terr: Optional[str]
    out_ic: Optional[str]
    datum: float
    min_step: float
    flow_thresh: float


def parse_args() -> Args:
    p = argparse.ArgumentParser(description="Bathymetric inversion — V4.8 hooks")
    p.add_argument("--bathy", required=True, help="Path to bathymetry/topobathy GeoTIFF (meters; negative below MSL)")
    p.add_argument("--uplift", help="Path to isostatic/flexural correction GeoTIFF (meters; positive up)")
    p.add_argument("--dsl", type=float, required=True, help="Lowstand ΔSL in meters (e.g., 120)")
    p.add_argument("--datum", type=float, default=0.0, help="Datum offset C (meters)")
    p.add_argument("--echo", help="Path to echo-feature mask GeoTIFF (binary or 0..1)")
    p.add_argument("--out_zstar", help="Output GeoTIFF for z*")
    p.add_argument("--out_drain", help="Output GeoTIFF for inverted drainage mask (0/1)")
    p.add_argument("--out_terr", help="Output GeoTIFF for terrace label raster")
    p.add_argument("--out_ic", help="Output GeoTIFF for IC (single scalar replicated to grid or per-cell if desired)")
    p.add_argument("--min_step", type=float, default=2.0, help="Minimum vertical spacing to consider a 'step' (m)")
    p.add_argument("--flow_thresh", type=float, default=0.005, help="Threshold for drainage mask from normalized acc")
    a = p.parse_args()

    return Args(
        bathy=a.bathy,
        uplift=a.uplift,
        dsl=a.dsl,
        out_zstar=a.out_zstar,
        echo=a.echo,
        out_drain=a.out_drain,
        out_terr=a.out_terr,
        out_ic=a.out_ic,
        datum=a.datum,
        min_step=a.min_step,
        flow_thresh=a.flow_thresh,
    )


def main():
    args = parse_args()

    if RICH:
        progress = Progress()
        progress.start()

    # Load rasters
    zb, T, meta = _read_tif(args.bathy)
    U = None
    if args.uplift:
        U, Tu, _ = _read_tif(args.uplift)
        if Tu != T:
            print("[yellow]Warning:[/] uplift raster transform differs from bathy — assuming same grid.")

    # 1) Invert
    if RICH: tid = progress.add_task("[cyan]Inverting bathymetry...", total=1)
    zstar = invert_bathy(zb, U, args.dsl, args.datum)
    if args.out_zstar:
        _write_tif(args.out_zstar, zstar, T, meta)
    if RICH: progress.update(tid, advance=1)

    # 2) Terraces
    if RICH: tid2 = progress.add_task("[cyan]Detecting terraces...", total=1)
    terr = detect_terraces(zstar, min_step=args.min_step)
    steps_lbl = terr["steps"]
    TSR = float(terr["TSR"])
    if args.out_terr:
        _write_tif(args.out_terr, steps_lbl.astype("float32"), T, meta)
    if RICH:
        progress.update(tid2, advance=1)
        print(f"[green]TSR (terrace spacing ratio): {TSR:.3f}")

    # 3) Inverted drainage
    if RICH: tid3 = progress.add_task("[cyan]Extracting inverted drainage...", total=1)
    Dstar = extract_inverted_drainage(zstar, flow_thresh=args.flow_thresh)
    if args.out_drain:
        _write_tif(args.out_drain, Dstar, T, meta)
    if RICH: progress.update(tid3, advance=1)

    # 4) Echo match (optional)
    HE = 0.0
    if args.echo:
        E, Te, _ = _read_tif(args.echo)
        if Te != T:
            print("[yellow]Warning:[/] echo raster transform differs from bathy — assuming same grid.")
        # Normalize E to 0..1
        Emin, Emax = np.nanmin(E), np.nanmax(E)
        if Emax - Emin > 0:
            E = (E - Emin) / (Emax - Emin)
        else:
            E = np.zeros_like(E)
        HE = echo_match(Dstar, E)
        if RICH:
            print(f"[green]Hydraulic Echo (HE): {HE:.3f}")

    # 5) Paleoshore continuity (quick proxy)
    PC = paleoshore_continuity(zstar)
    if RICH:
        print(f"[green]Paleoshore Continuity (PC): {PC:.3f}")

    # 6) Chronologic Fit / TIO placeholders (user should supply real values)
    CF = 0.5  # e.g., reef/tephra/cores alignment score in [0..1]
    TIO = 10.0  # RMSE in meters between predicted vs observed uplift (lower is better)

    # 7) Composite confidence
    IC = score_IC(TSR=TSR, PC=PC, HE=HE, CF=CF, TIO=TIO)

    if args.out_ic:
        # Write a constant IC grid for convenience (same geotransform)
        ic_grid = np.full_like(zstar, IC, dtype="float32")
        _write_tif(args.out_ic, ic_grid, T, meta)

    if RICH:
        progress.stop()
        print(f"\n[bold]Inversion Confidence (IC): {IC:.3f}[/bold]")
    else:
        print(f"Inversion Confidence (IC): {IC:.3f}")
        print(f"TSR={TSR:.3f}, PC={PC:.3f}, HE={HE:.3f}, CF={CF:.3f}, TIO={TIO:.2f}")


if __name__ == "__main__":
    main()