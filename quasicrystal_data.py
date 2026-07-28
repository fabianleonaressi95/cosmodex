"""
COSMO-DEX // Quasicrystal Dataset Generator
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, Any, Union

PHI = (1.0 + np.sqrt(5.0)) / 2.0


def fibonacci_word_points(n=200, scale=1.0):
    s = "0"
    while len(s) < n + 10:
        s = s.replace("0", "a").replace("1", "0").replace("a", "01")
    s = s[:n]
    positions = []
    x = 0.0
    for c in s:
        positions.append(x)
        x += scale * (PHI if c == "0" else 1.0)
    return np.array(positions)


def cut_and_project_2d(n_points=300, window_size=1.0, slope=PHI, scale=8.0):
    side = int(np.ceil(np.sqrt(n_points * 8)))
    xs = np.arange(-side, side + 1)
    ys = np.arange(-side, side + 1)
    xx, yy = np.meshgrid(xs, ys)
    lattice = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(float)

    v = np.array([-slope, 1.0])
    v /= np.linalg.norm(v)

    coords_v = lattice @ v
    mask = np.abs(coords_v) < window_size
    selected = lattice[mask]

    e1 = np.array([1.0, 0.0])
    e2 = np.array([0.5, np.sqrt(3) / 2])
    twist = np.array([[1.0, 0.1 * PHI], [-0.07 * PHI, 1.0]])
    points = (selected @ twist) @ np.stack([e1, e2], axis=0).T
    points *= scale / (side * 0.4)

    dists = np.linalg.norm(points, axis=1)
    idx = np.argsort(dists)[:n_points]
    return points[idx]


def ammann_beenker_approx(n_points=250, scale=10.0):
    angles = np.array([0, np.pi / 4, np.pi / 2, 3 * np.pi / 4])
    points = []
    density = int(np.ceil(np.sqrt(n_points / 2.0)))
    for a in angles:
        c, s = np.cos(a), np.sin(a)
        for i in range(-density, density + 1):
            for j in range(-density, density + 1):
                shift = (i * 0.41421356237 + j * 0.17157287525) % 1.0
                if shift < 0.55:
                    x = (i * c - j * s) * scale / density
                    y = (i * s + j * c) * scale / density
                    points.append([x, y])
    pts = np.array(points)
    pts -= pts.mean(axis=0)
    dists = np.linalg.norm(pts, axis=1)
    idx = np.argsort(dists)[:n_points]
    return pts[idx]


def generate_dataset(kind="cut_project", n_points=300, seed=42):
    np.random.seed(seed)
    if kind == "fibonacci":
        pts_1d = fibonacci_word_points(n_points)
        t = np.linspace(0, 2 * np.pi, n_points)
        pts = np.stack([pts_1d * np.cos(t * 0.3), pts_1d * np.sin(t * 0.3)], axis=1)
        meta = {"type": "fibonacci_1d_lifted", "n": n_points}
    elif kind == "ammann":
        pts = ammann_beenker_approx(n_points)
        meta = {"type": "ammann_beenker_approx", "n": len(pts)}
    else:
        pts = cut_and_project_2d(n_points)
        meta = {"type": "cut_and_project_2d", "n": len(pts), "phi": float(PHI)}

    max_abs = np.max(np.abs(pts)) + 1e-9
    pts_norm = pts / max_abs

    return {
        "meta": meta,
        "points": pts_norm.tolist(),
        "centroid": pts_norm.mean(axis=0).tolist(),
        "radial_std": float(np.std(np.linalg.norm(pts_norm, axis=1))),
        "phi": float(PHI),
    }


def save_dataset(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved -> {} ({} points)".format(path, data["meta"]["n"]))


def load_dataset(path):
    with open(str(path), "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    out_dir = Path(__file__).parent / "datasets"
    for kind in ("cut_project", "ammann", "fibonacci"):
        data = generate_dataset(kind=kind, n_points=280)
        save_dataset(data, out_dir / ("quasicrystal_" + kind + ".json"))
    print("All datasets generated.")
