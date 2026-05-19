"""Famine analysis plots — 02, 05, 06, 07.

Mirrors the earthquake project's analytical conventions:
- Hard-coded catalog regimes (WPF coverage: 1870+, ≥100k deaths)
- Pre-1870 entries excluded from trend fits and statistical claims
- Inter-event interval and cumulative-vs-reference for rare events
- Log-aware aggregation for power-law tails
"""

from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = Path(__file__).parent
PLOTS = HERE / "plots"
PLOTS.mkdir(exist_ok=True)

CATALOG_START = 1870
GREAT_FAMINE_THRESHOLD = 1_000_000
PARTIAL_DECADE_START = 2020

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})


def load_events() -> pd.DataFrame:
    df = pd.read_csv(HERE / "famines-and-deaths.csv")
    df = df.rename(columns={"wpf_authoritative_mortality_estimate": "deaths"})
    df["decade"] = (df["year"] // 10) * 10
    span = df["entity"].str.extract(r"(\d{4})(?:-(\d{4}|\d{2}))?")
    df["year_start"] = span[0].astype(int)
    end_raw = span[1]
    end = []
    for s, e in zip(span[0], end_raw):
        if pd.isna(e):
            end.append(int(s))
        elif len(e) == 2:
            end.append(int(s[:2] + e))
        else:
            end.append(int(e))
    df["year_end"] = end
    df["duration"] = df["year_end"] - df["year_start"] + 1
    return df


def load_region_decade() -> pd.DataFrame:
    return pd.read_csv(HERE / "deaths-by-region-decade.csv")


# ---------------------------------------------------------------------------
# Plot 02 — Decadal famine counts by death-band, stacked bars
# ---------------------------------------------------------------------------
def plot_02(df: pd.DataFrame) -> None:
    bands = [
        (100_000, 500_000, "100k–500k"),
        (500_000, 1_000_000, "500k–1M"),
        (1_000_000, 5_000_000, "1M–5M"),
        (5_000_000, float("inf"), "≥5M"),
    ]
    decades = np.arange(CATALOG_START, 2030, 10)
    counts = {label: [] for _, _, label in bands}
    for d in decades:
        sub = df[df["decade"] == d]
        for lo, hi, label in bands:
            counts[label].append(((sub["deaths"] >= lo) & (sub["deaths"] < hi)).sum())

    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = ["#cfe2f3", "#9fc5e8", "#3d85c6", "#0b3d66"]
    bottom = np.zeros(len(decades))
    for (lo, hi, label), color in zip(bands, colors):
        vals = np.array(counts[label])
        ax.bar(decades, vals, width=8, bottom=bottom, label=label,
               color=color, edgecolor="white", linewidth=0.6)
        bottom += vals

    partial_mask = decades >= PARTIAL_DECADE_START
    if partial_mask.any():
        ax.axvspan(PARTIAL_DECADE_START - 5, decades.max() + 5,
                   color="grey", alpha=0.08, zorder=0)
        ax.text(PARTIAL_DECADE_START, ax.get_ylim()[1] * 0.95,
                "partial\ndecade", fontsize=8, color="grey", ha="left", va="top")

    ax.set_title("Famines per decade by death band (WPF catalog, ≥100k deaths)")
    ax.set_xlabel("Decade")
    ax.set_ylabel("Number of famines")
    ax.set_xticks(decades)
    ax.set_xticklabels([str(d) for d in decades], rotation=45, ha="right")
    ax.legend(title="Deaths per event", frameon=False, loc="upper right")
    ax.text(0.01, -0.18,
            "Catalog: World Peace Foundation Historic Famines, 1870–2023. "
            "Each event placed in the decade of its start year.",
            transform=ax.transAxes, fontsize=8, color="grey")
    fig.savefig(PLOTS / "02_decadal_counts_by_band.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 05 — Decadal intensity: peak event + cumulative deaths
# ---------------------------------------------------------------------------
def plot_05(df: pd.DataFrame, region_decade: pd.DataFrame) -> None:
    decades = np.arange(CATALOG_START, 2030, 10)
    peak = df.groupby("decade")["deaths"].max().reindex(decades, fill_value=0)

    world = (region_decade.groupby("year")["decadal_famine_deaths"].sum()
             .reindex(decades, fill_value=0))

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5))

    axL.bar(decades, peak.values / 1e6, width=8,
            color="#0b3d66", edgecolor="white", linewidth=0.6)
    axL.set_yscale("log")
    axL.set_title("Peak single-famine deaths per decade")
    axL.set_xlabel("Decade")
    axL.set_ylabel("Deaths (millions, log scale)")
    axL.set_xticks(decades)
    axL.set_xticklabels([str(d) for d in decades], rotation=45, ha="right")
    axL.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}M"))
    for d, v in zip(decades, peak.values):
        if v > 0:
            top = df[(df["decade"] == d) & (df["deaths"] == v)].iloc[0]["entity"]
            label = re.sub(r"\s*\d{4}.*$", "", top)
            axL.text(d, v / 1e6 * 1.15, label, fontsize=7,
                     ha="center", va="bottom", rotation=0, color="#222")

    axR.bar(decades, world.values / 1e6, width=8,
            color="#a23b3b", edgecolor="white", linewidth=0.6)
    axR.set_title("Total famine deaths per decade (world)")
    axR.set_xlabel("Decade")
    axR.set_ylabel("Deaths (millions)")
    axR.set_xticks(decades)
    axR.set_xticklabels([str(d) for d in decades], rotation=45, ha="right")
    axR.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}M"))

    fig.suptitle("Decadal intensity — peak event vs. total deaths", y=1.02)
    fig.text(0.01, -0.04,
             "Left: largest single famine per decade (log-scaled). "
             "Right: sum across all famines in the decade. "
             "Source: WPF / Our World in Data.",
             fontsize=8, color="grey")
    fig.savefig(PLOTS / "05_decadal_intensity.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 06 — Great-famine timing: cumulative vs constant-rate + intervals
# ---------------------------------------------------------------------------
def plot_06(df: pd.DataFrame) -> None:
    great = df[df["deaths"] >= GREAT_FAMINE_THRESHOLD].sort_values("year_start").reset_index(drop=True)
    years = great["year_start"].values
    cum = np.arange(1, len(years) + 1)

    span_start, span_end = CATALOG_START, 2023
    total = len(great)
    rate = total / (span_end - span_start)
    ref_x = np.array([span_start, span_end])
    ref_y = np.array([0, total])

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5))

    axL.step(years, cum, where="post", color="#0b3d66", linewidth=2,
             label=f"Observed (n={total})")
    axL.plot(ref_x, ref_y, color="grey", linestyle="--",
             label=f"Constant rate ({rate:.2f}/yr)")
    axL.scatter(years, cum, s=22, color="#0b3d66", zorder=3)
    axL.set_title(f"Cumulative ≥{GREAT_FAMINE_THRESHOLD/1e6:.0f}M-death famines vs. constant-rate reference")
    axL.set_xlabel("Year")
    axL.set_ylabel("Cumulative count")
    axL.set_xlim(span_start - 5, span_end + 5)
    axL.legend(frameon=False, loc="upper left")

    intervals = np.diff(years)
    mids = years[1:]
    axR.bar(mids, intervals, width=2.5,
            color="#a23b3b", edgecolor="white", linewidth=0.4)
    mean_int = intervals.mean()
    axR.axhline(mean_int, color="grey", linestyle="--",
                label=f"Mean interval ({mean_int:.1f} yr)")
    if len(intervals) >= 5:
        roll = pd.Series(intervals).rolling(5, min_periods=2).mean()
        axR.plot(mids, roll, color="#0b3d66", linewidth=2, label="5-event rolling mean")
    axR.set_title(f"Inter-event intervals between ≥{GREAT_FAMINE_THRESHOLD/1e6:.0f}M-death famines")
    axR.set_xlabel("Year (later event in pair)")
    axR.set_ylabel("Years since previous great famine")
    axR.legend(frameon=False, loc="upper left")

    fig.suptitle("Great-famine timing — has the rate changed?", y=1.02)
    fig.text(0.01, -0.04,
             "A flat slope on the left = constant arrival rate. "
             "Bend below the dashed line in recent decades = rate has dropped. "
             "Source: WPF / Our World in Data.",
             fontsize=8, color="grey")
    fig.savefig(PLOTS / "06_great_famine_timing.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 07 — Death-magnitude frequency distribution (G-R analog)
# ---------------------------------------------------------------------------
def plot_07(df: pd.DataFrame) -> None:
    deaths = np.sort(df["deaths"].values)
    n = len(deaths)
    survival = 1 - np.arange(n) / n  # P(D >= d)

    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.loglog(deaths, survival, "o", color="#0b3d66",
              markersize=6, label="Empirical P(deaths ≥ x)")

    mask = deaths >= 200_000
    log_d = np.log10(deaths[mask])
    log_s = np.log10(survival[mask])
    slope, intercept = np.polyfit(log_d, log_s, 1)
    xs = np.array([deaths[mask].min(), deaths.max()])
    ys = 10 ** (intercept + slope * np.log10(xs))
    ax.loglog(xs, ys, color="#a23b3b", linewidth=1.8, linestyle="--",
              label=f"Power-law fit (α ≈ {-slope:.2f}) on deaths ≥ 200k")

    ax.set_title("Famine death-toll distribution (1870–2023)")
    ax.set_xlabel("Deaths per famine (log scale)")
    ax.set_ylabel("P(deaths ≥ x), log scale")
    ax.legend(frameon=False, loc="lower left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{int(v/1e6)}M" if v >= 1e6 else (f"{int(v/1e3)}k" if v >= 1e3 else f"{int(v)}")))
    ax.text(0.01, -0.10,
            "Straight line on log-log = power-law tail (analog of Gutenberg-Richter). "
            "Source: WPF / Our World in Data, n=" + str(n) + ".",
            transform=ax.transAxes, fontsize=8, color="grey")
    fig.savefig(PLOTS / "07_magnitude_distribution.png")
    plt.close(fig)


def main() -> None:
    df = load_events()
    region_decade = load_region_decade()
    print(f"Loaded {len(df)} famine events ({df['year'].min()}–{df['year'].max()})")
    plot_02(df)
    plot_05(df, region_decade)
    plot_06(df)
    plot_07(df)
    print(f"Wrote 4 plots to {PLOTS}/")


if __name__ == "__main__":
    main()
