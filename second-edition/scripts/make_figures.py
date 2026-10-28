#!/usr/bin/env python3
"""Generate every figure for the second edition.

All diagrams are drawn from physics or from published, cited numbers, so the
book carries no scanned textbook figures. Run from anywhere:

    python3 second-edition/scripts/make_figures.py

Output goes to second-edition/images/<chapter>/<name>.svg
"""
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parent.parent / "images"

# Validated categorical palette (fixed order) and text tokens.
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#6250d6", "#e34948",
)
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "axes.edgecolor": MUTED,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "lines.linewidth": 2,
    "legend.frameon": False,
    "svg.fonttype": "path",
})

# Planck 2018 (TT,TE,EE+lowE+lensing) cosmology used throughout.
H0 = 67.4                     # km/s/Mpc
OM, OL = 0.315, 0.685
OR = 9.15e-5                  # photons + three massless neutrino species
T_CMB = 2.7255                # K (Fixsen 2009)
H0_SI = H0 * 1e3 / 3.0857e22  # 1/s
GYR = 3.156e16                # s
HUBBLE_TIME_GYR = 1 / H0_SI / GYR


def E(z, om=OM, ol=OL, orad=OR):
    ok = 1 - om - ol - orad
    return np.sqrt(orad * (1 + z) ** 4 + om * (1 + z) ** 3 + ok * (1 + z) ** 2 + ol)


def save(fig, chapter, name):
    out = ROOT / chapter
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.svg", bbox_inches="tight", pad_inches=0.15)
    if os.environ.get("PREVIEW_DIR"):  # optional PNG copies for proofreading
        fig.savefig(Path(os.environ["PREVIEW_DIR"]) / f"{chapter}-{name}.png", dpi=90,
                    bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out / f"{name}.svg")


def blank(ax):
    ax.set_axis_off()
    ax.set_aspect("equal")


def arrow(ax, p, q, color=INK2, lw=1.4, style="-|>", ms=10, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0, **kw))


