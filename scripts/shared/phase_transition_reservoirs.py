#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase Transition Reservoirs — Codex V4.9 helper
------------------------------------------------

Compute Codex stability and resonance metrics for high‑altitude or caldera
basins that cycle water across phase states (ice, liquid, vapor).

This module is intentionally lightweight (stdlib only) so it can run anywhere.
It exposes a functional API and a small CLI for single-site or batch CSV use.

References (by layer):
- V4.9: Phase Transition Reservoirs & Terraforming Echoes
- V4.5: Quartz Resonance Quality (Q_he_ru)
- V3.x: Core hydrology / geodesy inputs, elevation + storage logic

Core quantities
---------------
Inputs per site (SI-like units where practical):

- V      : Effective volumetric capacity across all phase states [km^3]
- H      : Hydraulic head differential from inflow crest to lowest spillway [m]
- dS     : Seasonal storage shift (phase swing) [km^3]
- L      : Latent heat budget for the full phase transition [MJ]
- HSI    : Harmonic Symmetry Index in [0,1] (0=irregular; 1=concentric/terraced)

Optional cross‑layer couplers (defaults = None):
- Q_he_ru  : Quartz Resonance Quality, dimensionless in [0,1] (from V4.5)
- S_he_ru  : Solar Forcing Index, normalized in [0,1] (from V4.5)
- X_he_ru  : Electro‑Hydro Coupling χ (chi), normalized in [0,1] (from V4.5)

Primary outputs
---------------
- G_base        : ChiRhombant base term, G = V * H^2 (units: km^3 * m^2)
- G_eff         : Geometry‑adjusted stability, G_base * HSI
- A_season      : Seasonal resonance amplitude factor, f(dS, L)
- R_event       : Resonant event likelihood proxy in [0,1] (if Q/S/X provided)
- period_est    : Characteristic resonance period (years), heuristic
- stability_idx : Final stability score in [0,1] for cross‑site comparison

Notes
-----
This is a *transparent* modeling skeleton. The weighting constants are exposed
for calibration/peer review. Replace with field-derived regressions when available.

CLI
---
Single site (prompted):
    python phase_transition_reservoirs.py

Single site (flags):
    python phase_transition_reservoirs.py --V 900 --H 85 --dS 25 --L 3.2e8 --HSI 0.78 --Q 0.62 --S 0.44 --X 0.35

Batch CSV:
    python phase_transition_reservoirs.py --csv data/sites_v49.csv --out results/v49_scores.csv

