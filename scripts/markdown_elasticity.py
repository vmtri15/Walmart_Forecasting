"""Estimate how store revenue responds to markdown spend.

The dataset has no prices, so this is a markdown (promotion) elasticity, not a price elasticity of demand.
MarkDown1-5 are only recorded from Nov 2011, so the model uses those 52 weeks (45 stores).

Model: log(weekly store revenue) ~ log(1 + total markdown) + store fixed effects + week fixed effects,
standard errors clustered by store. The week effects remove seasonality and holidays, so the estimate
comes from stores that ran bigger or smaller markdowns in the same week.

Run from the project root:
    python scripts/markdown_elasticity.py
Output:
    data/markdown_elasticity.csv   (coefficient, standard error, 95% interval)
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

MARKDOWNS = [f"MarkDown{i}" for i in range(1, 6)]
OUT_PATH = "data/markdown_elasticity.csv"

df = pd.read_csv("data/walmart_prepared.csv", parse_dates=["Date"])
wk = (
    df.groupby(["Store", "Date"])
    .agg(Revenue=("Revenue", "sum"), **{m: (m, "first") for m in MARKDOWNS})
    .reset_index()
)
wk["Markdown"] = wk[MARKDOWNS].sum(axis=1)
wk = wk[wk["Date"] >= "2011-11-01"]  # markdowns are not recorded before this
wk["log_rev"] = np.log(wk["Revenue"])
wk["log_md"] = np.log1p(wk["Markdown"])

fit = smf.ols("log_rev ~ log_md + C(Store) + C(Date)", data=wk).fit(
    cov_type="cluster", cov_kwds={"groups": wk["Store"]}
)
b, se = fit.params["log_md"], fit.bse["log_md"]
out = pd.DataFrame([{"Elasticity": b, "StdErr": se, "CI95_Low": b - 1.96 * se, "CI95_High": b + 1.96 * se,
                     "Observations": int(fit.nobs)}])
out.to_csv(OUT_PATH, index=False)
print(out.round(4).to_string(index=False))
print(f"A 10% larger markdown is associated with a {b * 0.1:.2%} change in weekly revenue (association, not proven cause).")
if out["CI95_Low"][0] <= 0 <= out["CI95_High"][0]:
    print("The 95% interval includes 0: no detectable effect of markdown size on revenue.")