# --------------------------------------------------------------------------
# Chapter 1
# --------------------------------------------------------------------------
def telescope_foci():
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.4))
    titles = ["(a) Prime focus", "(b) Newtonian focus",
              "(c) Cassegrain focus", "(d) Coudé focus"]
    for ax, title in zip(axes.flat, titles):
        blank(ax)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-2.6, 2.6)
        ax.set_title(title, loc="left", fontsize=11, color=INK)
        # tube
        ax.add_patch(Rectangle((1, -1.6), 8.2, 3.2, fill=False, ec=MUTED, lw=1))
        # primary mirror (concave, at right end)
        ax.add_patch(Arc((14.0, 0), 10, 10, theta1=160, theta2=200, color=INK, lw=3))

    rays_y = [-1.2, -0.6, 0.6, 1.2]
    mirror_x = lambda y: 14.0 - np.sqrt(25 - y ** 2)
    f = 3.6  # focus x for primary

    def incoming(ax, stop=None):
        for y in rays_y:
            x_m = mirror_x(y)
            ax.plot([-0.3, x_m], [y, y], color=BLUE, lw=1.1)

    # (a) prime focus: rays converge to f, detector there
    ax = axes[0, 0]
    incoming(ax)
    for y in rays_y:
        ax.plot([mirror_x(y), f], [y, 0], color=ORANGE, lw=1.1)
    ax.add_patch(Rectangle((f - 0.5, -0.3), 0.5, 0.6, color=INK))
    ax.annotate("detector at focus", (f - 0.3, 0.3), (1.2, 2.1), fontsize=9,
                color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    # (b) Newtonian: flat diagonal mirror sends beam out the side
    ax = axes[0, 1]
    incoming(ax)
    xd = 5.4
    for y in rays_y:
        xm = mirror_x(y)
        yd = y * (xd - f) / (xm - f)
        ax.plot([xm, xd], [y, yd], color=ORANGE, lw=1.1)
        ax.plot([xd, xd + (yd * 0)], [yd, 2.3], color=ORANGE, lw=1.1, alpha=0.9)
    ax.plot([xd - 0.45, xd + 0.45], [-0.45, 0.45], color=INK, lw=3)
    ax.plot(xd, 2.35, marker="o", color=INK, ms=5)
    ax.text(xd + 0.3, 2.25, "focus", fontsize=9, color=INK2, va="center")

    # (c) Cassegrain: convex secondary sends beam back through hole in primary
    ax = axes[1, 0]
    incoming(ax)
    xs = 4.6
    for y in rays_y:
        xm = mirror_x(y)
        ys = y * (xs - f) / (xm - f)
        ax.plot([xm, xs], [y, ys], color=ORANGE, lw=1.1)
        ax.plot([xs, 10.3], [ys, 0], color=ORANGE, lw=1.1)
    ax.plot([xs, xs], [-0.5, 0.5], color=INK, lw=3)
    ax.add_patch(Rectangle((8.7, -0.18), 0.8, 0.36, color=SURFACE, zorder=3))
    ax.plot(10.3, 0, marker="o", color=INK, ms=5)
    ax.text(10.1, -0.6, "focus", fontsize=9, color=INK2, ha="center")
    ax.text(8.3, 1.9, "hole in primary", fontsize=9, color=INK2, ha="center")

    # (d) Coudé: like Cassegrain, then a flat sends light down the polar axis
    ax = axes[1, 1]
    incoming(ax)
    xc = 7.4
    for y in rays_y:
        xm = mirror_x(y)
        ys = y * (xs - f) / (xm - f)
        ax.plot([xm, xs], [y, ys], color=ORANGE, lw=1.1)
        yc = ys * (1 - (xc - xs) / (10.3 - xs))
        ax.plot([xs, xc], [ys, yc], color=ORANGE, lw=1.1)
        ax.plot([xc, xc], [yc, -2.4], color=ORANGE, lw=1.1)
    ax.plot([xs, xs], [-0.5, 0.5], color=INK, lw=3)
    ax.plot([xc - 0.4, xc + 0.4], [0.4, -0.4], color=INK, lw=3)
    ax.text(xc + 0.4, -2.3, "to fixed spectrograph room", fontsize=9, color=INK2)

    fig.text(0.5, 0.01, "Starlight (blue) enters from the left; the concave primary "
             "mirror (thick black, right) reflects it (orange) to a focus.",
             ha="center", fontsize=9, color=INK2)
    save(fig, "ch01", "fig-telescope-foci")


def light_gathering():
    names = ["Human eye\n(dark adapted)", "Yerkes refractor\n(1897)", "Mt Wilson\nHooker (1917)",
             "Palomar Hale\n(1948)", "Keck\n(1993)", "ELT\n(under construction)"]
    d = np.array([0.007, 1.02, 2.54, 5.08, 10.0, 39.3])  # aperture, m
    gain = (d / d[0]) ** 2
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.barh(range(len(d)), gain, color=BLUE, height=0.55)
    ax.set_xscale("log")
    ax.set_yticks(range(len(d)), names, fontsize=9)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    for i, (g, di) in enumerate(zip(gain, d)):
        ax.text(g * 1.4, i, f"{di:g} m  →  ×{g:,.0f}", va="center", fontsize=9, color=INK)
    ax.set_xlim(0.5, 1e9)
    ax.set_xlabel("Light-gathering power relative to the eye (∝ aperture²)")
    save(fig, "ch01", "fig-light-gathering")


# --------------------------------------------------------------------------
# Chapter 2
# --------------------------------------------------------------------------
def parallax():
    fig, ax = plt.subplots(figsize=(8, 4.4))
    blank(ax)
    sun, star = np.array([0, 0]), np.array([0, 5.2])
    e1, e2 = np.array([-1.6, 0]), np.array([1.6, 0])
    ax.add_patch(Ellipse((0, 0), 3.2, 0.9, fill=False, ec=MUTED, ls="--"))
    ax.add_patch(Circle(sun, 0.18, color=YELLOW))
    ax.text(0, -0.55, "Sun", ha="center", fontsize=9, color=INK2)
    for p, lab in [(e1, "Earth\n(January)"), (e2, "Earth\n(July)")]:
        ax.add_patch(Circle(p, 0.11, color=BLUE))
        ax.text(p[0], -0.95, lab, ha="center", fontsize=9, color=INK2)
    ax.add_patch(Circle(star, 0.12, color=ORANGE))
    ax.text(0.25, 5.25, "nearby star", fontsize=9.5, color=INK)
    for p in (e1, e2):
        ax.plot(*zip(p, star), color=ORANGE, lw=1.3)
        far = star + (star - p) * 0.45
        ax.plot(*zip(star, far), color=ORANGE, lw=0.9, ls=":")
    ax.plot([0, 0], [0, 5.2], color=INK2, lw=0.8, ls="--")
    ax.text(0.1, 2.6, "d", fontsize=12, style="italic")
    ax.plot([0, 1.6], [0.05, 0.05], color=INK, lw=1.6)
    ax.text(0.8, 0.22, "1 AU", ha="center", fontsize=9.5)
    ax.add_patch(Arc(star, 1.4, 1.4, theta1=270, theta2=270 + np.degrees(np.arctan(1.6 / 5.2)),
                     color=INK, lw=1.2))
    ax.text(0.25, 4.15, "p", fontsize=12, style="italic")
    # background sky with apparent positions
    ax.plot([-3.6, 3.6], [7.3, 7.3], color=GRID, lw=6)
    ax.text(3.7, 7.3, "distant background stars", fontsize=9, va="center", color=INK2)
    for x in (-3.2, -1.2, 2.6):
        ax.plot(x, 7.3, "*", color=MUTED, ms=8)
    for p, lab, ha in [(e1, "seen from\nJanuary position", "left"), (e2, "seen from\nJuly position", "right")]:
        x = star[0] + (star[0] - p[0]) * (7.3 - 5.2) / 5.2
        ax.plot(x, 7.3, "o", color=ORANGE, ms=6, mfc=SURFACE, mew=1.5)
        ax.text(x, 7.6, lab, ha=ha, fontsize=8.5, color=INK2)
    ax.set_xlim(-4, 6.2)
    ax.set_ylim(-1.4, 8.5)
    save(fig, "ch02", "fig-parallax")


def planck_lambda(lam_m, T):
    h, c, k = 6.626e-34, 2.998e8, 1.381e-23
    return 2 * h * c ** 2 / lam_m ** 5 / np.expm1(h * c / (lam_m * k * T))


def blackbody_ubv():
    lam = np.linspace(150, 1100, 600)  # nm
    fig, ax = plt.subplots(figsize=(8, 4))
    bands = [("U", 365, 66), ("B", 445, 94), ("V", 551, 88)]
    for name, c, w in bands:
        ax.axvspan(c - w / 2, c + w / 2, color=GRID, alpha=0.8, lw=0)
        ax.text(c, 1.04, name, ha="center", fontsize=11, color=INK, transform=ax.get_xaxis_transform())
    for T, col, lab in [(12000, BLUE, "12 000 K (blue-white, e.g. Vega-like)"),
                        (5800, AQUA, "5 800 K (Sun)"),
                        (3500, ORANGE, "3 500 K (red, e.g. Betelgeuse-like)")]:
        b = planck_lambda(lam * 1e-9, T)
        b = b / planck_lambda(551e-9, T)  # normalise at V so colour = shape
        ax.plot(lam, b, color=col, label=lab)
    ax.set_ylim(0, 3.2)
    ax.set_xlim(150, 1100)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Brightness (normalised at V)")
    ax.legend(loc="upper right", fontsize=9)
    save(fig, "ch02", "fig-blackbody-ubv")


# zero-age main sequence (approximate): mass [Msun], Teff [K], L [Lsun]
MS = np.array([
    (40, 42000, 3e5), (15, 30000, 2e4), (5.9, 15500, 830), (2.9, 9800, 54),
    (1.6, 7300, 6.5), (1.0, 5780, 1.0), (0.79, 5250, 0.4), (0.67, 4400, 0.17),
    (0.47, 3800, 0.06), (0.21, 3200, 0.008),
])


def hr_diagram():
    rng = np.random.default_rng(4)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    order = np.argsort(MS[:, 1])
    logT, logL = np.log10(MS[order, 1]), np.log10(MS[order, 2])
    tt = np.linspace(logT.min(), logT.max(), 200)
    ll = np.interp(tt, logT, logL)
    # scatter of main-sequence stars along the locus
    ts = rng.uniform(logT.min(), logT.max(), 260)
    ls = np.interp(ts, logT, logL) + rng.normal(0, 0.18, ts.size)
    ax.scatter(10 ** ts, 10 ** ls, s=9, color=BLUE, alpha=0.55, lw=0)
    ax.plot(10 ** tt, 10 ** ll, color=BLUE, lw=2, label="main sequence")
    # giants, supergiants, white dwarfs
    gT = rng.uniform(np.log10(3600), np.log10(5400), 60)
    gL = rng.uniform(1.6, 2.9, 60) - (gT - 3.55) * 1.2
    ax.scatter(10 ** gT, 10 ** gL, s=12, color=ORANGE, lw=0, alpha=0.8, label="giants")
    sT = rng.uniform(np.log10(3500), np.log10(25000), 30)
    sL = rng.uniform(4.2, 5.4, 30)
    ax.scatter(10 ** sT, 10 ** sL, s=14, color=VIOLET, lw=0, alpha=0.8, label="supergiants")
    wT = rng.uniform(np.log10(6000), np.log10(30000), 35)
    wL = -4.0 + (wT - 3.78) * 2.2 + rng.normal(0, 0.15, wT.size)
    ax.scatter(10 ** wT, 10 ** wL, s=12, color=AQUA, lw=0, alpha=0.9, label="white dwarfs")
    for m, T, L in MS[[0, 1, 3, 5, 8, 9]]:
        ax.annotate(f"{m:g} M☉", (T, L), (T * 1.18, L * 2.6), fontsize=8.5, color=INK2,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.plot(5780, 1, marker="o", ms=9, mfc=YELLOW, mec=INK, mew=1, zorder=5)
    ax.text(5000, 0.55, "Sun", fontsize=9.5, ha="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(50000, 2600)
    ax.set_ylim(1e-4, 2e6)
    ax.set_xticks([40000, 20000, 10000, 5000, 3000], ["40 000", "20 000", "10 000", "5 000", "3 000"])
    ax.minorticks_off()
    ax.set_xlabel("Surface temperature, Tₑ (K)  —  hotter to the left")
    ax.set_ylabel("Luminosity, L / L☉")
    ax.legend(loc="lower left", fontsize=9, bbox_to_anchor=(0, 0.06))
    save(fig, "ch02", "fig-hr-diagram")


ZAMS_BV = np.array([-0.25, -0.10, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6])
ZAMS_MV = np.array([-2.2, -0.3, 0.8, 2.0, 3.1, 4.4, 5.6, 6.4, 7.3, 8.9, 11.0])


def main_sequence_fitting():
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(7, 5.4))
    bv = np.linspace(-0.2, 1.5, 200)
    mv = np.interp(bv, ZAMS_BV, ZAMS_MV)
    ax.plot(bv, mv, color=BLUE, label="calibrating cluster (absolute magnitude M_V)")
    dm = 9.0
    sb = rng.uniform(0.0, 1.3, 90)
    sm = np.interp(sb, ZAMS_BV, ZAMS_MV) + dm + rng.normal(0, 0.15, sb.size) - rng.exponential(0.12, sb.size)
    ax.scatter(sb, sm, s=12, color=ORANGE, lw=0, label="distant cluster (apparent magnitude m_V)")
    ax.plot(bv, mv + dm, color=ORANGE, lw=1, ls="--")
    x0 = 0.6
    m0 = np.interp(x0, ZAMS_BV, ZAMS_MV)
    arrow(ax, (x0, m0), (x0, m0 + dm), color=INK, lw=1.4)
    ax.text(x0 + 0.04, m0 + dm / 2, "shift = m − M = 9 mag\n⇒ d = 10^(1 + 9/5) pc ≈ 630 pc",
            fontsize=9.5, va="center")
    ax.invert_yaxis()
    ax.set_xlabel("Colour index B − V  (bluer ← → redder)")
    ax.set_ylabel("Magnitude (brighter ↑)")
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "ch02", "fig-main-sequence-fitting")


def moving_cluster():
    fig, ax = plt.subplots(figsize=(8, 5))
    blank(ax)
    obs = np.array([0.0, 0.0])
    cp = np.array([10.0, 2.2])  # direction of the convergent point
    ax.add_patch(Circle(obs, 0.12, color=BLUE))
    ax.text(0, -0.5, "Sun / observer", ha="center", fontsize=9, color=INK2)
    c = np.array([2.6, 3.4])  # cluster centre
    vdir = (cp - obs) / np.linalg.norm(cp - obs)
    for off in [(-0.3, 0.1), (0.25, 0.3), (0.0, -0.3), (0.35, -0.15), (-0.2, 0.45)]:
        s_ = c + np.array(off)
        ax.add_patch(Circle(s_, 0.07, color=ORANGE))
        ax.plot(*zip(s_, cp), color=ORANGE, lw=0.5, ls=":")
    ax.plot(*cp, marker="x", color=INK, ms=9, mew=2)
    ax.text(cp[0], cp[1] - 0.75, "convergent point\n(direction of V)", fontsize=9.5, ha="center")
    ax.plot(*zip(obs, c * 1.75), color=INK2, lw=0.8, ls="--")
    ax.text(*(c * 1.75 + [0.1, 0]), "line of sight", fontsize=8.5, color=INK2)
    ax.plot(*zip(obs, cp), color=INK2, lw=0.8, ls="--")
    V = vdir * 3.2
    los = c / np.linalg.norm(c)
    vr = los * np.dot(V, los)
    arrow(ax, c, c + V, color=INK, lw=1.8)
    arrow(ax, c, c + vr, color=BLUE, lw=1.6)
    arrow(ax, c + vr, c + V, color=AQUA, lw=1.6)
    ax.text(*(c + V + [0.15, -0.1]), "space velocity V", fontsize=9.5)
    ax.text(*(c + vr + [-0.2, 0.25]), "v_r = V cos θ  (Doppler shift)", fontsize=9, ha="right", color=BLUE)
    ax.text(*(c + (vr + V) / 2 + [0.25, 0.1]), "v_t = V sin θ\n(proper motion μ)", fontsize=9, color=AQUA)
    a1 = np.degrees(np.arctan2(cp[1], cp[0]))
    a2 = np.degrees(np.arctan2(c[1], c[0]))
    ax.add_patch(Arc(obs, 2.6, 2.6, theta1=a1, theta2=a2, color=INK, lw=1))
    ax.text(1.45, 0.95, "θ", fontsize=12)
    ax.text(5.6, -0.6, "d = v_r tan θ / (4.74 μ)   [d in pc, v_r in km/s, μ in arcsec/yr]",
            fontsize=9.5, ha="center")
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1.0, 6.4)
    save(fig, "ch02", "fig-moving-cluster")


