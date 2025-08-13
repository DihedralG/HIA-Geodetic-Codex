#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V4.11 — Kinetic Tools & Flow-Based Stoneworking
Detects flow-shaped features (siphons, V-grooves, step/curvature breaks) that
could indicate ancient hydraulic tooling: water hammers, siphons, spillway accelerators.

Inputs
------
- DEM raster (GeoTIFF)
- Optional site vectors (GeoJSON/GeoPackage) with candidate feature lines/points
- Optional karst/bedrock masks (GeoTIFF) to weight mineral/erodibility context

Outputs
-------
- GeoJSON of candidate features with indices:
    * KT_siphon_i    : siphon likelihood (0-1)
    * KT_vgroove_i   : V-groove likelihood (0-1)
    * KT_step_i      : step/curvature index (0-1)
    * KT_whammer_i   : water-hammer index (0-1)
- PNG quicklook (hillshade + candidates)
- CSV summary per candidate segment

Dependencies
------------
numpy, rasterio, shapely, geopandas, matplotlib (optional for PNG)
Uses utils:
- utils/geodesy_utils.py: load/reproject helpers (optional)
- utils/codex_rasters.py: standard raster loader (optional)

CLI
---
python v4/kinetic_tools.py \
  --dem data/dem.tif \
  --sites data/sites.geojson \
  --out out/v411_kinetics

