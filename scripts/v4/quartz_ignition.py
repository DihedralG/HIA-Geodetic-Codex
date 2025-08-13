#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quartz_ignition.py — V4.10 helper

Compute:
  - QII (Quartz Ignition Index) = w_q*Q + w_i*Integrity + w_h*H*
  - RTL (Resonant Trigger Likelihood) = v_s*Solar + v_x*Coupling + v_q*QII

Inputs expected in [0,1] except raw_head_m (meters), which is logistic-scaled.

USAGE
------
# Single-site
python scripts/quartz_ignition.py \
  --quartz 0.72 --integrity 0.64 --raw_head_m 85 \
  --solar 0.38 --coupling 0.41 \
  --out out/quartz_ignition_single.csv

# Batch CSV
python scripts/quartz_ignition.py \
  --csv data/quartz_inputs.csv \
  --out out/quartz_ignition_batch.csv

# Custom weights + head scaling
python scripts/quartz_ignition.py \
  --csv data/quartz_inputs.csv \
  --weights '{"w_q":0.5,"w_i":0.25,"w_h":0.25,"v_s":0.35,"v_x":0.35,"v_q":0.30}' \
  --head-scale '{"k":0.04,"mid":60,"cap":400}'

INPUT CSV SCHEMA (UTF-8)
------------------------
Columns (plain names preferred; Unicode symbols optional and autodetected):
  site_id                (str)
  quartz                 (float in [0,1])          # “Q𐤒ᚩ” accepted
  integrity              (float in [0,1])          # “Ι𐤉ᚱ” accepted
  raw_head_m             (float in meters)         # hydraulic head (unscaled)
  solar                  (float in [0,1])          # “S𐤎ᚦ” accepted
  coupling               (float in [0,1])          # “χ𐤏ᚠ” accepted

OUTPUT CSV COLUMNS
------------------
site_id, quartz, integrity, raw_head_m, head_scaled, solar, coupling,
w_q, w_i, w_h, v_s, v_x, v_q, qii, rtl, notes

NOTES
-----
- If any driver for RTL is missing, weights are re-normalized among present terms
  and a note is appended. Same for QII components.