def cepheid_light_curve():
    P = 5.366  # days, delta Cephei
    t = np.linspace(0, 3 * P, 1200)
    ph = (t / P) % 1
    # asymmetric light curve: fast rise (~25% of cycle), slow decline
    rise = 0.25
    shape = np.where(ph < rise, ph / rise, 1 - (ph - rise) / (1 - rise))
    shape = 0.5 * (1 - np.cos(np.pi * shape))
    mag = 4.37 - (4.37 - 3.48) * shape
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(t, mag, color=BLUE)
    ax.invert_yaxis()
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Apparent magnitude V")
    arrow(ax, (P * 0.25, 3.40), (P * 1.25, 3.40), color=INK2, style="<|-|>", lw=1)
    ax.text(P * 0.75, 3.36, f"period P = {P} days", ha="center", fontsize=9.5)
    ax.set_ylim(4.5, 3.3)
    ax.set_title("δ Cephei: rapid brightening, slow fading", loc="left", fontsize=10.5)
    save(fig, "ch02", "fig-cepheid-light-curve")


def period_luminosity():
    # Benedict et al. 2007 (HST parallaxes): M_V = -2.43 (log P - 1) - 4.05
    rng = np.random.default_rng(3)
    logP = rng.uniform(0.4, 1.8, 70)
    MV = -2.43 * (logP - 1) - 4.05 + rng.normal(0, 0.2, logP.size)
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.scatter(10 ** logP, MV, s=14, color=BLUE, lw=0, alpha=0.7, label="Cepheids (illustrative scatter)")
    x = np.linspace(0.3, 1.9, 50)
    ax.plot(10 ** x, -2.43 * (x - 1) - 4.05, color=ORANGE, label="M_V = −2.43 (log P − 1) − 4.05")
    ax.set_xscale("log")
    ax.set_xticks([2, 5, 10, 20, 50], ["2", "5", "10", "20", "50"])
    ax.minorticks_off()
    ax.invert_yaxis()
    ax.set_xlabel("Pulsation period P (days, log scale)")
    ax.set_ylabel("Absolute magnitude M_V (brighter ↑)")
    sec = ax.secondary_yaxis("right", functions=(lambda m: 10 ** (-0.4 * (m - 4.83)),
                                                  lambda L: 4.83 - 2.5 * np.log10(np.clip(L, 1e-9, None))))
    sec.set_ylabel("Luminosity (L☉)")
    sec.set_yticks([1000, 3000, 10000, 30000], ["1 000", "3 000", "10 000", "30 000"])
    ax.legend(loc="lower right", fontsize=9)
    save(fig, "ch02", "fig-period-luminosity")