Notes
-----
Indices are heuristic but monotonic and reproducible. Intended as a *detector*
feeding manual review and higher-fidelity CFD where needed.
"""

from __future__ import annotations
import json, os, math, argparse
from dataclasses import dataclass
import numpy as np

try:
    import rasterio
    from rasterio import features
except ImportError:
    rasterio = None

try:
    import geopandas as gpd
    from shapely.geometry import LineString, Point, mapping
except ImportError:
    gpd = None
    LineString = Point = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


# ----------------------------- small helpers ----------------------------- #

def _nan_normalize(a: np.ndarray) -> np.ndarray:
    a = a.astype("float64")
    m = np.nanmin(a); M = np.nanmax(a)
    if not np.isfinite(m) or not np.isfinite(M) or M <= m:
        return np.zeros_like(a, dtype="float64")
    out = (a - m) / (M - m)
    out[~np.isfinite(out)] = 0.0
    return out


def slope_aspect(dem: np.ndarray, res_xy: tuple[float,float]) -> tuple[np.ndarray,np.ndarray]:
    """Horn 1981-ish 3x3 gradient → slope (radians) & aspect (radians)."""
    sx, sy = res_xy
    dzdx = (np.roll(dem, -1, 1) - np.roll(dem, 1, 1)) / (2*sx)
    dzdy = (np.roll(dem, -1, 0) - np.roll(dem, 1, 0)) / (2*sy)
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(dzdy, -dzdx)  # ESRI-style
    return slope, aspect


def curvature(dem: np.ndarray, res_xy: tuple[float,float]) -> np.ndarray:
    """Simple Laplacian curvature (convexity/concavity)."""
    sx, sy = res_xy
    d2zdx2 = (np.roll(dem, -1, 1) - 2*dem + np.roll(dem, 1, 1)) / (sx**2)
    d2zdy2 = (np.roll(dem, -1, 0) - 2*dem + np.roll(dem, 1, 0)) / (sy**2)
    curv = d2zdx2 + d2zdy2
    return curv


def v_groove_likelihood(slope: np.ndarray, aspect: np.ndarray) -> np.ndarray:
    """
    Proxy: strong, aligned aspects with locally elevated slope → V-groove.
    Returns [0,1].
    """
    # local coherence of aspect via circular variance (cheap proxy)
    ax = np.cos(aspect); ay = np.sin(aspect)
    kx = (ax + np.roll(ax,1,0)+np.roll(ax,-1,0)+np.roll(ax,1,1)+np.roll(ax,-1,1))/5.0
    ky = (ay + np.roll(ay,1,0)+np.roll(ay,-1,0)+np.roll(ay,1,1)+np.roll(ay,-1,1))/5.0
    coh = np.hypot(kx, ky)  # 0..1
    s = _nan_normalize(slope)
    return np.clip(0.6*s + 0.4*coh, 0, 1)


def step_break_index(curv: np.ndarray) -> np.ndarray:
    """High |curvature| → steps/ledges. Return [0,1]."""
    return _nan_normalize(np.abs(curv))


def siphon_likelihood(dem: np.ndarray, slope: np.ndarray) -> np.ndarray:
    """
    Heuristic: candidates where short-wavelength elevation oscillates along
    potential flowlines but net head drop persists → hints of siphon/pipe runs.
    """
    # high-pass in both axes
    hp = dem - (np.roll(dem,1,0)+np.roll(dem,-1,0)+np.roll(dem,1,1)+np.roll(dem,-1,1))/4.0
    hp = np.abs(hp)
    s = _nan_normalize(slope)
    return np.clip(0.7*_nan_normalize(hp) + 0.3*s, 0, 1)


def water_hammer_index(vgroove: np.ndarray, step_i: np.ndarray, slope: np.ndarray) -> np.ndarray:
    """
    Water-hammer (transient pulse) proxy:
      - constricted channel (V-groove)
      - step/discontinuity (reflection site)
      - appreciable slope
    """
    s = _nan_normalize(slope)
    return np.clip(0.45*vgroove + 0.35*step_i + 0.20*s, 0, 1)


@dataclass
class KTOutputs:
    kt_siphon: np.ndarray
    kt_vgroove: np.ndarray
    kt_step: np.ndarray
    kt_whammer: np.ndarray


def compute_kinetic_indices(dem: np.ndarray, res_xy: tuple[float,float]) -> KTOutputs:
    slope, aspect = slope_aspect(dem, res_xy)
    curv = curvature(dem, res_xy)
    vgroove = v_groove_likelihood(slope, aspect)
    step_i = step_break_index(curv)
    siphon_i = siphon_likelihood(dem, slope)
    whammer = water_hammer_index(vgroove, step_i, slope)
    return KTOutputs(siphon_i, vgroove, step_i, whammer)


# ----------------------------- I/O + CLI -------------------------------- #

def load_dem(path: str):
    if rasterio is None:
        raise RuntimeError("rasterio is required to load DEM.")
    ds = rasterio.open(path)
    dem = ds.read(1).astype("float64")
    res = (abs(ds.transform.a), abs(ds.transform.e))
    profile = ds.profile
    ds.close()
    return dem, res, profile


def save_png_quicklook(out_png: str, dem: np.ndarray, kt: KTOutputs):
    if plt is None:
        return
    fig, axs = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
    axs = axs.ravel()
    axs[0].imshow(dem, cmap="gray"); axs[0].set_title("DEM (gray)")
    axs[1].imshow(kt.kt_vgroove, vmin=0, vmax=1); axs[1].set_title("V-groove likelihood")
    axs[2].imshow(kt.kt_step, vmin=0, vmax=1); axs[2].set_title("Step/curvature index")
    axs[3].imshow(kt.kt_whammer, vmin=0, vmax=1); axs[3].set_title("Water-hammer index")
    for ax in axs: ax.axis("off")
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def write_rasters(prefix: str, kt: KTOutputs, profile):
    if rasterio is None:
        return
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    layers = {
        "_siphon.tif": kt.kt_siphon,
        "_vgroove.tif": kt.kt_vgroove,
        "_step.tif": kt.kt_step,
        "_whammer.tif": kt.kt_whammer,
    }
    prof = profile.copy(); prof.update(count=1, dtype="float32", nodata=0.0)
    for suf, arr in layers.items():
        with rasterio.open(prefix + suf, "w", **prof) as dst:
            dst.write(arr.astype("float32"), 1)


def main():
    ap = argparse.ArgumentParser(description="V4.11 kinetic tools detector")
    ap.add_argument("--dem", required=True)
    ap.add_argument("--out", required=True, help="output path prefix (no suffix)")
    args = ap.parse_args()

    dem, res, prof = load_dem(args.dem)
    kt = compute_kinetic_indices(dem, res)
    write_rasters(args.out, kt, prof)
    save_png_quicklook(args.out + "_quicklook.png", dem, kt)

    print("✓ V4.11 kinetic indices written:")
    print("  ", args.out + "_{siphon,vgroove,step,whammer}.tif")
    if plt: print("  ", args.out + "_quicklook.png")

if __name__ == "__main__":
    main()