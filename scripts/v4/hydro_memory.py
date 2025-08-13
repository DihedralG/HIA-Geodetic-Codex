"""
ChiR-IPP helpers: subterranean memory + coupling

voidgraph(): build a karst/aquifer conduit graph and return basic metrics
glift():     compute G = V * H^2 from minimal state layers

Dependencies (all widely available):
  - numpy (required)
  - networkx (required)
  - scipy (optional: for ndimage label/skeleton)
  - rasterio/xarray (optional: for I/O, not required by these funcs)

Author: ChiR Labs, 2025 — MIT-style reference implementation
"""

from __future__ import annotations
import numpy as np
import networkx as nx

# ---------- small utilities ----------

def _norm01(a, eps=1e-9):
    """Min-max scale to [0,1] with nan-safety."""
    a = np.asarray(a, float)
    m, M = np.nanmin(a), np.nanmax(a)
    if not np.isfinite(m) or not np.isfinite(M) or abs(M - m) < eps:
        return np.zeros_like(a, float)
    out = (a - m) / (M - m + eps)
    return np.clip(out, 0.0, 1.0)

def _grad_mag(z):
    """Finite-difference gradient magnitude (cell-size agnostic if z is in meters)."""
    gy, gx = np.gradient(z.astype(float))
    return np.hypot(gx, gy)

def _eight_neighbors(shape, y, x):
    """Yield (ny, nx) within 8-neighborhood bounds."""
    H, W = shape
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W:
                yield ny, nx

# ---------- core API ----------

def voidgraph(
    dem: np.ndarray,
    aquifer_mask: np.ndarray,
    transmissivity: np.ndarray | float,
    min_slope: float = 1e-4,
    t_weight: float = 0.6,
    s_weight: float = 0.4,
):
    """
    Build a conduit graph over cells where aquifer_mask==1.
    Edge capacity is a blend of local transmissivity and downslope preference.

    Args
    ----
    dem : 2D array (meters). Can be a cave-floor DEM or piezometric surface.
    aquifer_mask : 2D boolean/int array; True/1 where conduits/storage exist.
    transmissivity : 2D array (m^2/s) or float (scalar T) for the mask.
    min_slope : floors slope so flat areas still connect modestly.
    t_weight, s_weight : weights for T and slope in edge scoring (sum ~1.0).

    Returns
    -------
    G : networkx.DiGraph with nodes=(y,x) and edge attr:
        'w' (weight 0..1), 'slope' (>=0), 'Tn' (0..1)
    metrics : dict with:
        'kappa'  : normalized connectivity (giant component size / nodes)
        'lambda' : characteristic path length (normed 0..1 by graph diameter)
        'edges'  : number of edges
        'nodes'  : number of nodes
    """
    dem = np.asarray(dem, float)
    mask = aquifer_mask.astype(bool)
    if np.isscalar(transmissivity):
        T = np.full_like(dem, float(transmissivity))
    else:
        T = np.asarray(transmissivity, float)

    # restrict to mask
    dem_m = np.where(mask, dem, np.nan)
    T_m = np.where(mask, T, np.nan)

    # slope proxy (higher is “downhill potential”)
    # we want positive “driving” even in flats, so floor it
    slope = _grad_mag(dem_m)
    slope = np.nan_to_num(slope, nan=0.0)
    slope = np.maximum(slope, min_slope)

    # normalize layers inside mask
    Tn = _norm01(np.where(mask, T_m, np.nan))
    Sn = _norm01(np.where(mask, slope, np.nan))

    H, W = dem.shape
    G = nx.DiGraph()

    # add nodes
    ys, xs = np.where(mask)
    for y, x in zip(ys, xs):
        G.add_node((y, x))

    # add edges (8-neighbors), favoring downslope and high T
    for y, x in zip(ys, xs):
        z = dem_m[y, x]
        for ny, nx in _eight_neighbors((H, W), y, x):
            if not mask[ny, nx]:
                continue
            dz = z - dem_m[ny, nx]  # positive if neighbor is lower (downhill)
            downhill = 1.0 if dz > 0 else 0.5  # mild penalty for upslope links
            # combine transmissivity at source/target and local slope
            Tloc = 0.5 * (Tn[y, x] + Tn[ny, nx])
            Sloc = max(Sn[y, x], Sn[ny, nx])
            w = downhill * (t_weight * Tloc + s_weight * Sloc)
            if w > 0:
                G.add_edge((y, x), (ny, nx), w=float(w), slope=float(Sloc), Tn=float(Tloc))

    # metrics
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    if n_nodes == 0:
        return G, dict(kappa=0.0, lambda_=0.0, nodes=0, edges=0)

    # giant weakly-connected size as connectivity proxy
    if n_nodes > 0:
        comps = list(nx.weakly_connected_components(G))
        giant = max((len(c) for c in comps), default=0)
        kappa = giant / float(n_nodes)
    else:
        kappa = 0.0

    # characteristic path length on weighted UNDIRECTED projection (approx)
    if n_nodes > 1 and n_edges > 0:
        UG = G.to_undirected()
        # convert “capacity-like” w (higher is easier) into distance (lower is better)
        for u, v, d in UG.edges(data=True):
            d['dist'] = 1.0 / (d.get('w', 1e-6) + 1e-6)
        try:
            # use giant component only
            gc_nodes = max(nx.connected_components(UG), key=len)
            UG_gc = UG.subgraph(gc_nodes).copy()
            spl = dict(nx.all_pairs_dijkstra_path_length(UG_gc, weight='dist'))
            # average pairwise distance
            vals = []
            keys = list(UG_gc.nodes())
            for i in range(len(keys)):
                di = spl.get(keys[i], {})
                for j in range(i + 1, len(keys)):
                    d = di.get(keys[j])
                    if d is not None:
                        vals.append(d)
            lam = np.mean(vals) if vals else 0.0
            # normalize by a rough upper bound (grid diameter)
            Hh, Ww = dem.shape
            dia = np.hypot(Hh, Ww)
            lambda_norm = 1.0 - np.tanh(lam / (dia + 1e-6))  # higher is “tighter” network
        except Exception:
            lambda_norm = 0.0
    else:
        lambda_norm = 0.0

    metrics = dict(kappa=float(kappa), lambda_=float(lambda_norm),
                   nodes=int(n_nodes), edges=int(n_edges))
    return G, metrics