def distance_ladder():
    rungs = [  # name, min pc, max pc, colour
        ("Radar ranging (Solar System)", 1e-8, 1e-4, MUTED),
        ("Trigonometric parallax (Gaia)", 1, 1e4, BLUE),
        ("Main-sequence fitting / moving clusters", 40, 6e4, AQUA),
        ("Cepheid variables", 1e3, 4e7, ORANGE),
        ("Type Ia supernovae", 1e6, 5e9, VIOLET),
        ("Hubble's law (redshift)", 1e7, 1.4e10, INK2),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    for i, (name, a, b, col) in enumerate(rungs):
        ax.barh(i, np.log10(b) - np.log10(a), left=np.log10(a), color=col, height=0.55)
        ax.text(np.log10(a) - 0.2, i, name, ha="right", va="center", fontsize=9)
    ax.set_yticks([])
    ax.invert_yaxis()
    ax.set_xlim(-14, 10.5)
    ticks = {-8: "1 AU\n(5×10⁻⁶ pc)", 0: "1 pc", 3: "1 kpc", 6: "1 Mpc", 9: "1 Gpc"}
    ax.set_xticks(list(ticks), list(ticks.values()), fontsize=9)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    for x, lab, ha in [(np.log10(8200), "Galactic centre ", "right"), (np.log10(7.7e5), "Andromeda", "center"),
                       (np.log10(1.65e7), " Virgo cluster", "left")]:
        ax.axvline(x, color=MUTED, lw=0.7, ls="--")
        ax.text(x, -0.9, lab, ha=ha, fontsize=8, color=INK2)
    ax.set_ylim(len(rungs) - 0.4, -1.3)
    ax.set_xlabel("Distance (each rung is calibrated by the one above it)")
    save(fig, "ch02", "fig-distance-ladder")


# --------------------------------------------------------------------------
# Chapter 3
# --------------------------------------------------------------------------
def redshift_spectrum():
    lines = {"Ca H+K": 395.1, "Hβ": 486.1, "Mg": 517.5, "Na D": 589.3, "Hα": 656.3}
    lam = np.linspace(370, 720, 2000)
    cont = 0.6 + 0.4 * np.sin((lam - 370) / 350 * np.pi * 0.9)

    def spectrum(z):
        f = cont.copy()
        for l0 in lines.values():
            f -= 0.45 * np.exp(-0.5 * ((lam - l0 * (1 + z)) / 1.4) ** 2)
        return f

    z = 0.04
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.6), sharex=True)
    for ax, zz, lab, col in [(axes[0], 0, "Laboratory (at rest)", BLUE),
                             (axes[1], z, f"Galaxy, z = {z}  (v ≈ cz ≈ 12 000 km/s)", ORANGE)]:
        ax.plot(lam, spectrum(zz), color=col, lw=1.5)
        ax.set_yticks([])
        ax.set_title(lab, loc="left", fontsize=10)
        ax.grid(False)
        ax.set_ylim(0, 1.15)
    for name, l0 in lines.items():
        axes[0].text(l0, 0.05, name, ha="center", fontsize=8, color=INK2)
        axes[1].annotate("", (l0 * (1 + z), 0.12), (l0, 0.12),
                         arrowprops=dict(arrowstyle="->", color=INK2, lw=0.9))
    axes[1].set_xlabel("Wavelength (nm)   —   every line moves by the same factor (1 + z)")
    save(fig, "ch03", "fig-redshift-spectrum")


