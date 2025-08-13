#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3 polyhedral / geodesic mesh generator (GeoJSON / ASCII-safe)

- Builds a unit icosahedron, subdivides triangle faces by frequency f, projects to sphere.
- Exports:
    out/v3_mesh_nodes.geojson   (Points)
    out/v3_mesh_edges.geojson   (LineStrings; densified)
    out/v3_mesh_faces.geojson   (Polygons; one ring per face)

Use either:
    python scripts/v3/polyhedral_mesh.py --out out/v3_mesh --f 6
or:
    python scripts/v3/polyhedral_mesh.py --out out/v3_mesh --target_km 732
"""

from __future__ import annotations
import os, json, math, argparse
from typing import Dict, Tuple, List
import numpy as np

EARTH_R_KM = 6371.0088

# -------------------------- vector helpers -------------------------- #

def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    """Spherical linear interpolation on the unit sphere."""
    a = normalize(a); b = normalize(b)
    dot = np.clip(np.dot(a, b), -1.0, 1.0)
    omega = math.acos(dot)
    if omega < 1e-10:
        return a  # nearly identical
    so = math.sin(omega)
    return (math.sin((1 - t) * omega) / so) * a + (math.sin(t * omega) / so) * b

def gc_distance_km(a: np.ndarray, b: np.ndarray) -> float:
    """Great-circle distance between two unit vectors (km)."""
    a = normalize(a); b = normalize(b)
    ang = math.acos(np.clip(np.dot(a, b), -1.0, 1.0))
    return EARTH_R_KM * ang

def cart_to_latlon(v: np.ndarray) -> Tuple[float, float]:
    """Return (lat, lon) in degrees from unit xyz."""
    x, y, z = v
    lat = math.degrees(math.asin(np.clip(z, -1.0, 1.0)))
    lon = math.degrees(math.atan2(y, x))
    return (lat, lon)

# ----------------------- icosahedron + subdivision ------------------ #

def icosahedron() -> Tuple[np.ndarray, List[Tuple[int,int,int]]]:
    """Return vertices (Nx3) and 20 faces of a unit icosahedron."""
    phi = (1 + 5 ** 0.5) / 2
    verts = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            verts.append((0, s1, s2 * phi))
            verts.append((s1, s2 * phi, 0))
            verts.append((s1 * phi, 0, s2))
    V = np.array([normalize(np.array(v, dtype=float)) for v in verts], dtype=float)
    F = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
    ]
    return V, F

def subdivide_face(V: np.ndarray, tri: Tuple[int,int,int], f: int,
                   cache: Dict[Tuple[int,int], int]) -> List[Tuple[int,int,int]]:
    """
    Subdivide a single triangular face with frequency f.
    Returns list of new triangle indices; extends V and uses cache for mid-edges.
    """
    def midpoint(i: int, j: int) -> int:
        key = (min(i, j), max(i, j))
        if key in cache:
            return cache[key]
        m = normalize((V[i] + V[j]) * 0.5)
        V_list.append(m)
        idx = len(V_list) - 1
        cache[key] = idx
        return idx

    a, b, c = tri
    V_list = V.tolist()  # we’ll append and convert back later

    # Build grid of points on the triangle via spherical interpolation
    # Using barycentric steps along edges (a->b) and (a->c)
    grid: List[List[int]] = []
    for i in range(f + 1):
        row = []
        ab = slerp(V[a], V[b], i / f) if f > 0 else V[a]
        ac = slerp(V[a], V[c], i / f) if f > 0 else V[a]
        steps = f - i
        for j in range(steps + 1):
            p = slerp(ab, ac, 0 if steps == 0 else j / steps)
            V_list.append(normalize(p))
            row.append(len(V_list) - 1)
        grid.append(row)

    # Triangulate the grid
    tris: List[Tuple[int,int,int]] = []
    for i in range(f):
        for j in range(f - i):
            v00 = grid[i][j]
            v01 = grid[i][j + 1]
            v10 = grid[i + 1][j]
            v11 = grid[i + 1][j + 1]
            tris.append((v00, v01, v11))
            if j < f - i - 1:
                tris.append((v00, v11, v10))

    # Update V from V_list
    V_out = np.array(V_list, dtype=float)
    return V_out, tris

def geodesic_icosahedron(f: int) -> Tuple[np.ndarray, List[Tuple[int,int]], List[Tuple[int,int,int]]]:
    """Subdivide each face of the icosahedron by frequency f and return (V, E, F)."""
    V, F0 = icosahedron()
    if f <= 1:
        F = F0[:]
    else:
        F: List[Tuple[int,int,int]] = []
        cache: Dict[Tuple[int,int], int] = {}
        for tri in F0:
            V, tris = subdivide_face(V, tri, f, cache)
            F.extend(tris)

    # Build edge set
    edges = set()
    for a, b, c in F:
        for i, j in ((a, b), (b, c), (c, a)):
            if i != j:
                edges.add((min(i, j), max(i, j)))
    E = sorted(edges)
    return V, E, F

# ---------------------------- exporters ----------------------------- #

def export_nodes_geojson(prefix: str, V: np.ndarray):
    feats = []
    for i, v in enumerate(V):
        lat, lon = cart_to_latlon(v)
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [lon, lat]},
                      "properties": {"id": int(i)}})
    fc = {"type": "FeatureCollection", "features": feats}
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    with open(f"{prefix}_nodes.geojson", "w") as f:
        json.dump(fc, f)

def export_edges_geojson(prefix: str, V: np.ndarray, E: List[Tuple[int,int]], densify: int = 12):
    feats = []
    for u, v in E:
        a = V[u]; b = V[v]
        line = []
        for t in np.linspace(0.0, 1.0, max(2, densify)):
            p = normalize(slerp(a, b, float(t)))
            lat, lon = cart_to_latlon(p)
            line.append([lon, lat])
        feats.append({"type": "Feature",
                      "geometry": {"type": "LineString", "coordinates": line},
                      "properties": {"u": int(u), "v": int(v)}})
    fc = {"type": "FeatureCollection", "features": feats}
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    with open(f"{prefix}_edges.geojson", "w") as f:
        json.dump(fc, f)

def export_faces_geojson(prefix: str, V: np.ndarray, F: List[Tuple[int,int,int]]):
    feats = []
    for fid, (a, b, c) in enumerate(F):
        ring = []
        for idx in (a, b, c, a):  # close ring
            lat, lon = cart_to_latlon(V[idx])
            ring.append([lon, lat])
        feats.append({"type": "Feature",
                      "geometry": {"type": "Polygon", "coordinates": [ring]},
                      "properties": {"face_id": int(fid)}})
    fc = {"type": "FeatureCollection", "features": feats}
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    with open(f"{prefix}_faces.geojson", "w") as f:
        json.dump(fc, f)

# ------------------------ sizing & reporting ------------------------ #

def edge_lengths_km(V: np.ndarray, E: List[Tuple[int,int]]) -> np.ndarray:
    return np.array([gc_distance_km(V[i], V[j]) for i, j in E], dtype=float)

def choose_frequency(target_km: float, f_min: int = 1, f_max: int = 12) -> Tuple[int, float, float]:
    """Pick f so that the median edge length is closest to target_km. Returns (f, err, median)."""
    best = None
    for f in range(f_min, f_max + 1):
        V, E, _ = geodesic_icosahedron(f)
        d = edge_lengths_km(V, E)
        med = float(np.median(d))
        err = abs(med - target_km)
        if best is None or err < best[1]:
            best = (f, err, med)
    return best  # type: ignore

# ---------------------------- public API ---------------------------- #

def generate_mesh(out: str, target_km: float | None = None, f: int | None = None, densify: int = 12):
    """
    Programmatic entry point (Kaggle/Colab safe).
    Provide exactly one of (target_km, f).
    """
    if (f is None) == (target_km is None):
        raise ValueError("Provide exactly one of f or target_km")

    if f is None:
        f, err, med = choose_frequency(float(target_km))
        print(f"[chooser] f={f}  median={med:.1f} km  |Δ|={err:.1f} km  (target={float(target_km):.1f} km)")
    else:
        print(f"[fixed] using f={f}")

    V, E, F = geodesic_icosahedron(int(f))
    d = edge_lengths_km(V, E)
    print(f"[mesh] nodes={len(V)}  edges={len(E)}  faces={len(F)}")
    print(f"[edges] median={np.median(d):.1f} km  min={np.min(d):.1f}  max={np.max(d):.1f}")

    prefix = out.rstrip("/")
    export_nodes_geojson(prefix, V)
    export_edges_geojson(prefix, V, E, densify=max(2, int(densify)))
    export_faces_geojson(prefix, V, F)
    print(f"[write] {prefix}_nodes.geojson")
    print(f"[write] {prefix}_edges.geojson")
    print(f"[write] {prefix}_faces.geojson")



# ---------------------------- faces helper ---------------------------- #
def export_faces_geojson(prefix: str, V: np.ndarray, F: List[Tuple[int, int, int]]) -> None:
    """
    Save triangular faces as a GeoJSON FeatureCollection of Polygons.
    Each triangle ring is closed (first point repeated at end).
    Coordinates are [lon, lat] in WGS84.
    """
    feats = []
    for fid, (a, b, c) in enumerate(F):
        latA, lonA = cart_to_latlon(V[a])
        latB, lonB = cart_to_latlon(V[b])
        latC, lonC = cart_to_latlon(V[c])
        ring = [[lonA, latA], [lonB, latB], [lonC, latC], [lonA, latA]]  # closed ring
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {"id": fid}
        })

    fc = {"type": "FeatureCollection", "features": feats}
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    with open(f"{prefix}_faces.geojson", "w") as f:
        json.dump(fc, f)


# ------------------------------ CLI -------------------------------- #

def main():
    ap = argparse.ArgumentParser(description="V3 geodesic mesh generator (GeoJSON)")
    ap.add_argument("--out", required=True, help="output path prefix, e.g., out/v3_mesh")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--f", type=int, help="subdivision frequency (1..12)")
    group.add_argument("--target_km", type=float, help="target median edge length (km)")
    ap.add_argument("--densify", type=int, default=12, help="points per edge for LineString")
    args = ap.parse_args()

    generate_mesh(out=args.out, target_km=args.target_km, f=args.f, densify=args.densify)

if __name__ == "__main__":
    main()