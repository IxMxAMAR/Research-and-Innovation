"""Figures for 'The x16 Ceiling' — PCIe memory-bandwidth constraint paper."""
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
gens = ["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0"]
per_lane = [0.25, 0.50, 0.985, 1.969, 3.938, 7.56, 15.1]
x16 = [4, 8, 15.75, 31.5, 63, 121, 242]

fig, ax = plt.subplots(figsize=(6.6, 2.9))
x = np.arange(len(gens))
w = 0.38
b1 = ax.bar(x - w/2, [v - 0.15 for v in per_lane], w, bottom=0.15, color=TEAL, label="Per lane", zorder=3)
b2 = ax.bar(x + w/2, [v - 0.15 for v in x16], w, bottom=0.15, color=NAVY, label="x16 link", zorder=3)
ax.set_yscale("log")
ax.set_ylim(0.15, 600)
ax.set_xticks(x, gens)
ax.set_xlabel("PCIe generation")
ax.set_ylabel("GB/s, one direction (log)")
for xi, v in zip(x + w/2, x16):
    ax.text(xi, v * 1.18, f"{v:g}", ha="center", va="bottom", fontsize=7.6,
            color=NAVY, fontweight="bold")
ax.legend(frameon=False, loc="upper left", fontsize=8)
ax.grid(axis="x", visible=False)
save(fig, "fig1_link_scaling")

# ---------------------------------------------------------------- Figure 2
payload = np.array([64, 128, 256, 512, 1024, 2048, 4096])
fig, ax = plt.subplots(figsize=(6.0, 2.7))
for H, color, ls, lab in [(16, TEAL, "-", "H = 16 B (header only)"),
                          (24, NAVY, "-", "H = 24 B (TLP + link)"),
                          (32, AMBER, "--", "H = 32 B (TLP + link + ECRC)")]:
    eff = payload / (payload + H) * 100
    ax.plot(payload, eff, ls, color=color, lw=1.8, label=lab, zorder=3)
for p, y in [(64, 64/(64+24)*100), (256, 256/(256+24)*100), (4096, 4096/(4096+24)*100)]:
    ax.plot([p], [y], "o", ms=4, color=RED, zorder=4)
    ax.annotate(f"{p} B: {y:.0f}%", (p, y), textcoords="offset points",
                xytext=(6, -12), fontsize=7.6, color=RED)
ax.set_xscale("log", base=2)
ax.set_xlim(56, 4700)
ax.set_ylim(55, 101)
ax.set_xticks([64, 128, 256, 512, 1024, 2048, 4096],
              ["64", "128", "256", "512", "1K", "2K", "4K"])
ax.set_xlabel("TLP payload (bytes)")
ax.set_ylabel("Protocol efficiency (%)")
ax.legend(frameon=False, loc="lower right", fontsize=7.6)
save(fig, "fig2_efficiency")

# ---------------------------------------------------------------- Figure 3
N = np.logspace(0, 4, 400)
P = 64.0
fig, ax = plt.subplots(figsize=(6.6, 3.0))
for rtt, color, lab in [(0.5, TEAL, "RTT = 0.5 µs"),
                        (1.0, NAVY, "RTT = 1 µs"),
                        (2.0, AMBER, "RTT = 2 µs")]:
    B = N * P / (rtt * 1e-6) / 1e9
    ax.plot(N, B, color=color, lw=1.9, label=lab, zorder=3)
for b, lab, color in [(31.5, "Gen4 x16", GRAY), (63, "Gen5 x16", GRAY),
                      (121, "Gen6 x16", GRAY)]:
    ax.axhline(b, color=color, ls=(0, (4, 3)), lw=1.0, zorder=2)
    ax.text(1.05, b + 2.5, lab, fontsize=7.2, color=GRAY, va="bottom")
ax.axvline(32, color=RED, ls=":", lw=1.2, zorder=2)
ax.axvline(256, color=RED, ls=":", lw=1.2, zorder=2)
ax.text(32, 8, "32 tags\n(default)", rotation=90, fontsize=7, color=RED,
        ha="right", va="bottom")
ax.text(256, 8, "256 tags\n(extended)", rotation=90, fontsize=7, color=RED,
        ha="right", va="bottom")
ax.plot([886], [63], "o", ms=4.5, color=RED, zorder=5)
ax.annotate("N ≈ 886 to reach\nGen5 x16 at 1 µs", (886, 63),
            textcoords="offset points", xytext=(-118, 12), fontsize=7.6,
            color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
ax.set_xscale("log")
ax.set_xlim(1, 10000)
ax.set_ylim(0, 132)
ax.set_xlabel("Outstanding requests, N (log)")
ax.set_ylabel("Effective bandwidth (GB/s)")
ax.legend(frameon=False, loc="upper left", fontsize=7.8)
ax.grid(axis="x", which="minor", visible=False)
save(fig, "fig3_latency_bound")

# ---------------------------------------------------------------- Figure 4
labels = ["PCIe 3.0", "PCIe 4.0", "PCIe 5.0", "PCIe 6.0", "PCIe 7.0",
          "HBM2E", "HBM3", "HBM3E"]
vals = [0.246, 0.492, 0.985, 1.89, 3.78, 0.45, 0.80, 1.20]
colors = [NAVY]*5 + [TEAL]*3
fig, ax = plt.subplots(figsize=(6.2, 2.8))
y = np.arange(len(labels))[::-1]
ax.barh(y, vals, color=colors, height=0.62, zorder=3)
for yi, v in zip(y, vals):
    ax.text(v + 0.06, yi, f"{v:.2f}", va="center", fontsize=7.6, color="#222")
ax.set_yticks(y, labels)
ax.set_xlim(0, 4.35)
ax.set_xlabel("One-directional bandwidth per signal pin (GB/s)")
ax.axvline(1.20, color=RED, ls="--", lw=1.0, zorder=2)
ax.text(1.26, 0.35, "HBM3E", fontsize=7.4, color=RED)
ax.grid(axis="y", visible=False)
save(fig, "fig4_per_pin")

print("figures written to", OUT)