def hubbles_law():
    rng = np.random.default_rng(11)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4))
    # Left: Hubble 1929 scale (illustrative, his slope ~500 km/s/Mpc)
    d = rng.uniform(0.05, 2.0, 24)
    v = 500 * d + rng.normal(0, 180, d.size)
    ax = axes[0]
    ax.scatter(d, v, s=22, color=BLUE, lw=0)
    x = np.linspace(0, 2.1, 10)
    ax.plot(x, 500 * x, color=ORANGE, lw=1.6)
    ax.set_title("1929 scale: H₀ ≈ 500 km/s/Mpc", loc="left", fontsize=10)
    ax.set_xlabel("Distance (Mpc)")
    ax.set_ylabel("Recession velocity (km/s)")
    # Right: modern scale
    d = rng.uniform(5, 450, 120)
    v = H0 * d + rng.normal(0, 400, d.size) + rng.normal(0, 0.06, d.size) * H0 * d
    ax = axes[1]
    ax.scatter(d, v, s=12, color=BLUE, lw=0, alpha=0.7)
    x = np.linspace(0, 470, 10)
    ax.plot(x, 70 * x, color=ORANGE, lw=1.6)
    ax.set_title("Today: H₀ ≈ 70 km/s/Mpc", loc="left", fontsize=10)
    ax.set_xlabel("Distance (Mpc)")
    fig.text(0.5, -0.03, "Illustrative points. Hubble's 1929 distances were too small by a "
             "factor of ~7, so his slope was too steep; the straight line is what survived.",
             ha="center", fontsize=9, color=INK2)
    save(fig, "ch03", "fig-hubbles-law")


def expansion_grid():
    rng = np.random.default_rng(5)
    pts = rng.uniform(-1, 1, (28, 2))
    pts[0] = [0.05, -0.05]  # "us"
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    for ax, s, title in [(axes[0], 1.0, "Earlier"), (axes[1], 1.5, "Later: every distance ×1.5")]:
        blank(ax)
        ax.set_xlim(-1.7, 1.7)
        ax.set_ylim(-1.7, 1.7)
        ax.set_title(title, loc="left", fontsize=10.5)
        P = pts * s
        ax.scatter(P[1:, 0], P[1:, 1], s=26, color=BLUE, lw=0)
        ax.scatter(*P[0], s=60, color=ORANGE, zorder=4)
        ax.text(P[0, 0] + 0.07, P[0, 1] - 0.15, "our galaxy", fontsize=9)
    ax = axes[1]
    for p in pts[1:]:
        arrow(ax, p * 1.0 + (pts[0] * 1.5 - pts[0]), p * 1.5, color=AQUA, lw=1, ms=7)
    fig.text(0.5, 0.0, "Seen from our galaxy (arrows), each galaxy has moved by an amount "
             "proportional to its distance — Hubble's law. The same is true from any galaxy.",
             ha="center", fontsize=9, color=INK2)
    save(fig, "ch03", "fig-expansion-grid")


def scale_factor_models():
    """a(t) for three models, all normalised to H0 today."""
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    models = [("Empty (coasting): age = 1/H₀", 0.0, 0.0, MUTED),
              ("Matter only: age = ⅔ × 1/H₀", 1.0, 0.0, ORANGE),
              ("ΛCDM (Planck 2018): age = 13.8 Gyr", OM, OL, BLUE)]
    a = np.linspace(1e-4, 1.6, 400)
    for name, om, ol, col in models:
        def integrand(x):
            ok = 1 - om - ol
            return 1 / (x * np.sqrt(om / x ** 3 + ok / x ** 2 + ol))
        t = np.array([quad(integrand, 1e-8, ai)[0] for ai in a]) * HUBBLE_TIME_GYR
        t0 = quad(integrand, 1e-8, 1)[0] * HUBBLE_TIME_GYR
        ax.plot(t - t0, a, color=col, label=name)
        ax.plot(-t0, 0, marker="o", color=col, ms=6)
    ax.axhline(1, color=MUTED, lw=0.7, ls=":")
    ax.axvline(0, color=MUTED, lw=0.7, ls=":")
    ax.text(0.3, 0.06, "today", fontsize=9, color=INK2)
    ax.set_xlim(-16, 8)
    ax.set_ylim(0, 1.6)
    ax.set_xlabel("Time relative to today (billions of years)")
    ax.set_ylabel("Scale factor a (size relative to today)")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "ch03", "fig-scale-factor-models")


# --------------------------------------------------------------------------
# Chapter 4
# --------------------------------------------------------------------------
def radio_counts():
    logS = np.linspace(-1.5, 2, 200)  # Jy, at 1.4 GHz scale
    # schematic of observed Euclidean-normalised counts: rise to a peak then fall
    obs = 1.0 + 1.3 * np.exp(-0.5 * ((logS - 0.0) / 0.75) ** 2) - 0.6 * (logS < -0.9) * (-0.9 - logS)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(10 ** logS, obs, color=BLUE, label="observed (schematic)")
    ax.axhline(1, color=ORANGE, ls="--", lw=1.6, label="static Euclidean / steady state: flat")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Flux density S (Jy)   —   fainter, hence typically more distant, to the right")
    ax.set_ylabel("Counts ÷ Euclidean expectation")
    ax.text(1, 2.45, "excess of faint sources:\nradio galaxies were more\ncommon in the past",
            fontsize=9, ha="center")
    ax.set_ylim(0, 3.0)
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "ch04", "fig-radio-source-counts")


