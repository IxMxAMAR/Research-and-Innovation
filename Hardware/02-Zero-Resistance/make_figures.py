"""Figures for 'Zero Resistance, Zero Speedup' — superconducting interconnect position paper."""
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

E0 = 0.3          # pJ/bit, fixed interface energy
A_CU = 2.0        # pJ/bit/m, copper wire loss
A_SC = 0.01       # pJ/bit/m, superconducting wire loss
L = np.logspace(-2, 2, 400)

def e_cu(L):
    return E0 + A_CU * L

def e_sc(L, eta):
    return (1.0 + eta) * (E0 + A_SC * L)

# ---------------------------------------------------------------- Figure 1
fig, ax = plt.subplots(figsize=(6.6, 3.0))
ax.loglog(L, e_cu(L), color=GRAY, lw=2.0, label="Copper, 300 K")
ax.loglog(L, e_sc(L, 20), color=TEAL, lw=2.0, label="Superconductor, 77 K")
ax.loglog(L, e_sc(L, 300), color=RED, lw=2.0, label="Superconductor, 4 K")
ax.loglog(L, e_sc(L, 0), color=NAVY, lw=2.0, ls="--", label="RTSC, 300 K")

# crossover at 77 K
eta77 = 20.0
Lstar = eta77 * E0 / (A_CU - (1 + eta77) * A_SC)
ax.plot([Lstar], [e_cu(Lstar)], "o", color=TEAL, ms=4, zorder=5)
ax.annotate(f"crossover {Lstar:.1f} m", xy=(Lstar, e_cu(Lstar)),
            xytext=(Lstar * 1.6, e_cu(Lstar) * 0.35),
            fontsize=7.6, color=TEAL,
            arrowprops=dict(arrowstyle="-", color=TEAL, lw=0.7))

ax.set_xlabel("Link length (m)")
ax.set_ylabel("Energy per bit (pJ)")
ax.set_xlim(0.01, 100)
ax.set_ylim(0.1, 1000)
ax.legend(frameon=False, fontsize=7.8, loc="upper left")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig1_energy_length")

# ---------------------------------------------------------------- Figure 2
labels = ["Protocol (PCIe RTT)", "SerDes / PHY", "Driver + receiver",
          "Wire, copper (1 m)", "Wire, SC (1 m)"]
vals = [500.0, 0.2, 0.04, 6.7, 11.1]
colors = [NAVY, GRAY, GRAY, AMBER, TEAL]

fig, ax = plt.subplots(figsize=(6.6, 2.5))
y = np.arange(len(labels))
ax.barh(y, vals, color=colors, height=0.55, zorder=3)
ax.set_xscale("log")
ax.set_xlim(0.01, 1500)
ax.set_yticks(y, labels)
ax.invert_yaxis()
ax.set_xlabel("Latency (ns, log scale)")
for yi, v in zip(y, vals):
    ax.text(v * 1.25, yi, f"{v:g} ns", va="center", fontsize=8)
ax.grid(axis="y", visible=False)
save(fig, "fig2_latency")

# ---------------------------------------------------------------- Figure 3
eta = np.logspace(-1, 3, 700)

fig, ax = plt.subplots(figsize=(6.6, 3.0))
for a, c in [(0.01, NAVY), (0.05, TEAL), (0.1, AMBER)]:
    denom = A_CU - (1 + eta) * a
    Lstar = np.where(denom > 0, eta * E0 / denom, np.nan)
    ax.loglog(eta, Lstar, color=c, lw=2.0,
              label=rf"$\alpha_{{sc}}$ = {a:g} pJ/bit/m")

ax.axvline(20, color=GRAY, ls=":", lw=1.0)
ax.axvline(300, color=RED, ls=":", lw=1.0)
ax.text(20, 2e-3, "77 K", color=GRAY, fontsize=7.6, ha="center")
ax.text(300, 2e-3, "4 K", color=RED, fontsize=7.6, ha="center")

ax.set_xlabel(r"Cryogenic overhead $\eta$ (W/W)")
ax.set_ylabel(r"Crossover length $L^*$ (m)")
ax.set_xlim(0.1, 1000)
ax.set_ylim(1e-3, 1e4)
ax.legend(frameon=False, fontsize=7.6, loc="upper left")
ax.grid(True, which="both", alpha=0.35)
save(fig, "fig3_crossover")

# ---------------------------------------------------------------- Figure 4
lengths = [0.1, 1.0]
cu = [[150.0, A_CU * Lm * 1000.0, 150.0, 100.0] for Lm in lengths]
sc = [[150.0, A_SC * Lm * 1000.0, 150.0, 100.0] for Lm in lengths]

fig, ax = plt.subplots(figsize=(6.6, 3.0))
xpos = [0, 1, 2.6, 3.6]
names = ["Copper\n0.1 m", "RTSC\n0.1 m", "Copper\n1 m", "RTSC\n1 m"]
data = [cu[0], sc[0], cu[1], sc[1]]
comp_colors = [NAVY, AMBER, TEAL, GRAY]
comp_names = ["Driver", "Wire", "Receiver", "Clocking"]

for i, (x, vals) in enumerate(zip(xpos, data)):
    bottom = 0.0
    for j, (v, c) in enumerate(zip(vals, comp_colors)):
        ax.bar(x, v, bottom=bottom, width=0.72, color=c, zorder=3,
               label=comp_names[j] if i == 0 else None)
        bottom += v
    ax.text(x, bottom + 30, f"{bottom:.0f} fJ", ha="center", va="bottom",
            fontsize=7.8, fontweight="bold")

ax.set_xticks(xpos, names)
ax.set_ylabel("Energy per bit (fJ)")
ax.set_ylim(0, 2800)
ax.grid(axis="x", visible=False)
ax.legend(frameon=False, fontsize=7.6, loc="upper left", ncol=2)
save(fig, "fig4_energy_breakdown")

print("figures written to", OUT)
