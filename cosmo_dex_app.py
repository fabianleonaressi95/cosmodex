"""
COSMO-DEX // Quantum Quasicrystal Explorer
Flet UI with live animations + real quasicrystal point sets.
"""

import flet as ft
import random
import math
import time
import threading
import json
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Local quasicrystal generator (fallback if datasets/ not present)
# ---------------------------------------------------------------------------
try:
    from quasicrystal_data import generate_dataset, load_dataset, PHI
except ImportError:
    PHI = (1 + 5 ** 0.5) / 2

    def generate_dataset(kind="cut_project", n_points=200, seed=42):
        import numpy as np
        np.random.seed(seed)
        # Minimal fallback: golden-angle spiral (still aperiodic-ish)
        pts = []
        for i in range(n_points):
            r = math.sqrt(i) * 0.06
            theta = i * 2.399963  # golden angle
            pts.append([r * math.cos(theta), r * math.sin(theta)])
        return {
            "meta": {"type": "golden_spiral_fallback", "n": n_points},
            "points": pts,
            "centroid": [0.0, 0.0],
            "radial_std": 0.4,
            "phi": PHI,
        }

    def load_dataset(path):
        return generate_dataset()


# ---------------------------------------------------------------------------
# Animated StarField that uses real quasicrystal points
# ---------------------------------------------------------------------------
class AnimatedStarField(ft.UserControl):
    def __init__(self, points: List[List[float]], width=450, height=250):
        super().__init__()
        self.width = width
        self.height = height
        self.base_points = points  # normalised [-1,1]
        self.stars: List[ft.Container] = []
        self._running = False
        self._phase = 0.0
        self._phason = 0.0  # external phason drive

    def build(self):
        self.stars = []
        cx, cy = self.width / 2, self.height / 2
        scale = min(self.width, self.height) * 0.42

        for i, (x, y) in enumerate(self.base_points):
            size = 1.5 + (i % 4) * 0.7
            # slight colour variation
            brightness = 180 + (i % 5) * 15
            color = f"#{brightness:02x}{brightness:02x}ff"
            star = ft.Container(
                width=size,
                height=size,
                bgcolor=color,
                border_radius=50,
                left=cx + x * scale,
                top=cy + y * scale,
                opacity=0.7 + (i % 3) * 0.1,
                animate_position=300,
                animate_opacity=400,
            )
            self.stars.append(star)

        return ft.Stack(
            self.stars,
            width=self.width,
            height=self.height,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def set_phason(self, value: float):
        """Called from outside when the phason slider moves."""
        self._phason = value

    def start_animation(self, page: ft.Page):
        if self._running:
            return
        self._running = True

        def loop():
            while self._running:
                self._phase += 0.035
                cx, cy = self.width / 2, self.height / 2
                scale = min(self.width, self.height) * 0.42

                for i, star in enumerate(self.stars):
                    bx, by = self.base_points[i]
                    # gentle breathing + phason shear
                    breathe = 1.0 + 0.04 * math.sin(self._phase + i * 0.17)
                    shear_x = self._phason * 0.18 * by
                    shear_y = -self._phason * 0.12 * bx
                    # tiny orbital drift
                    drift = 0.012 * math.sin(self._phase * 0.6 + i)
                    nx = bx * breathe + shear_x + drift
                    ny = by * breathe + shear_y - drift * 0.7
                    star.left = cx + nx * scale
                    star.top = cy + ny * scale
                    # twinkle
                    star.opacity = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(self._phase * 1.3 + i * 0.4))
                try:
                    page.update()
                except Exception:
                    break
                time.sleep(0.045)

        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._running = False


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "COSMO-DEX // Quantum Quasicrystal Explorer"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 15
    page.bgcolor = "#0B0F19"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 980
    page.window_height = 720

    # ------------------------------------------------------------------
    # Load / generate quasicrystal dataset
    # ------------------------------------------------------------------
    data_dir = Path(__file__).parent / "datasets"
    dataset = None
    for name in ("quasicrystal_cut_project.json", "quasicrystal_ammann.json"):
        p = data_dir / name
        if p.exists():
            try:
                dataset = load_dataset(p)
                break
            except Exception:
                pass
    if dataset is None:
        dataset = generate_dataset(kind="cut_project", n_points=220)

    points = dataset["points"]
    n_pts = len(points)

    # ------------------------------------------------------------------
    # Reactive UI elements
    # ------------------------------------------------------------------
    status_text = ft.Text("ONLINE", color=ft.colors.GREEN_ACCENT, weight=ft.FontWeight.BOLD)
    phason_coord_text = ft.Text("PHASON: [0.000, 0.000]", color=ft.colors.CYAN_ACCENT, size=13)

    l2_error_val = ft.Text("0.0000", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD, size=16)
    w1_dist_val = ft.Text("0.0000", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD, size=16)
    coherence_val = ft.Text("100.0%", color=ft.colors.GREEN_ACCENT, weight=ft.FontWeight.BOLD, size=16)

    # Animated Bragg matrix (simple rotating symbols)
    bragg_symbols = ["✦", "○", "✧", "◈", "✵", "⋆"]
    sk_matrix_text = ft.Text(
        "  ✦  \n✦ ○ ✦\n  ✦  ",
        color=ft.colors.AMBER_ACCENT,
        font_family="monospace",
        size=20,
        text_align=ft.TextAlign.CENTER,
        animate_opacity=300,
    )

    spectral_bar = ft.ProgressBar(
        value=0.15,
        width=220,
        color=ft.colors.CYAN,
        bgcolor=ft.colors.GREY_800,
        bar_height=8,
    )

    mission2_progress = ft.Text("[██████░░░░] RUNNING", size=11, color=ft.colors.AMBER_ACCENT)

    # ------------------------------------------------------------------
    # Star field
    # ------------------------------------------------------------------
    star_field = AnimatedStarField(points, width=460, height=260)

    # ------------------------------------------------------------------
    # Simulation / animation logic
    # ------------------------------------------------------------------
    def compute_metrics(phason: float):
        """Toy physics that reacts to the phason coordinate."""
        abs_p = abs(phason)
        w1 = abs_p * 0.048 + 0.008 + 0.004 * math.sin(phason * 7)
        l2 = abs_p * 0.019 + 0.0035 + 0.002 * math.cos(phason * 5)
        coh = max(62.0, 100.0 - abs_p * 22 - 3 * math.sin(phason * 3) ** 2)
        damage = min(0.95, 0.12 + abs_p * 0.55)
        return w1, l2, coh, damage

    def update_bragg(phason: float):
        """Change the little matrix according to phason."""
        idx = int((phason + 1) * 3) % len(bragg_symbols)
        s = bragg_symbols
        matrix = (
            f"  {s[idx]}  \n"
            f"{s[(idx+1)%6]} {s[(idx+2)%6]} {s[(idx+3)%6]}\n"
            f"  {s[(idx+4)%6]}  "
        )
        sk_matrix_text.value = matrix
        sk_matrix_text.opacity = 0.55
        page.update()
        sk_matrix_text.opacity = 1.0

    def run_simulation(e=None):
        p = phason_slider.value
        phason_coord_text.value = f"PHASON: [{p:.3f}, {-p * 0.5:.3f}]"
        star_field.set_phason(p)

        w1, l2, coh, damage = compute_metrics(p)
        w1_dist_val.value = f"{w1:.4f}"
        l2_error_val.value = f"{l2:.4f}"
        coherence_val.value = f"{coh:.1f}%"
        coherence_val.color = (
            ft.colors.GREEN_ACCENT if coh > 90
            else ft.colors.AMBER_ACCENT if coh > 75
            else ft.colors.RED_ACCENT
        )
        spectral_bar.value = damage

        # Mission progress based on how close we are to the sweet spot
        progress = max(0, min(10, int((1.0 - abs(p)) * 10)))
        bars = "█" * progress + "░" * (10 - progress)
        status = "COMPLETE" if progress >= 9 else "RUNNING"
        color = ft.colors.GREEN_ACCENT if progress >= 9 else ft.colors.AMBER_ACCENT
        mission2_progress.value = f"[{bars}] {status}"
        mission2_progress.color = color

        update_bragg(p)
        page.update()

    phason_slider = ft.Slider(
        min=-1.0,
        max=1.0,
        divisions=200,
        value=0.0,
        on_change=run_simulation,
        active_color=ft.colors.CYAN_ACCENT,
        inactive_color=ft.colors.GREY_700,
        thumb_color=ft.colors.CYAN,
    )

    # ------------------------------------------------------------------
    # Continuous soft animation of metrics (even when idle)
    # ------------------------------------------------------------------
    def soft_pulse():
        t0 = time.time()
        while True:
            t = time.time() - t0
            # very subtle oscillation of the spectral bar when phason ~ 0
            base = spectral_bar.value or 0.15
            spectral_bar.value = max(0.05, min(0.98, base + 0.012 * math.sin(t * 1.8)))
            try:
                page.update()
            except Exception:
                break
            time.sleep(0.08)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    page.add(
        ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Text("🚀 COSMO-DEX", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text("QUANTUM QUASICRYSTAL EXPLORER", size=13, color=ft.colors.CYAN_ACCENT),
                        ft.Container(
                            content=ft.Text(f"Φ = {PHI:.6f}  |  N = {n_pts}", size=11, color=ft.colors.GREY_500),
                            padding=ft.padding.only(left=12),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(color=ft.colors.GREY_800, height=1),

                # Top row: Galaxy Map + Scanner
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("🌌 GALAXY MAP  (Aperiodic Lattice)", size=12, color=ft.colors.GREY_400),
                                    star_field,
                                ],
                                spacing=6,
                            ),
                            padding=12,
                            bgcolor="#111827",
                            border_radius=10,
                            border=ft.border.all(1, ft.colors.GREY_800),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("🛰 SATELLITE SCANNER", size=12, color=ft.colors.GREY_400),
                                    ft.Row([ft.Text("STATUS:", color=ft.colors.WHITE, size=12), status_text]),
                                    phason_coord_text,
                                    ft.Divider(height=8, color=ft.colors.GREY_800),
                                    ft.Text("W₁ DISTANCE", size=11, color=ft.colors.GREY_500),
                                    w1_dist_val,
                                    ft.Text("L₂ ERROR", size=11, color=ft.colors.GREY_500),
                                    l2_error_val,
                                    ft.Text("COHERENCE", size=11, color=ft.colors.GREY_500),
                                    coherence_val,
                                ],
                                spacing=6,
                            ),
                            padding=14,
                            bgcolor="#111827",
                            border_radius=10,
                            width=210,
                            border=ft.border.all(1, ft.colors.GREY_800),
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),

                # Middle row: Bragg + Phason control
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("🔬 BRAGG SPECTRUM  S(k)", size=12, color=ft.colors.GREY_400),
                                    ft.Container(
                                        content=sk_matrix_text,
                                        alignment=ft.alignment.center,
                                        padding=16,
                                        bgcolor="#0d1320",
                                        border_radius=8,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=12,
                            bgcolor="#111827",
                            border_radius=10,
                            expand=True,
                            border=ft.border.all(1, ft.colors.GREY_800),
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("⚛ PHASON CONTROL VECTOR", size=12, color=ft.colors.GREY_400),
                                    phason_slider,
                                    ft.ElevatedButton(
                                        "RUN SIMULATION",
                                        on_click=run_simulation,
                                        bgcolor=ft.colors.CYAN_ACCENT,
                                        color=ft.colors.BLACK,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                                    ),
                                    ft.Text("SPECTRAL DAMAGE", size=11, color=ft.colors.GREY_500),
                                    spectral_bar,
                                ],
                                spacing=10,
                            ),
                            padding=12,
                            bgcolor="#111827",
                            border_radius=10,
                            expand=True,
                            border=ft.border.all(1, ft.colors.GREY_800),
                        ),
                    ],
                    spacing=12,
                ),

                # Mission log
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("📋 MISSION LOG", size=12, color=ft.colors.GREY_400),
                            ft.Row(
                                [
                                    ft.Text("MISSION 001: Locate hidden quasicrystal lattice", size=11, color=ft.colors.WHITE),
                                    ft.Text("[██████████] COMPLETE", size=11, color=ft.colors.GREEN_ACCENT),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                [
                                    ft.Text("MISSION 002: Minimise spectral divergence (L₂ < 0.02)", size=11, color=ft.colors.WHITE),
                                    mission2_progress,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"Dataset: {dataset['meta'].get('type', 'unknown')}  •  points={n_pts}",
                                size=10,
                                color=ft.colors.GREY_600,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=12,
                    bgcolor="#111827",
                    border_radius=10,
                    border=ft.border.all(1, ft.colors.GREY_800),
                ),
            ],
            spacing=12,
            expand=True,
        )
    )

    # Kick off animations after the page is ready
    def on_ready(_=None):
        star_field.start_animation(page)
        threading.Thread(target=soft_pulse, daemon=True).start()
        run_simulation()  # initial state

    page.on_load = on_ready
    # Also call immediately (some Flet versions fire on_load late)
    page.update()
    on_ready()


if __name__ == "__main__":
    ft.app(target=main)