def glift(
    grad_head: np.ndarray,
    strain_rate: np.ndarray,
    memory_entropy: np.ndarray,
    resonance_centrality: np.ndarray | None = None,
    v_alpha: float = 0.5,
    v_beta: float = 0.5,
    h_gamma: float = 0.7,
    h_delta: float = 0.3,
):
    """
    Compute G = V * H^2 on a per-cell basis with simple, transparent components.

    Args
    ----
    grad_head : 2D array — |∇φ| piezometric gradient (e.g., m/m); proxy for hydraulic drive.
    strain_rate : 2D array — |ε̇| or |σ̇| (per yr), any consistent scalar stress/strain rate metric.
    memory_entropy : 2D array — H_chem (0..1 recommended), e.g., entropy of isotope/solute series.
    resonance_centrality : 2D array or None — optional R* (0..1): mineral resonance × conduit centrality.
    v_alpha, v_beta : weights summing ~1 for V blend (hydraulic vs tectonic drive).
    h_gamma, h_delta : weights summing ~1 for H blend (chemical memory vs resonant conduit).

    Returns
    -------
    out : dict with 2D arrays
      V : normalized hydraulic/tectonic drive (0..1)
      H : normalized memory strength (0..1)
      G : V * H^2  (0..1 after internal scaling)
    """
    gh = _norm01(grad_head)
    sr = _norm01(strain_rate)
    V = np.clip(v_alpha * gh + v_beta * sr, 0.0, 1.0)

    Hc = _norm01(memory_entropy)
    if resonance_centrality is None:
        Hr = np.zeros_like(Hc)
        h_delta = 0.0
        h_gamma = 1.0
    else:
        Hr = _norm01(resonance_centrality)

    H = np.clip(h_gamma * Hc + h_delta * Hr, 0.0, 1.0)

    # raw G
    G_raw = V * (H ** 2)

    # final normalization to 0..1 for map comparability
    G = _norm01(G_raw)

    return dict(V=V, H=H, G=G)