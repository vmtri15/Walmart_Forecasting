"""Markdown what-if on top of the 52 week forecast.

Uses the elasticity from markdown_elasticity.py (log-log, so a markdown change of p moves revenue by
elasticity * ln(1 + p)). The 95% interval of the elasticity gives a low and high case. Because that
interval includes 0, expect the low and high cases to straddle the baseline.

Run from the project root:
    python scripts/scenario_simulator.py
Output:
    data/scenario_markdown.csv
"""
import numpy as np
import pandas as pd

SCENARIOS = {"markdown_minus30": -0.30, "markdown_plus30": 0.30}

base = pd.read_csv("data/forecast_future.csv")
el = pd.read_csv("data/markdown_elasticity.csv").iloc[0]

rows = []
for name, pct in SCENARIOS.items():
    shift = np.log1p(pct)
    d = base[["Store", "Date", "Forecast"]].copy()
    d["Scenario"] = name
    d["Revenue_Low"] = d["Forecast"] * np.exp(el["CI95_Low"] * shift)
    d["Revenue_Mid"] = d["Forecast"] * np.exp(el["Elasticity"] * shift)
    d["Revenue_High"] = d["Forecast"] * np.exp(el["CI95_High"] * shift)
    rows.append(d)

out = pd.concat(rows)
out.to_csv("data/scenario_markdown.csv", index=False)
for name, g in out.groupby("Scenario"):
    t = g["Forecast"].sum()
    print(f"{name}: revenue {g['Revenue_Low'].sum() / t - 1:+.2%} to {g['Revenue_High'].sum() / t - 1:+.2%} vs baseline")
