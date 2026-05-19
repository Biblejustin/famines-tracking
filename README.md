# famines-tracking

Data + analysis for tracking famines globally, parallel in spirit to the `earthquakes` and `spaceweather` tracking projects.

## Quick findings

- **No ≥1M-death famine since Cambodia 1975–79.** Pre-1975 baseline was a great famine every ~3 years. The cumulative-vs-constant-rate plot is the cleanest summary.
- **The ≥1M and ≥5M severity bands disappear after 1960.** Recent decades still see 2–5 famines per decade, but in the 100k–500k range.
- **Death-toll distribution is fat-tailed power law (α ≈ 0.76).** Same statistical regime Cirillo & Taleb document for war casualties.

See `plots/` for the four charts.

## Files

### Modern catalog (1870–2023)
- `famines-and-deaths.csv` — 78 individual famines ≥100k deaths. WPF/OWID.
- `deaths-by-region-year.csv` — annual deaths by region.
- `deaths-by-region-decade.csv` — decadal totals by region.
- `deaths-by-country-decade.csv` — decadal totals by country.
- `deaths-by-decade.csv` — global decadal **death rate** (per 100k population).
- `famines-and-deaths.metadata.json` — OWID metadata sidecar.

Source: World Peace Foundation (2025), *Historic Famines dataset*, via [Our World in Data](https://ourworldindata.org/famines). Only events ≥100k deaths.

### Historical pointer list (pre-1870)
- `historical_famines_pre1870.csv` — ~70 entries c. 2700 BC – 1868 AD. Hand-compiled from Wikipedia's *List of famines* (citing Ó Gráda, Davis, Jordan, Mallory, Bhatia, et al.), supplemented with Greco-Roman entries from Garnsey, *Famine and Food Supply in the Greco-Roman World* (1988), and biblical/Josephan references where externally attested.

Treat this as a research index, not a dataset:
- Pre-1500 mortality figures are orders of magnitude only.
- BC years are encoded as negative integers (`-587` = 587 BC).
- `source_tradition` names the primary source or scholarly catalog.
- Excluded from all statistical plots.

### Analysis
- `make_plots.py` — generates the four plots below.
- `plots/02_decadal_counts_by_band.png` — stacked bars, famines per decade by death band.
- `plots/05_decadal_intensity.png` — peak single-famine deaths per decade + total deaths per decade.
- `plots/06_great_famine_timing.png` — cumulative ≥1M-death famines vs. constant-rate reference + inter-event intervals.
- `plots/07_magnitude_distribution.png` — log-log survival function (Gutenberg-Richter analog), power-law fit.

## Reproducing the plots

```bash
uv venv .venv
uv pip install --python .venv/bin/python matplotlib pandas numpy
.venv/bin/python make_plots.py
```

## Analytical conventions

Adapted from a parallel earthquake-tracking project; transferable to other rare-event "signs" data (wars, pandemics).

- **Catalog regime constants.** WPF coverage starts 1870 at ≥100k deaths. Pre-1870 entries excluded from all statistical claims.
- **Partial-period handling.** 2020s bar in plot 02 shaded grey; not in trend fits.
- **Rolling/cumulative views for rare events.** Inter-event intervals and cumulative-vs-constant-rate sidestep calendar-bin noise.
- **Log-scaled severity.** Plot 05-left and plot 07 use log scales because death tolls span 10⁵ to 10⁷.
- **Power-law fit on the tail only.** Plot 07 fits the line on deaths ≥ 200k to avoid the catalog-completeness floor.

## Open work

- Population-normalized versions of plots 02 and 05 (need world-pop time series).
- Trailing-25-year sliding window (plot 04 analog).
- Add IPC Phase 5 person-month data for 2004–present to extend the modern series past raw mortality.
