#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubmergedVectors.py — Codex V4.4 scaffold
Computes:
  τ  (torsional release index)
  𝒰 (subglacial upwell propensity)
  ℋ  (hazard index)

Inputs (rasters):
  - bathymetry (or precomputed slope)
  - shear_strain (GNSS/focal-mech derived)
  - curvature (from bathy or structural surface)
  - HydroMemory outputs: M (memory), C (connectivity), sigma (void stability)
  - triggers (optional: pockmarks, EM bursts, etc.)
  - mask (optional: analysis mask, e.g., shelf)

Optional vector:
  - nodes.geojson: points to sample outputs → CSV

Outputs:
  - out/v44_vectors/tau_*.tif
  - out/v44_vectors/U_*.tif
  - out/v44_vectors/H_*.tif
  - out/v44_vectors/node_vectors.csv (if nodes provided)

Notes:
  - Dual-script notation is represented here with ASCII names and documented
    mapping in metadata. ARIA/Unicode rendering belongs in HTML layers.
  - All normalizations are min–max per raster, ignoring NaNs and nodata.
"""

import os
import json
import math
import argparse
import logging
from typing import Dict, Optional, Tuple

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.io import DatasetReader
import geopandas as gpd
from shapely.geometry import Point

# ----------------------------- Utils --------------------------------- #

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def read_raster(path: str) -> Tuple[np.ndarray, Dict]:
    with rasterio.open(path) as ds:
        arr = ds.read(1, masked=True).astype("float64")
        profile = ds.profile
    return np.array(arr), profile

def write_raster(path: str, arr: np.ndarray, template_profile: Dict, nodata: float = -9999.0, meta: Optional[Dict]=None) -> None:
    prof = template_profile.copy()
    prof.update(
        dtype="float32",
        count=1,
        compress="deflate",
        predictor=2,
        zlevel=6,
        tiled=True,
        nodata=nodata
    )
    with rasterio.open(path, "w", **prof) as dst:
        out = np.where(np.isfinite(arr), arr, nodata).astype("float32")
        dst.write(out, 1)
        if meta:
            dst.update_tags(**meta)

def minmax_norm(arr: np.ndarray) -> np.ndarray:
    m = np.nanmin(arr)
    M = np.nanmax(arr)
    if not np.isfinite(m) or not np.isfinite(M) or M - m == 0:
        return np.zeros_like(arr)
    return (arr - m) / (M - m)

def safe_inv(arr: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return 1.0 / (np.abs(arr) + eps)

def sigmoid(x: np.ndarray) -> np.ndarray:
    # Numerically stable sigmoid
    x = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x))

def compute_slope_from_bathy(bathy: np.ndarray, transform: Affine) -> np.ndarray:
    """
    Simple gradient-based slope (unitless); replace with your preferred operator.
    """
    # Pixel size
    px = transform.a
    py = -transform.e if transform.e != 0 else transform.a
    gY, gX = np.gradient(bathy, py, px)
    slope = np.hypot(gX, gY)
    return slope

def apply_mask(arr: np.ndarray, mask: Optional[np.ndarray]) -> np.ndarray:
    if mask is None:
        return arr
    masked = np.where(mask > 0.5, arr, np.nan)
    return masked

# ----------------------- Core Computations --------------------------- #

def compute_tau(
    shear_strain: np.ndarray,
    curvature: np.ndarray,
    inv_sigma: np.ndarray,  # 1/sigma
    memory_M: np.ndarray,
    conn_C: np.ndarray,
    weights: Dict[str, float]
) -> np.ndarray:
    """
    τ = g(Shear, |Curv|, 1/σ, ℳ, 𝒞)
    All components normalized to [0,1] before weighted sum.
    """
    comp = {
        "shear": minmax_norm(np.abs(shear_strain)),
        "curv":  minmax_norm(np.abs(curvature)),
        "inv_sigma": minmax_norm(inv_sigma),
        "M":     minmax_norm(memory_M),
        "C":     minmax_norm(conn_C),
    }
    wsum = 0.0
    tsum = np.zeros_like(memory_M, dtype="float64")
    for k, w in weights.items():
        if k not in comp: continue
        tsum += w * comp[k]
        wsum += w
    if wsum == 0:
        return np.zeros_like(memory_M)
    tau = np.clip(tsum / wsum, 0, 1)
    return tau

def compute_U(
    pressure: np.ndarray,
    thermal: np.ndarray,
    slope: np.ndarray,
    alpha: float,
    beta: float,
    gamma: float
) -> np.ndarray:
    """
    𝒰 = sigmoid(alpha*P + beta*T - gamma*Slope)
    Inputs should be normalized or comparable scale; we normalize inside.
    """
    Pn = minmax_norm(pressure)
    Tn = minmax_norm(thermal)
    Sn = minmax_norm(slope)
    x = alpha * Pn + beta * Tn - gamma * Sn
    return sigmoid(x)

def compute_H(
    tau: np.ndarray,
    U: np.ndarray,
    slope: np.ndarray,
    triggers: Optional[np.ndarray],
    weights: Dict[str, float]
) -> np.ndarray:
    """
    ℋ = a·τ + b·𝒰 + c·Slope + d·Triggers
    With all terms normalized to [0,1].
    """
    comp = {
        "tau":  minmax_norm(tau),
        "U":    minmax_norm(U),
        "slope":minmax_norm(slope),
    }
    if triggers is not None:
        comp["triggers"] = minmax_norm(triggers)

    wsum, Hsum = 0.0, np.zeros_like(tau)
    for k, w in weights.items():
        if k not in comp: continue
        Hsum += w * comp[k]
        wsum += w
    if wsum == 0:
        return np.zeros_like(tau)
    H = np.clip(Hsum / wsum, 0, 1)
    return H

# -------------------------- Orchestration ---------------------------- #

def run(
    out_dir: str,
    bathy_path: Optional[str],
    slope_path: Optional[str],
    shear_path: str,
    curv_path: str,
    M_path: str,
    C_path: str,
    sigma_path: str,
    pressure_path: Optional[str],
    thermal_path: Optional[str],
    triggers_path: Optional[str],
    mask_path: Optional[str],
    nodes_path: Optional[str],
    tau_weights: Dict[str, float],
    H_weights: Dict[str, float],
    U_params: Dict[str, float],
    tag: str = "default"
):
    logging.info("Reading inputs…")
    # HydroMemory inputs
    M, prof = read_raster(M_path)
    C, _ = read_raster(C_path)
    sigma, _ = read_raster(sigma_path)
    inv_sigma = safe_inv(sigma)

    # Stress/curvature
    shear, _ = read_raster(shear_path)
    curv, _  = read_raster(curv_path)

    # Slope from file or derive from bathymetry
    if slope_path:
        slope, _ = read_raster(slope_path)
    elif bathy_path:
        with rasterio.open(bathy_path) as ds:
            bathy = ds.read(1, masked=True).astype("float64")
            slope = compute_slope_from_bathy(np.array(bathy), ds.transform)
    else:
        raise ValueError("Provide either --slope or --bathy to compute slope.")

    # Optional layers
    pressure = thermal = triggers = mask = None
    if pressure_path:
        pressure, _ = read_raster(pressure_path)
    if thermal_path:
        thermal, _ = read_raster(thermal_path)
    if triggers_path:
        triggers, _ = read_raster(triggers_path)
    if mask_path:
        mask, _ = read_raster(mask_path)

    # Apply mask early
    for name, arr in [("M", M), ("C", C), ("sigma", sigma), ("inv_sigma", inv_sigma),
                      ("shear", shear), ("curv", curv), ("slope", slope),
                      ("pressure", pressure), ("thermal", thermal),
                      ("triggers", triggers)]:
        if arr is None: 
            continue
        if mask is not None:
            locals()[name][:] = apply_mask(arr, mask)

    logging.info("Computing τ (torsional release)…")
    tau = compute_tau(
        shear_strain=shear,
        curvature=curv,
        inv_sigma=inv_sigma,
        memory_M=M,
        conn_C=C,
        weights=tau_weights
    )

    logging.info("Computing 𝒰 (upwell propensity)…")
    if pressure is None or thermal is None:
        logging.warning("pressure/thermal not provided — setting U from slope only (low-signal).")
        alpha = U_params.get("alpha", 1.0)
        beta  = U_params.get("beta", 0.0)
        gamma = U_params.get("gamma", 1.0)
        pressure = np.zeros_like(slope)
        thermal  = np.zeros_like(slope)
    else:
        alpha = U_params.get("alpha", 1.0)
        beta  = U_params.get("beta", 1.0)
        gamma = U_params.get("gamma", 1.0)

    U = compute_U(
        pressure=pressure,
        thermal=thermal,
        slope=slope,
        alpha=alpha, beta=beta, gamma=gamma
    )

    logging.info("Computing ℋ (hazard)…")
    H = compute_H(
        tau=tau,
        U=U,
        slope=slope,
        triggers=triggers,
        weights=H_weights
    )

    ensure_dir(out_dir)

    meta_common = {
        "codex_v": "V4.4",
        "notation": json.dumps({
            "tau": "τ (torsional release index)",
            "U": "𝒰 (subglacial upwell propensity)",
            "H": "ℋ (hazard index)",
            "mapping": "ASCII variable names map to Codex dual-script symbols in HTML."
        }),
        "tag": tag
    }

    tau_path = os.path.join(out_dir, f"tau_{tag}.tif")
    U_path   = os.path.join(out_dir, f"U_{tag}.tif")
    H_path   = os.path.join(out_dir, f"H_{tag}.tif")

    logging.info(f"Writing: {tau_path}")
    write_raster(tau_path, tau, prof, meta=meta_common | {"layer":"tau"})
    logging.info(f"Writing: {U_path}")
    write_raster(U_path, U, prof, meta=meta_common | {"layer":"U"})
    logging.info(f"Writing: {H_path}")
    write_raster(H_path, H, prof, meta=meta_common | {"layer":"H"})

    # Optional: sample node points
    if nodes_path and os.path.exists(nodes_path):
        logging.info("Sampling nodes → CSV…")
        gdf = gpd.read_file(nodes_path)
        # open for sampling
        with rasterio.open(tau_path) as d_tau, \
             rasterio.open(U_path) as d_U, \
             rasterio.open(H_path) as d_H:
            vals_tau, vals_U, vals_H = [], [], []
            for geom in gdf.geometry:
                if geom.is_empty or not isinstance(geom, Point):
                    vals_tau.append(np.nan); vals_U.append(np.nan); vals_H.append(np.nan)
                    continue
                r, c = d_tau.index(geom.x, geom.y)
                try:
                    vals_tau.append(d_tau.read(1)[r, c])
                    vals_U.append(d_U.read(1)[r, c])
                    vals_H.append(d_H.read(1)[r, c])
                except IndexError:
                    vals_tau.append(np.nan); vals_U.append(np.nan); vals_H.append(np.nan)
        gdf["tau"] = vals_tau
        gdf["U"]   = vals_U
        gdf["H"]   = vals_H
        out_csv = os.path.join(out_dir, "node_vectors.csv")
        gdf.drop(columns="geometry").to_csv(out_csv, index=False)
        logging.info(f"Wrote: {out_csv}")

    logging.info("Done.")

# --------------------------- CLI ------------------------------------- #

def parse_args():
    p = argparse.ArgumentParser(
        description="Codex V4.4 — Submerged Vectors & Torsional Release (τ, 𝒰, ℋ)"
    )
    p.add_argument("--out", default="out/v44_vectors", help="Output directory")
    p.add_argument("--bathy", help="Bathymetry raster (for slope derivation)")
    p.add_argument("--slope", help="Slope raster (if provided, bathy not required)")

    p.add_argument("--shear", required=True, help="Shear strain raster")
    p.add_argument("--curv", required=True, help="Curvature raster")

    p.add_argument("--M", required=True, help="HydroMemory: ℳ raster (aquifer memory)")
    p.add_argument("--C", required=True, help="HydroMemory: 𝒞 raster (karst connectivity)")
    p.add_argument("--sigma", required=True, help="HydroMemory: σ raster (void stability)")

    p.add_argument("--pressure", help="Basal or pore pressure raster (optional)")
    p.add_argument("--thermal", help="Thermal anomaly raster (optional)")
    p.add_argument("--triggers", help="Triggers raster (optional: pockmarks, EM)")

    p.add_argument("--mask", help="Analysis mask raster (optional)")
    p.add_argument("--nodes", help="Node points GeoJSON (optional)")

    p.add_argument("--tau-weights", default='{"shear":0.3,"curv":0.2,"inv_sigma":0.2,"M":0.15,"C":0.15}',
                   help='JSON dict weights for τ components')
    p.add_argument("--H-weights", default='{"tau":0.45,"U":0.35,"slope":0.15,"triggers":0.05}',
                   help='JSON dict weights for ℋ components')
    p.add_argument("--U-params", default='{"alpha":1.0,"beta":1.0,"gamma":1.0}',
                   help='JSON dict params for 𝒰 (pressure/thermal/slope coefficients)')
    p.add_argument("--tag", default="default", help="Tag for output filenames")
    p.add_argument("--log", default="INFO", help="Logging level (DEBUG, INFO, WARNING)")

    return p.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO),
                        format="%(levelname)s | %(message)s")
    try:
        tau_w = json.loads(args.tau_weights)
        H_w   = json.loads(args.H_weights)
        U_p   = json.loads(args.U_params)
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON parsing error: {e}")

    run(
        out_dir=args.out,
        bathy_path=args.bathy,
        slope_path=args.slope,
        shear_path=args.shear,
        curv_path=args.curv,
        M_path=args.M,
        C_path=args.C,
        sigma_path=args.sigma,
        pressure_path=args.pressure,
        thermal_path=args.thermal,
        triggers_path=args.triggers,
        mask_path=args.mask,
        nodes_path=args.nodes,
        tau_weights=tau_w,
        H_weights=H_w,
        U_params=U_p,
        tag=args.tag
    )

if __name__ == "__main__":
    main()