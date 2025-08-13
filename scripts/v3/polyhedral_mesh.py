#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3 — Polyhedral Elastic-Harmonic Mesh for the Geodetic Codex
Generates a geodesic (subdivided icosahedron) on the unit sphere, scales to Earth,
and exports:
  - nodes.csv (id, face_id, lat, lon)
  - edges.geojson (great-circle links; densified for map rendering)
  - faces.geojson (optional triangular faces)

Target edge length: ~732 miles (~1180 km) along great-circles.
You can override with --target_km or --freq.

Usage
-----
python scripts/v3/polyhedral_mesh.py \
  --out out/v3_mesh \
  --target_km 1180

# or specify frequency subdivision directly:
python scripts/v3/polyhedral_mesh.py --out out/v3_mesh --freq 3

Dependencies: numpy, shapely, pyproj (optional but recommended for robust geodesics)
If pyproj is unavailable, we fall back to spherical linear interpolation (slerp).
"""

from __future__ import annotations
import os, json, math, argparse, csv
import numpy as np

try:
    from shapely.geometry import LineString, Polygon, mapping
    from shapely.ops import unary_union
except Exception:
    LineString = Polygon = None  # still export basic GeoJSON if shapely missing

try:
    from pyproj import Geod
except Exception:
    Geod = None

EARTH_RADIUS_KM = 6371.0088  # IUGG mean spherical equivalent


# ---------- basic icosahedron on unit sphere ---------- #

def icosahedron_vertices_faces():
    """Return (V, F) with V Nx3 unit vectors, F Mx3 int indices (triangles)."""
    phi = (1 + 5 ** 0.5) / 2
    a, b = 1.0, 1.0 / phi
    verts = []
    for x, y, z in [
        (0, ±a, ±b) for ±a in (a, -a) for ±b in (b, -b)
    ] + [
        (±a, ±b, 0) for ±a in (a, -a) for ±b in (b, -b)
    ] + [
        (±b, 0, ±a) for ±a in (a, -a) for ±b in (b, -b)
    ]:
        verts.append((x, y, z))
    # The above Python comprehension is tricky to inline; build explicitly:
    verts = []
    for A in (a, -a):
        for B in (b, -b):
            verts.append((0, A, B))
    for A in (a, -a):
        for B in (b, -b):
            verts.append((A, B, 0))
    for B in (b, -b):
        for A in (a, -a):
            verts.append((B, 0, A))

    V = np.array(verts, dtype=float)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)

    # Faces (indices into V) for a standard icosahedron layout:
    F = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9],  [5, 11, 4], [11, 10, 2],[10, 7, 6], [7, 1, 8],
        [3, 9, 4],  [3, 4, 2],  [3, 2, 6],  [3, 6, 8],  [3, 8, 9],
        [4, 9, 5],  [2, 4, 11], [6, 2, 10], [8, 6, 7],  [9, 8, 1],
    ], dtype=int)
    return V, F


# ---------- geodesic subdivision (frequency f) ---------- #

def subdivide_face(v0, v1, v2, f):
    """Subdivide spherical triangle into f^2 smaller ones. Return list of vertices and triangular faces (local indices)."""
    # Build a grid by linear combos then project to sphere.
    pts = []
    idx = lambda i, j: i*(f+1) + j
    for i in range(f+1):
        for j in range(f+1 - i):
            k = f - i - j
            p = (i*v0 + j*v1 + k*v2) / f
            p = p / np.linalg.norm(p)
            pts.append(p)
    pts = np.array(pts)

    tri = []
    for i in range(f):
        for j in range(f - i):
            a = idx(i, j)
            b = idx(i+1, j)
            c = idx(i, j+1)
            tri.append([a, b, c])
            if j < f - i - 1:
                d = idx(i+1, j+1)
                tri.append([b, d, c])
    return pts, np.array(tri, dtype=int)


def geodesic_icosahedron(f):
    """Return (V, F) of a frequency-f subdivided icosahedron on unit sphere."""
    V0, F0 = icosahedron_vertices_faces()
    verts = []
    faces = []
    offset = 0
    for face_id, (i, j, k) in enumerate(F0):
        p, t = subdivide_face(V0[i], V0[j], V0[k], f)
        faces.append(t + offset)
        verts.append(p)
        offset += len(p)
    V = np.vstack(verts)
    F = np.vstack(faces)
    # Deduplicate vertices (same 3D point shared by adjacent parent faces)
    Vu, inv = np.unique(np.round(V, 8), axis=0, return_inverse=True)
    F = inv[F]
    return Vu, F


# ---------- geometry helpers ---------- #

def cart_to_latlon(v):
    x, y, z = v
    lat = math.degrees(math.asin(z))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon

def edge_length_km(a, b):
    """Great-circle distance (km) on sphere."""
    # Haversine on unit sphere scaled by Earth radius:
    lat1, lon1 = cart_to_latlon(a)
    lat2, lon2 = cart_to_latlon(b)
    φ1, λ1, φ2, λ2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dφ = φ2-φ1; dλ = λ2-λ1
    h = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    return 2*EARTH_RADIUS_KM*math.asin(min(1.0, math.sqrt(h)))

def densify_gc(lat1, lon1, lat2, lon2, n=32):
    """Points along great-circle; uses pyproj.Globe if available, else slerp."""
    if Geod is not None:
        g = Geod(a=EARTH_RADIUS_KM*1000, b=EARTH_RADIUS_KM*1000)
        lats, lons = g.npts(lon1, lat1, lon2, lat2, n-2)
        coords = [(lon1, lat1)] + [(lo, la) for lo, la in zip(lons, lats)] + [(lon2, lat2)]
        return coords
    # slerp on unit sphere
    def to_xyz(lat, lon):
        φ, λ = math.radians(lat), math.radians(lon)
        return np.array([math.cos(φ)*math.cos(λ), math.cos(φ)*math.sin(λ), math.sin(φ)])
    a = to_xyz(lat1, lon1); b = to_xyz(lat2, lon2)
    dot = np.clip(np.dot(a, b), -1.0, 1.0)
    θ = math.acos(dot)
    if θ < 1e-9:
        return [(lon1, lat1), (lon2, lat2)]
    pts = []
    for t in np.linspace(0, 1, n):
        s1 = math.sin((1-t)*θ) / math.sin(θ)
        s2 = math.sin(t*θ) / math.sin(θ)
        v = s1*a + s2*b
        v = v / np.linalg.norm(v)
        la, lo = cart_to_latlon(v)
        pts.append((lo, la))
    return pts

def face_edges(F):
    """Set of undirected edges (i,j) with i<j from triangular faces."""
    E = set()
    for a,b,c in F:
        for i,j in ((a,b),(b,c),(c,a)):
            if i>j: i,j=j,i
            E.add((i,j))
    return sorted(list(E))


# ---------- choosing frequency for target edge ---------- #

def choose_frequency(target_km):
    """
    Find geodesic frequency f whose median edge length is closest to target_km.
    Reasonable f for global meshes: 1..10 (keeps node count tractable).
    """
    best = (None, 1e9, None)
    for f in range(1, 11):
        V, F = geodesic_icosahedron(f)
        E = face_edges(F)
        dists = [edge_length_km(V[i], V[j]) for i,j in E]
        med = float(np.median(dists))
        err = abs(med - target_km)
        if err < best[1]:
            best = (f, err, med)
    return best  # (f, |Δ|, achieved_med)


# ---------- export utilities ---------- #

def export_nodes_csv(path, V, face_of_node):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id","face_id","lat","lon"])
        for i, v in enumerate(V):
            lat, lon = cart_to_latlon(v)
            w.writerow([i, face_of_node.get(i, -1), f"{lat:.6f}", f"{lon:.6f}"])

def export_edges_geojson(path, V, E, densify=48):
    feats = []
    for i, j in E:
        lat1, lon1 = cart_to_latlon(V[i])
        lat2, lon2 = cart_to_latlon(V[j])
        line = densify_gc(lat1, lon1, lat2, lon2, n=densify)
        geom = {"type":"LineString","coordinates":[[lo, la] for lo, la in line]}
        feats.append({"type":"Feature","geometry":geom,"properties":{"u":i,"v":j}})
    fc = {"type":"FeatureCollection","features":feats}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(fc, f)

def export_faces_geojson(path, V, F):
    feats = []
    for fid, (a,b,c) in enumerate(F):
        latlon = [cart_to_latlon(V[k]) for k in (a,b,c,a)]
        geom = {"type":"Polygon","coordinates":[[[lo,la] for lo,la in [(lon,lat) for lat,lon in latlon]]]}
        feats.append({"type":"Feature","geometry":geom,"properties":{"face_id":fid}})
    fc = {"type":"FeatureCollection","features":feats}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(fc, f)


# ---------- main ---------- #

def main():
    ap = argparse.ArgumentParser(description="V3 polyhedral/geodesic mesh generator")
    ap.add_argument("--out", required=True, help="output directory/prefix (e.g., out/v3_mesh)")
    ap.add_argument("--target_km", type=float, default=1180.0, help="target edge length (km)")
    ap.add_argument("--freq", type=int, default=None, help="override geodesic frequency (1..10)")
    ap.add_argument("--write_faces", action="store_true", help="export faces.geojson")
    args = ap.parse_args()

    if args.freq is None:
        f, err, med = choose_frequency(args.target_km)
        print(f"Selected frequency f={f} (median edge ≈ {med:.1f} km; Δ={err:.1f} km)")
    else:
        f = args.freq
        print(f"Using user-specified frequency f={f}")

    V, F = geodesic_icosahedron(f)
    E = face_edges(F)

    # optional: a simple "face ownership" per node (first face that contains it)
    face_of_node = {}
    for fid, tri in enumerate(F):
        for k in tri:
            face_of_node.setdefault(int(k), fid)

    prefix = args.out.rstrip("/")
    export_nodes_csv(prefix + "_nodes.csv", V, face_of_node)
    export_edges_geojson(prefix + "_edges.geojson", V, E, densify=48)
    if args.write_faces:
        export_faces_geojson(prefix + "_faces.geojson", V, F)

    # quick stats
    dists = [edge_length_km(V[i], V[j]) for i,j in E]
    print(f"Edges: {len(E)} | median={np.median(dists):.1f} km | min={np.min(dists):.1f} | max={np.max(dists):.1f}")
    print(f"Nodes: {len(V)} | Faces: {len(F)}")
    print(f"✓ Wrote: {prefix}_nodes.csv, {prefix}_edges.geojson" + (", faces.geojson" if args.write_faces else ""))

if __name__ == "__main__":
    main()