# --------------------------------------------------------------------------
# Chapter 5
# --------------------------------------------------------------------------
def olbers():
    rng = np.random.default_rng(2)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    ax = axes[0]
    blank(ax)
    ax.set_title("(a) Infinite, static, eternal: every sight-line hits a star",
                 loc="left", fontsize=9.5)
    for r in (1, 2, 3):
        ax.add_patch(Circle((0, 0), r, fill=False, ec=MUTED, lw=0.8, ls="--"))
        n = 6 * r ** 2
        th = rng.uniform(0, 2 * np.pi, n)
        rr = r - rng.uniform(0, 0.25, n)
        ax.scatter(rr * np.cos(th), rr * np.sin(th), s=10, color=YELLOW, lw=0)
    ax.text(0, 3.3, "stars per shell ∝ r²,  light from each ∝ 1/r²\n⇒ every shell adds equal light",
            ha="center", fontsize=8.5, color=INK2)
    ax.plot(0, 0, "o", color=BLUE, ms=6)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 4)

    ax = axes[1]
    blank(ax)
    ax.set_title("(b) Finite age: we only see light that has had time to arrive",
                 loc="left", fontsize=9.5)
    th = rng.uniform(0, 2 * np.pi, 220)
    rr = 3.4 * np.sqrt(rng.uniform(0, 1, 220))
    inside = rr < 2.2
    ax.scatter((rr * np.cos(th))[inside], (rr * np.sin(th))[inside], s=10, color=YELLOW, lw=0)
    ax.scatter((rr * np.cos(th))[~inside], (rr * np.sin(th))[~inside], s=10, color=GRID, lw=0)
    ax.add_patch(Circle((0, 0), 2.2, fill=False, ec=ORANGE, lw=1.8))
    ax.text(0, -2.75, "horizon: distance light travels\nin the age of the Universe",
            ha="center", fontsize=8.5, color=INK)
    ax.text(2.5, 2.5, "light not yet\narrived", fontsize=8.5, color=INK2, ha="center")
    ax.plot(0, 0, "o", color=BLUE, ms=6)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 4)
    save(fig, "ch05", "fig-olbers")


# --------------------------------------------------------------------------
# Chapters 6 and 7
# --------------------------------------------------------------------------
def cmb_timeline():
    events = [
        (1927, "Lemaître: expanding\nuniverse from a\n'primeval atom'"),
        (1929, "Hubble's law"),
        (1948, "Alpher & Herman\npredict ≈5 K\nbackground"),
        (1948.6, "Bondi, Gold, Hoyle:\nsteady state"),
        (1964, "Dicke, Peebles et al.\nbuild a radiometer"),
        (1965, "Penzias & Wilson\ndetect 3.5 K excess"),
        (1978, "Nobel Prize to\nPenzias & Wilson"),
        (1990, "COBE FIRAS: perfect\nblackbody, 2.735 K"),
        (1992, "COBE DMR:\nanisotropies"),
    ]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_axis_off()
    ax.axhline(0, color=MUTED, lw=1.2)
    for i, (yr, text) in enumerate(events):
        up = 1 if i % 2 == 0 else -1
        col = ORANGE if yr in (1948, 1965) else BLUE
        ax.plot([yr, yr], [0, 0.55 * up], color=col, lw=1)
        ax.plot(yr, 0, "o", color=col, ms=6)
        ax.text(yr, 0.6 * up, f"{int(yr)}\n{text}" if up > 0 else f"{text}\n{int(yr)}",
                ha="center", va="bottom" if up > 0 else "top", fontsize=8.2)
    ax.set_xlim(1920, 1997)
    ax.set_ylim(-1.9, 1.9)
    save(fig, "ch06", "fig-cmb-timeline")


def planck_nu(nu_hz, T):
    h, c, k = 6.626e-34, 2.998e8, 1.381e-23
    return 2 * h * nu_hz ** 3 / c ** 2 / np.expm1(h * nu_hz / (k * T))


def cmb_spectrum():
    nu = np.linspace(1, 700, 800) * 1e9
    I = planck_nu(nu, T_CMB) * 1e20  # MJy/sr
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.plot(nu / 1e9, I, color=BLUE, label=f"blackbody, T = {T_CMB} K")
    nf = np.linspace(68, 640, 43) * 1e9
    ax.errorbar(nf / 1e9, planck_nu(nf, T_CMB) * 1e20, yerr=planck_nu(nf, T_CMB) * 1e20 * 0.02,
                fmt="o", ms=3.5, color=ORANGE, elinewidth=1,
                label="COBE FIRAS frequencies (errors ×400 to be visible)")
    pw = 4.08e9
    ax.plot(pw / 1e9, planck_nu(pw, T_CMB) * 1e20, marker="D", color=INK, ms=7, ls="none",
            label="Penzias & Wilson 1965 (λ = 7.35 cm)")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Intensity (MJy/sr)")
    ax.text(175, 395, "peak ≈ 160 GHz (λ ≈ 1.9 mm)", fontsize=9)
    ax.set_ylim(0, 440)
    ax.legend(loc="center right", fontsize=8.8)
    save(fig, "ch07", "fig-cmb-spectrum")


# --------------------------------------------------------------------------
# Chapter 8
# --------------------------------------------------------------------------
def density_evolution():
    rho_c = 1.878e-26 * (H0 / 100) ** 2  # kg/m^3
    zp1 = np.logspace(-0.3, 10, 400)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.plot(zp1, OR * rho_c * zp1 ** 4, color=ORANGE, label="radiation  ∝ (1+z)⁴")
    ax.plot(zp1, OM * rho_c * zp1 ** 3, color=BLUE, label="matter  ∝ (1+z)³")
    ax.plot(zp1, OL * rho_c * np.ones_like(zp1), color=AQUA, label="dark energy  = constant")
    z_eq = OM / OR
    ax.axvline(z_eq, color=MUTED, lw=0.8, ls="--")
    ax.text(z_eq * 1.3, 1e-27, f"matter–radiation\nequality\n1+z ≈ {z_eq:,.0f}", fontsize=8.8)
    z_l = (OL / OM) ** (1 / 3)
    ax.axvline(z_l, color=MUTED, lw=0.8, ls="--")
    ax.text(z_l * 1.3, 1e-10, "dark energy\ntakes over\n(z ≈ 0.3)", fontsize=8.8)
    ax.axvline(1100, color=MUTED, lw=0.6, ls=":")
    ax.text(1100 / 1.3, 1e-25, "CMB\nreleased", fontsize=8, color=INK2, ha="right")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.5, 1e10)
    ax.set_ylim(1e-28, 1e16)
    ax.set_xlabel("1 + z   (the Universe was 1+z times smaller)  →  earlier")
    ax.set_ylabel("Mass-energy density (kg/m³)")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "ch08", "fig-density-evolution")