- Head scaling is logistic with saturation cap and midpoint; see HeadScaler.
- All values are clipped to [0,1] post-normalization where applicable.
"""

from __future__ import annotations
import argparse, csv, json, math, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------- Defaults (transparent & editable) ----------

DEFAULT_WEIGHTS = {
    "w_q": 0.45,   # quartz -> QII
    "w_i": 0.30,   # integrity -> QII
    "w_h": 0.25,   # head_scaled -> QII
    "v_s": 0.40,   # solar -> RTL
    "v_x": 0.30,   # coupling -> RTL
    "v_q": 0.30,   # QII -> RTL
}

# Logistic head scaling defaults: head_scaled = 1 / (1 + exp(-k*(min(head,cap)-mid)))
DEFAULT_HEAD_SCALE = {
    "k": 0.03,     # steepness
    "mid": 50.0,   # midpoint (m) where head_scaled ≈ 0.5
    "cap": 300.0,  # saturation cap (m) to limit runaway heads
}

# Unicode header fallbacks (Charter symbols)
UHEAD = {
    "quartz": "Q𐤒ᚩ",
    "solar": "S𐤎ᚦ",
    "coupling": "χ𐤏ᚠ",
    "integrity": "Ι𐤉ᚱ",
}

# ---------- Helpers ----------

def clip01(x: Optional[float]) -> Optional[float]:
    if x is None: return None
    return max(0.0, min(1.0, x))

def parse_json_obj(s: Optional[str]) -> Dict:
    if not s: return {}
    try:
        obj = json.loads(s)
        if not isinstance(obj, dict):
            raise ValueError("JSON must be an object")
        return obj
    except Exception as e:
        raise SystemExit(f"[ERROR] Invalid JSON: {e}")

@dataclass
class HeadScaler:
    k: float
    mid: float
    cap: float
    def scale(self, head_m: Optional[float]) -> Optional[float]:
        if head_m is None:
            return None
        h = min(max(head_m, 0.0), float(self.cap))
        z = -self.k * (h - self.mid)
        return 1.0 / (1.0 + math.exp(z))

def renormalize(weights: List[Tuple[str, float]], present_flags: Dict[str, bool]) -> Dict[str, float]:
    """
    Given list of (name, weight) and which terms are present, zero missing ones and
    renormalize the rest to sum 1 (if any present).
    """
    present = [(n, w) for (n, w) in weights if present_flags.get(n, False)]
    total = sum(w for _, w in present)
    if total <= 0:
        return {n: 0.0 for n, _ in weights}
    return {n: (w / total if present_flags.get(n, False) else 0.0) for n, w in weights}

def weighted_sum(terms: Dict[str, float], weights: Dict[str, float]) -> float:
    return sum(terms.get(n, 0.0) * weights.get(n, 0.0) for n in weights)

# ---------- Core computation ----------

@dataclass
class QIIInputs:
    quartz: Optional[float]    # [0,1]
    integrity: Optional[float] # [0,1]
    head_scaled: Optional[float] # [0,1]

@dataclass
class RTLInputs:
    solar: Optional[float]     # [0,1]
    coupling: Optional[float]  # [0,1]
    qii: Optional[float]       # [0,1]

def compute_qii(qin: QIIInputs, w: Dict[str, float]) -> Tuple[float, Dict[str, float], str]:
    # Presence flags
    present = {
        "w_q": qin.quartz is not None,
        "w_i": qin.integrity is not None,
        "w_h": qin.head_scaled is not None,
    }
    # Renormalize QII weights over present components
    qii_weights = renormalize([("w_q", w["w_q"]), ("w_i", w["w_i"]), ("w_h", w["w_h"])], present)
    terms = {
        "w_q": clip01(qin.quartz),
        "w_i": clip01(qin.integrity),
        "w_h": clip01(qin.head_scaled),
    }
    qii = weighted_sum(terms, qii_weights)
    note = ""
    if sum(1 for p in present.values() if not p) > 0:
        missing = [n for n, p in present.items() if not p]
        note = f"QII renormalized; missing={','.join(missing)}"
    return clip01(qii), qii_weights, note

def compute_rtl(rin: RTLInputs, w: Dict[str, float]) -> Tuple[float, Dict[str, float], str]:
    present = {
        "v_s": rin.solar is not None,
        "v_x": rin.coupling is not None,
        "v_q": rin.qii is not None,
    }
    rtl_weights = renormalize([("v_s", w["v_s"]), ("v_x", w["v_x"]), ("v_q", w["v_q"])], present)
    terms = {
        "v_s": clip01(rin.solar),
        "v_x": clip01(rin.coupling),
        "v_q": clip01(rin.qii),
    }
    rtl = weighted_sum(terms, rtl_weights)
    note = ""
    if sum(1 for p in present.values() if not p) > 0:
        missing = [n for n, p in present.items() if not p]
        note = f"RTL renormalized; missing={','.join(missing)}"
    return clip01(rtl), rtl_weights, note

# ---------- IO ----------

def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        with path.open("w", encoding="utf-8", newline="") as f:
            f.write("")  # empty
        return
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def get_float(row: Dict[str, str], keys: List[str]) -> Optional[float]:
    for k in keys:
        if k in row and str(row[k]).strip() != "":
            try:
                return float(row[k])
            except ValueError:
                continue
    return None

def process_rows(rows: List[Dict[str, str]], weights: Dict[str, float], scaler: HeadScaler) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for i, r in enumerate(rows, 1):
        site_id = (r.get("site_id") or f"row_{i}").strip()

        quartz = get_float(r, ["quartz", UHEAD["quartz"]])
        integrity = get_float(r, ["integrity", UHEAD["integrity"]])
        raw_head = get_float(r, ["raw_head_m"])
        solar = get_float(r, ["solar", UHEAD["solar"]])
        coupling = get_float(r, ["coupling", UHEAD["coupling"]])

        head_scaled = scaler.scale(raw_head) if raw_head is not None else None

        qii_val, qii_wts, qii_note = compute_qii(
            QIIInputs(quartz=quartz, integrity=integrity, head_scaled=head_scaled), weights
        )
        rtl_val, rtl_wts, rtl_note = compute_rtl(
            RTLInputs(solar=solar, coupling=coupling, qii=qii_val), weights
        )

        note_parts = [s for s in [qii_note, rtl_note] if s]
        notes = " | ".join(note_parts)

        out.append({
            "site_id": site_id,
            "quartz": round(quartz, 6) if quartz is not None else "",
            "integrity": round(integrity, 6) if integrity is not None else "",
            "raw_head_m": round(raw_head, 3) if raw_head is not None else "",
            "head_scaled": round(head_scaled, 6) if head_scaled is not None else "",
            "solar": round(solar, 6) if solar is not None else "",
            "coupling": round(coupling, 6) if coupling is not None else "",
            # weights actually used (after renorm)
            "w_q": round(qii_wts.get("w_q", 0.0), 6),
            "w_i": round(qii_wts.get("w_i", 0.0), 6),
            "w_h": round(qii_wts.get("w_h", 0.0), 6),
            "v_s": round(rtl_wts.get("v_s", 0.0), 6),
            "v_x": round(rtl_wts.get("v_x", 0.0), 6),
            "v_q": round(rtl_wts.get("v_q", 0.0), 6),
            "qii": round(qii_val, 6),
            "rtl": round(rtl_val, 6),
            "notes": notes,
        })
    return out

# ---------- CLI ----------

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compute Quartz Ignition Index (QII) and Resonant Trigger Likelihood (RTL).")
    g_single = p.add_argument_group("single-site inputs")
    g_single.add_argument("--quartz", type=float, help="Quartz resonance quality [0,1]")
    g_single.add_argument("--integrity", type=float, help="Chamber integrity [0,1]")
    g_single.add_argument("--raw_head_m", type=float, help="Hydraulic head (meters)")
    g_single.add_argument("--solar", type=float, help="Solar forcing [0,1]")
    g_single.add_argument("--coupling", type=float, help="Electro-hydro coupling [0,1]")
    g_single.add_argument("--site_id", type=str, default="single_site", help="Identifier for single-site run")

    g_batch = p.add_argument_group("batch mode")
    g_batch.add_argument("--csv", type=str, help="Input CSV path")

    g_cfg = p.add_argument_group("config")
    g_cfg.add_argument("--weights", type=str, help="JSON for weights {w_q,w_i,w_h,v_s,v_x,v_q}")
    g_cfg.add_argument("--head-scale", type=str, help='JSON for head scaling {"k":..., "mid":..., "cap":...}')

    p.add_argument("--out", type=str, required=True, help="Output CSV path")

    args = p.parse_args(argv)

    weights = {**DEFAULT_WEIGHTS, **parse_json_obj(args.weights)}
    hs_cfg = {**DEFAULT_HEAD_SCALE, **parse_json_obj(args.head_scale)}
    scaler = HeadScaler(k=float(hs_cfg["k"]), mid=float(hs_cfg["mid"]), cap=float(hs_cfg["cap"]))

    out_path = Path(args.out)

    # Determine mode
    if args.csv:
        rows = read_csv(Path(args.csv))
        results = process_rows(rows, weights, scaler)
        write_csv(out_path, results)
        print(f"[OK] Wrote {len(results)} rows → {out_path}")
        return 0

    # Single-site mode requires at least one of the QII terms and one RTL driver or QII
    row = {
        "site_id": args.site_id,
        "quartz": args.quartz,
        "integrity": args.integrity,
        "raw_head_m": args.raw_head_m,
        "solar": args.solar,
        "coupling": args.coupling,
    }
    results = process_rows([row], weights, scaler)
    write_csv(out_path, results)
    print(f"[OK] Wrote single-site results → {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())