Expected CSV columns (case‑insensitive): name,V,H,dS,L,HSI,Q,S,X
"""

from __future__ import annotations
import argparse
import csv
import math
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List


# ----------------------------
# Tunable model coefficients
# ----------------------------

DEFAULT_WEIGHTS: Dict[str, float] = {
    # stability blend
    "w_geom": 0.55,     # weight on geometry-adjusted stability (G_eff)
    "w_season": 0.25,   # weight on seasonal amplitude A_season
    "w_event": 0.20,    # weight on R_event (if Q/S/X present; else re-normalize)
}

# Seasonal amplitude shaping (heuristic scalers)
SEASONAL_SCALERS: Dict[str, float] = {
    "alpha_dS": 0.015,       # sensitivity of amplitude to dS [per km^3]
    "beta_L":  1.0e-9,       # damping by latent heat budget [per MJ]
    "cap": 1.0,              # hard cap on amplitude in [0,1]
}

# Period estimate constants (very lightweight heuristic)
PERIOD_CONSTS: Dict[str, float] = {
    "k_G": 0.00025,   # scales (G_eff)^-1 effect
    "k_S": 3.5,       # scales seasonality effect via dS/V
    "min_years": 0.25,
    "max_years": 5000.0,
}

# Event likelihood coupling weights (if Q/S/X provided)
EVENT_WEIGHTS: Dict[str, float] = {
    "w_Q": 0.45,   # quartz resonance quality
    "w_S": 0.35,   # solar forcing index
    "w_X": 0.20,   # electro-hydrologic coupling
}


@dataclass
class ReservoirInput:
    name: str = "unnamed"
    V: float = 0.0            # km^3
    H: float = 0.0            # m
    dS: float = 0.0           # km^3
    L: float = 0.0            # MJ
    HSI: float = 0.0          # [0,1]
    Q: Optional[float] = None # [0,1]
    S: Optional[float] = None # [0,1]
    X: Optional[float] = None # [0,1]


@dataclass
class ReservoirOutput:
    name: str
    G_base: float
    G_eff: float
    A_season: float
    R_event: Optional[float]
    period_est_years: float
    stability_idx: float
    notes: str = ""


# ----------------------------
# Core computations
# ----------------------------

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_G_base(V: float, H: float) -> float:
    """ChiRhombant base term: G = V * H^2 (km^3 * m^2)"""
    return V * (H ** 2)


def adjust_geometry(G_base: float, HSI: float) -> float:
    """Geometry-adjusted stability using Harmonic Symmetry Index."""
    return G_base * clamp01(HSI)


def compute_seasonal_amplitude(dS: float, L: float, scalers: Dict[str, float]) -> float:
    """
    A_season in [0,1]: larger dS increases amplitude; higher latent heat budget L damps it.
    A = clamp( alpha * dS / (1 + beta * L) )
    """
    alpha = scalers["alpha_dS"]
    beta = scalers["beta_L"]
    cap = scalers["cap"]
    raw = 0.0
    denom = 1.0 + beta * max(L, 0.0)
    if denom <= 0:
        denom = 1.0
    raw = alpha * max(dS, 0.0) / denom
    return clamp01(min(raw, cap))


def compute_event_likelihood(Q: Optional[float], S: Optional[float], X: Optional[float],
                             weights: Dict[str, float]) -> Optional[float]:
    """
    Resonant event likelihood in [0,1] from quartz/solar/EM couplers.
    Returns None if any of Q/S/X is missing.
    """
    if Q is None or S is None or X is None:
        return None
    wQ, wS, wX = weights["w_Q"], weights["w_S"], weights["w_X"]
    total_w = wQ + wS + wX
    if total_w <= 0:
        total_w = 1.0
    score = (wQ * clamp01(Q) + wS * clamp01(S) + wX * clamp01(X)) / total_w
    return clamp01(score)


def estimate_period_years(G_eff: float, V: float, dS: float, consts: Dict[str, float]) -> float:
    """
    Very simple period heuristic (years):
        T ≈ clamp( k_G / (1 + G_eff)  +  k_S * (dS / max(V,eps)) )
    """
    eps = 1e-12
    k_G = consts["k_G"]
    k_S = consts["k_S"]
    t_geom = k_G / (1.0 + max(G_eff, 0.0))
    t_season = 0.0
    if V > eps:
        t_season = k_S * max(dS, 0.0) / V
    T = t_geom + t_season
    T = max(consts["min_years"], min(consts["max_years"], T))
    return T


def compute_stability_index(G_eff: float,
                            A_season: float,
                            R_event: Optional[float],
                            weights: Dict[str, float]) -> float:
    """
    Blend geometry stability, seasonal amplitude (as *inverse* volatility), and event risk.
    By design, higher stability should come from higher G_eff and *lower* A_season, *lower* R_event.
    We map A_stable = 1 - A_season, R_stable = 1 - R_event.

    If R_event is None, we re-normalize weights across the remaining terms.
    """
    w_geom = weights["w_geom"]
    w_season = weights["w_season"]
    w_event = weights["w_event"]

    # Normalize geometry to a bounded [0,1] proxy via logistic-ish squashing
    # This keeps very large G_eff from trivially saturating to 1.
    geom_proxy = 1.0 - math.exp(-1e-8 * max(G_eff, 0.0))  # tunable squashing

    A_stable = 1.0 - clamp01(A_season)

    if R_event is None:
        total = w_geom + w_season
        w_geom_n, w_season_n = w_geom / total, w_season / total
        stability = w_geom_n * geom_proxy + w_season_n * A_stable
    else:
        R_stable = 1.0 - clamp01(R_event)
        total = w_geom + w_season + w_event
        w_geom_n, w_season_n, w_event_n = w_geom / total, w_season / total, w_event / total
        stability = (w_geom_n * geom_proxy
                     + w_season_n * A_stable
                     + w_event_n * R_stable)

    return clamp01(stability)


def score_reservoir(site: ReservoirInput,
                    weights: Dict[str, float] = None,
                    scalers: Dict[str, float] = None,
                    period_consts: Dict[str, float] = None,
                    event_weights: Dict[str, float] = None) -> ReservoirOutput:
    """
    End-to-end scoring for a single site.
    """
    weights = weights or DEFAULT_WEIGHTS
    scalers = scalers or SEASONAL_SCALERS
    period_consts = period_consts or PERIOD_CONSTS
    event_weights = event_weights or EVENT_WEIGHTS

    G_base = compute_G_base(site.V, site.H)
    G_eff = adjust_geometry(G_base, site.HSI)
    A_season = compute_seasonal_amplitude(site.dS, site.L, scalers)
    R_event = compute_event_likelihood(site.Q, site.S, site.X, event_weights)
    period_est = estimate_period_years(G_eff, site.V, site.dS, period_consts)
    stability = compute_stability_index(G_eff, A_season, R_event, weights)

    notes = ""
    if R_event is None:
        notes = "R_event omitted (missing Q/S/X). Weights re-normalized."

    return ReservoirOutput(
        name=site.name,
        G_base=G_base,
        G_eff=G_eff,
        A_season=A_season,
        R_event=R_event,
        period_est_years=period_est,
        stability_idx=stability,
        notes=notes
    )


# ----------------------------
# CLI helpers
# ----------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Codex V4.9: Phase Transition Reservoir scoring (single or batch)."
    )
    p.add_argument("--V", type=float, help="Effective capacity [km^3]")
    p.add_argument("--H", type=float, help="Hydraulic head [m]")
    p.add_argument("--dS", type=float, help="Seasonal storage shift [km^3]")
    p.add_argument("--L", type=float, help="Latent heat budget [MJ]")
    p.add_argument("--HSI", type=float, help="Harmonic Symmetry Index [0..1]")

    p.add_argument("--Q", type=float, help="Quartz resonance (0..1)", dest="Q")
    p.add_argument("--S", type=float, help="Solar forcing (0..1)", dest="S")
    p.add_argument("--X", type=float, help="Electro‑hydro coupling (0..1)", dest="X")

    p.add_argument("--name", type=str, default="unnamed", help="Site name")

    p.add_argument("--csv", type=str, help="Batch input CSV path")
    p.add_argument("--out", type=str, help="Output CSV path for batch mode")

    return p.parse_args()


def _score_row(row: Dict[str, str]) -> ReservoirOutput:
    # Accept case-insensitive headers; strip spaces
    def getf(key: str, default: Optional[float]=None) -> Optional[float]:
        for k in row.keys():
            if k.lower().strip() == key.lower():
                val = row[k].strip()
                if val == "" and default is not None:
                    return default
                return float(val) if val != "" else default
        return default

    def gets(key: str, default: str = "unnamed") -> str:
        for k in row.keys():
            if k.lower().strip() == key.lower():
                val = row[k].strip()
                return val if val != "" else default
        return default

    site = ReservoirInput(
        name=gets("name", "unnamed"),
        V=getf("V", 0.0),
        H=getf("H", 0.0),
        dS=getf("dS", 0.0),
        L=getf("L", 0.0),
        HSI=getf("HSI", 0.0),
        Q=getf("Q", None),
        S=getf("S", None),
        X=getf("X", None),
    )
    return score_reservoir(site)


def _run_single(ns: argparse.Namespace) -> None:
    # If any required scalars missing, prompt interactively
    def ask_float(prompt: str) -> float:
        while True:
            try:
                return float(input(prompt + ": ").strip())
            except ValueError:
                print("Please enter a number.")

    def ask_opt_float(prompt: str) -> Optional[float]:
        s = input(prompt + " (blank to skip): ").strip()
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            print("Skipping invalid entry.")
            return None

    name = ns.name or "unnamed"
    V = ns.V if ns.V is not None else ask_float("V [km^3]")
    H = ns.H if ns.H is not None else ask_float("H [m]")
    dS = ns.dS if ns.dS is not None else ask_float("dS [km^3]")
    L = ns.L if ns.L is not None else ask_float("L [MJ]")
    HSI = ns.HSI if ns.HSI is not None else ask_float("HSI [0..1]")

    Q = ns.Q if ns.Q is not None else ask_opt_float("Q [0..1]")
    S = ns.S if ns.S is not None else ask_opt_float("S [0..1]")
    X = ns.X if ns.X is not None else ask_opt_float("X [0..1]")

    site = ReservoirInput(name=name, V=V, H=H, dS=dS, L=L, HSI=HSI, Q=Q, S=S, X=X)
    out = score_reservoir(site)

    print("\n— Codex V4.9: Phase Transition Reservoir —")
    for k, v in asdict(out).items():
        print(f"{k}: {v}")


def _run_batch(in_csv: str, out_csv: Optional[str]) -> None:
    rows_out: List[Dict[str, Any]] = []
    with open(in_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scored = _score_row(row)
            rows_out.append(asdict(scored))

    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
            writer.writeheader()
            writer.writerows(rows_out)
        print(f"Wrote {len(rows_out)} rows → {out_csv}")
    else:
        # Print to stdout
        for r in rows_out:
            print(r)


def main() -> None:
    ns = _parse_args()
    if ns.csv:
        _run_batch(ns.csv, ns.out)
    else:
        _run_single(ns)


if __name__ == "__main__":
    main()