def temperature_history():
    z = np.logspace(-3, 10, 500)

    def age(zz):
        a = 1 / (1 + zz)
        f = lambda x: 1 / np.sqrt(OR / x ** 2 + OM / x + OL * x ** 2)
        # split the integral so the tiny-a radiation era is resolved
        return sum(quad(f, lo, hi, limit=200)[0] for lo, hi in
                   [(0, min(a, 1e-6)), (min(a, 1e-6), min(a, 1e-3)), (min(a, 1e-3), a)]) / H0_SI

    t = np.array([age(zz) for zz in z])  # seconds
    T = T_CMB * (1 + z)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(t, T, color=ORANGE)
    yr = 3.156e7
    marks = [
        (age(3.7e8), "nucleosynthesis\n(≈ 3 minutes, 10⁹ K)"),
        (age(1090), "CMB released\n(380 000 yr, 3 000 K)"),
        (age(10), "first galaxies\n(≈ 0.5 Gyr)"),
        (age(0), "today\n(13.8 Gyr, 2.73 K)"),
    ]
    for tm, lab in marks:
        Tm = np.interp(tm, t[::-1], T[::-1])
        ax.plot(tm, Tm, "o", color=BLUE, ms=7, zorder=4)
        ax.annotate(lab, (tm, Tm), (tm * 2.5, Tm * 4), fontsize=8.8,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Time since the Big Bang (seconds)")
    ax.set_ylabel("Temperature of the radiation (K)")
    sec = ax.secondary_xaxis("top", functions=(lambda s: s / yr, lambda y: y * yr))
    sec.set_xlabel("years")
    ax.set_xlim(1, 3e18)
    ax.set_ylim(1, 3e10)
    save(fig, "ch08", "fig-temperature-history")


# --------------------------------------------------------------------------
# Chapter 9
# --------------------------------------------------------------------------
def neutron_proton():
    Q = 1.293  # MeV
    tau = 879.4  # s
    t = np.logspace(-2, np.log10(400), 500)
    kT = np.sqrt(1.32 / t)  # MeV, radiation era (after e+e- annihilation; adequate here)
    eq = np.exp(-Q / kT)
    kT_f = 0.8
    t_f = 1.32 / kT_f ** 2
    X_f = np.exp(-Q / kT_f) / (1 + np.exp(-Q / kT_f))
    Xn = np.where(t < t_f, eq / (1 + eq), X_f * np.exp(-(t - t_f) / tau))
    np_ratio = Xn / (1 - Xn)
    t_d = 200
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    ax.plot(t, eq, color=MUTED, ls="--", lw=1.4, label="if equilibrium continued: e^(−Δmc²/kT)")
    ax.plot(t, np_ratio, color=BLUE, label="simplified history of n/p")
    ax.axvline(t_f, color=MUTED, lw=0.8, ls=":")
    ax.text(t_f * 1.15, 0.6, f"weak reactions\nfreeze out\n(kT ≈ 0.8 MeV, ≈ 2 s)\nn/p ≈ 1/5", fontsize=8.8)
    ax.axvline(t_d, color=ORANGE, lw=1.2)
    nd = np.interp(t_d, t, np_ratio)
    ax.text(t_d * 0.92, 0.6, f"deuterium\nsurvives\n(≈ 200 s)\nn/p ≈ 1/{1 / nd:.1f}",
            fontsize=8.8, ha="right")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.02, 1.2)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Neutrons per proton, n/p")
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "ch09", "fig-neutron-proton")


def bbn_chain():
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    blank(ax)
    nodes = {"p + n": (0, 0), "²H\n(deuterium)": (2.6, 0), "³He": (5.2, 0.9),
             "³H": (5.2, -0.9), "⁴He": (7.8, 0), "⁷Li (trace)": (10.4, 0)}
    for name, (x, y) in nodes.items():
        col = ORANGE if name == "⁴He" else BLUE
        ax.add_patch(FancyBboxPatch((x - 0.85, y - 0.38), 1.7, 0.76,
                                    boxstyle="round,pad=0.05,rounding_size=0.15",
                                    fc=SURFACE, ec=col, lw=1.6))
        ax.text(x, y, name, ha="center", va="center", fontsize=9.5)
    edges = [("p + n", "²H\n(deuterium)", "+γ"), ("²H\n(deuterium)", "³He", "+p"),
             ("²H\n(deuterium)", "³H", "+n"), ("³He", "⁴He", "+n"), ("³H", "⁴He", "+p"),
             ("⁴He", "⁷Li (trace)", "+³H")]
    for a, b, lab in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        arrow(ax, (x1 + 0.9, y1), (x2 - 0.9, y2), color=INK2, lw=1.2)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.18, lab, ha="center", fontsize=8.5, color=INK2)
    ax.text(7.8, -0.75, "≈ 25% of the mass", ha="center", fontsize=8.5, color=INK)
    ax.set_xlim(-1, 11.4)
    ax.set_ylim(-1.5, 1.5)
    save(fig, "ch09", "fig-bbn-chain")


