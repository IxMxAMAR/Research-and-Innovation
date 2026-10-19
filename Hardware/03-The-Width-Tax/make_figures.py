"""Figures for 'The Width Tax' — PCIe lane-scaling analysis paper."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Georgia", "DejaVu Serif"],
    "font.size": 9,
    "axes.edgecolor": "#3a3a3a",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#dcdcdc",
    "grid.linewidth": 0.55,
    "grid.alpha": 1.0,
    "figure.dpi": 160,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "svg.fonttype": "path",
    "pdf.fonttype": 42,
})

NAVY = "#1f3a5f"
TEAL = "#2a7f7f"
AMBER = "#c8862a"
GRAY = "#6b7280"
RED = "#a63d40"

def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), transparent=False,
                    facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- Figure 1
N = np.array([1, 2, 4, 8, 16, 32, 64])
per_lane = [("Gen5 (32 GT/s)", 3.94, GRAY),
            ("Gen6 (64 GT/s PAM4)", 7.56, TEAL),
            ("Gen7 (128 GT/s PAM4)", 15.1, NAVY)]

fig, ax = plt.subplots(figsize=(6.6, 3.0))
for label, p, c in per_lane:
    ax.loglog(N, N * p, marker="o", ms=3.5, lw=2.0, color=c, label=label)
ax.axvline(16, color=RED, ls=":", lw=1.0)
ax.text(16 * 1.08, 2.2, "x16 CEM limit", color=RED, fontsize=7.6, rotation=90,
        va="bottom")
ax.set_xlabel("Lanes")
ax.set_ylabel("Bandwidth, one direction (GB/s)")
ax.set_xlim(1, 64)
ax.set_ylim(1, 2000)
ax.set_xticks(N, [str(n) for n in N])
ax.legend(frameon=False, fontsize=7.8, loc="upper left")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig1_bandwidth")

# ---------------------------------------------------------------- Figure 2
categories = ["Data pins", "Package bumps", "Connector pins",
              "SerDes power", "Retimers", "PCB layers", "Local thermal"]
x16 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
x32 = [2.0, 2.0, 2.0, 2.0, 3.0, 1.4, 2.0]
x64 = [4.0, 4.0, 4.0, 4.0, 6.0, 1.9, 4.0]

fig, ax = plt.subplots(figsize=(6.6, 3.0))
x = np.arange(len(categories))
w = 0.26
ax.bar(x - w, x16, w, color=GRAY, label="x16", zorder=3)
ax.bar(x, x32, w, color=TEAL, label="x32", zorder=3)
ax.bar(x + w, x64, w, color=NAVY, label="x64", zorder=3)
ax.set_xticks(x, categories, fontsize=7.8)
ax.set_ylabel("Cost relative to x16")
ax.set_ylim(0, 6.8)
ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
ax.grid(axis="x", visible=False)
save(fig, "fig2_width_tax")

# ---------------------------------------------------------------- Figure 3
f = np.logspace(np.log10(4), np.log10(128), 300)
def reach(f, k):
    return k / (f ** 1.2)

fig, ax = plt.subplots(figsize=(6.6, 3.0))
ax.loglog(f, reach(f, 10.0), color=GRAY, lw=2.0, label="NRZ")
ax.loglog(f, reach(f, 5.0), color=TEAL, lw=2.0, label="PAM4")
ax.loglog(f, reach(f, 2.5), color=NAVY, lw=2.0, label="PAM8")

for xv, label in [(8, "Gen3"), (32, "Gen5"), (64, "Gen6")]:
    ax.axvline(xv, color=RED, ls=":", lw=0.8)
    ax.text(xv * 1.05, 0.012, label, color=RED, fontsize=7.2, rotation=90)

ax.set_xlabel("Per-lane rate (GBd)")
ax.set_ylabel("Reach (m)")
ax.set_xlim(4, 128)
ax.set_ylim(0.01, 2.0)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig3_reach")

# ---------------------------------------------------------------- Figure 4
N = np.array([1, 2, 4, 8, 16, 32])
link = N * 3.94
lat = 256 * 64 / 1e3  # 256 tags * 64 B / 1 us, in GB/s
cache = np.minimum(link, lat)

fig, ax = plt.subplots(figsize=(6.6, 3.0))
ax.plot(N, link, marker="o", ms=4, lw=2.0, color=NAVY,
        label="Bandwidth-bound (4 KB)")
ax.plot(N, cache, marker="s", ms=4, lw=2.0, color=TEAL,
        label="Latency-bound (64 B, 256 tags)")
ax.axhline(lat, color=RED, ls="--", lw=1.0)
ax.text(1.1, lat * 1.06, f"latency bound {lat:.1f} GB/s", color=RED, fontsize=7.6)
ax.set_xscale("log", base=2)
ax.set_xticks(N, [str(n) for n in N])
ax.set_xlabel("Link width (lanes)")
ax.set_ylabel("Effective bandwidth (GB/s)")
ax.set_ylim(0, 140)
ax.legend(frameon=False, fontsize=7.8, loc="upper left")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig4_width_effect")

# ---------------------------------------------------------------- Figure 5
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ax.set_xscale("log")
ax.set_yscale("log")
ax.axvspan(1e-3, 1e-2, color=TEAL, alpha=0.10)
ax.axvspan(1e-2, 10, color=NAVY, alpha=0.07)
ax.axvspan(10, 1e3, color=AMBER, alpha=0.10)

tech = [
    ("HBM", 0.005, 1024),
    ("UCIe", 0.001, 64),
    ("PCIe x16", 0.3, 16),
    ("NVLink", 1.0, 32),
    ("Ethernet", 100, 4),
    ("CXL/ETH", 1000, 1),
    ("60 GHz", 5, 1),
]
for name, xv, yv in tech:
    ax.scatter(xv, yv, s=28, color=RED, zorder=5)
    ax.annotate(name, (xv, yv), textcoords="offset points", xytext=(5, 4),
                fontsize=7.4)

ax.text(0.0016, 300, "parallel bus", fontsize=7.6, color=TEAL)
ax.text(0.08, 3.0, "PCIe lanes", fontsize=7.6, color=NAVY)
ax.text(30, 40, "optics / network", fontsize=7.6, color=AMBER)

ax.set_xlim(1e-3, 1e3)
ax.set_ylim(1, 2048)
ax.set_xlabel("Reach (m)")
ax.set_ylabel("Lane count")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig5_frontier")

print("figures written to", OUT)