# --------------------------------------------------------------------------
# Chapter 11 (new): since 1998
# --------------------------------------------------------------------------
def supernova_hubble():
    z = np.linspace(0.01, 1.5, 200)
    c = 2.998e5

    def dl(zz, om, ol):
        ok = 1 - om - ol
        chi = quad(lambda x: 1 / np.sqrt(om * (1 + x) ** 3 + ok * (1 + x) ** 2 + ol), 0, zz)[0]
        if abs(ok) < 1e-6:
            s = chi
        elif ok > 0:
            s = np.sinh(np.sqrt(ok) * chi) / np.sqrt(ok)
        else:
            s = np.sin(np.sqrt(-ok) * chi) / np.sqrt(-ok)
        return (1 + zz) * s * c / 70

    def mu(om, ol):
        return np.array([5 * np.log10(dl(zz, om, ol) * 1e6 / 10) for zz in z])

    ref = mu(0, 0)
    i5 = np.argmin(abs(z - 0.5))
    gap = (mu(OM, OL) - mu(1, 0))[i5]
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    for name, om, ol, col in [("Accelerating: 31% matter + 69% dark energy", OM, OL, BLUE),
                              ("Empty, coasting universe (reference)", 0, 0, MUTED),
                              ("Decelerating: matter only (the 1998 expectation)", 1, 0, ORANGE)]:
        ax.plot(z, mu(om, ol) - ref, color=col, label=name)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("Redshift z")
    ax.set_ylabel("Δ magnitude vs empty universe\n(positive = fainter, farther)")
    ax.annotate("", (0.5, (mu(OM, OL) - ref)[i5]), (0.5, (mu(1, 0) - ref)[i5]),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1))
    ax.text(0.53, -0.12, f"at z = 0.5, supernovae look {gap:.2f} mag\n"
            f"({10 ** (0.4 * gap) - 1:.0%}) fainter than a\nmatter-only universe predicts",
            fontsize=9)
    ax.legend(loc="lower left", fontsize=9)
    save(fig, "ch11", "fig-supernova-acceleration")


def hubble_tension():
    data = [  # label, value, -err, +err
        ("Planck CMB + ΛCDM (2018)", 67.4, 0.5, 0.5),
        ("TRGB distance ladder (Freedman 2021)", 69.8, 1.7, 1.7),
        ("Gravitational-wave siren GW170817 (2017)", 70.0, 8.0, 12.0),
        ("Lensed quasar time delays (H0LiCOW 2020)", 73.3, 1.8, 1.7),
        ("Cepheid + SN Ia ladder (SH0ES 2022)", 73.0, 1.0, 1.0),
    ]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, (lab, v, lo, hi) in enumerate(data):
        col = BLUE if "Planck" in lab else (ORANGE if "SH0ES" in lab else INK2)
        ax.errorbar(v, i, xerr=[[lo], [hi]], fmt="o", ms=8, color=col, elinewidth=2, capsize=0)
        ax.text(v, i - 0.3, f"{v:.1f}", ha="center", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(data)), [d[0] for d in data], fontsize=9)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlim(60, 84)
    ax.set_xlabel("Hubble constant H₀ (km/s/Mpc)  —  horizontal bars are 1σ uncertainties")
    save(fig, "ch11", "fig-hubble-tension")


def cosmic_budget():
    parts = [("Dark energy", 68.5, BLUE), ("Dark matter", 26.6, ORANGE), ("Ordinary matter", 4.9, AQUA)]
    fig, ax = plt.subplots(figsize=(8.5, 1.9))
    left = 0
    for name, v, col in parts:
        ax.barh(0, v, left=left, color=col, height=0.6, edgecolor=SURFACE, linewidth=2)
        if v > 10:
            ax.text(left + v / 2, 0, f"{name}\n{v:g}%", ha="center", va="center", fontsize=9.5,
                    color="white")
        left += v
    ax.annotate("Ordinary matter\n4.9%", (97.6, 0.3), (88, 0.9), fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 1.4)
    ax.set_axis_off()
    save(fig, "ch11", "fig-cosmic-budget")


def cosmic_timeline():
    yr = 3.156e7
    events = [  # time, label, stem height (sign = side)
        (1e-32, "inflation\n(proposed 1980)", 0.5),
        (1e-6, "protons and\nneutrons form", -0.5),
        (180, "nucleosynthesis\n(3 minutes)", 0.5),
        (5e4 * yr, "matter–radiation\nequality (50 000 yr)", -1.0),
        (3.8e5 * yr, "CMB released\n(380 000 yr)", 0.5),
        (2e8 * yr, "first stars\n(~200 Myr)", -0.45),
        (13.8e9 * yr, "today\n(13.8 Gyr)", 1.05),
    ]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.set_axis_off()
    x = np.log10([e[0] for e in events])
    ax.plot([x.min() - 1, x.max() + 0.5], [0, 0], color=MUTED, lw=1.2)
    for (t, lab, h), xi in zip(events, x):
        ax.plot([xi, xi], [0, h], color=BLUE, lw=1)
        ax.plot(xi, 0, "o", color=ORANGE if lab.startswith("today") else BLUE, ms=6)
        ax.text(xi, h + 0.06 * np.sign(h), lab, ha="center", va="bottom" if h > 0 else "top", fontsize=8.5)
    for p, lab in [(-30, "10⁻³⁰ s"), (-20, "10⁻²⁰ s"), (-10, "10⁻¹⁰ s"), (0, "1 s"),
                   (np.log10(yr), "1 yr"), (np.log10(1e6 * yr), "1 Myr"), (np.log10(1e9 * yr), "1 Gyr")]:
        ax.text(p, -0.12, lab, ha="center", va="top", fontsize=7.5, color=INK2)
        ax.plot([p, p], [-0.04, 0.04], color=MUTED, lw=1)
    ax.set_xlim(-34, 19.5)
    ax.set_ylim(-1.7, 1.75)
    ax.text(-34, 1.55, "Time since the Big Bang (logarithmic scale)", fontsize=9, color=INK2)
    save(fig, "ch11", "fig-cosmic-timeline")


if __name__ == "__main__":
    for fn in [telescope_foci, light_gathering, parallax, blackbody_ubv, hr_diagram,
               main_sequence_fitting, moving_cluster, cepheid_light_curve, period_luminosity,
               distance_ladder, redshift_spectrum, hubbles_law, expansion_grid,
               scale_factor_models, radio_counts, olbers, cmb_timeline, cmb_spectrum,
               density_evolution, temperature_history, neutron_proton, bbn_chain,
               supernova_hubble, hubble_tension, cosmic_budget, cosmic_timeline]:
        fn()
