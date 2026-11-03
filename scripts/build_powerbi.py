"""Writes data/powerbi.xlsx: tidy tables (one sheet each) to load into Power BI."""
import pandas as pd

r = lambda n: pd.read_csv(f"data/{n}.csv", parse_dates=["Date"] if n not in ("holdout_summary", "markdown_elasticity") else [])
# legend labels people read in the report
names = {"SeasonalNaive": "Seasonal baseline", "XGB": "XGBoost",
         "markdown_minus30": "Markdown -30%", "markdown_plus30": "Markdown +30%"}
stores = pd.read_csv("data/raw/stores.csv")[["Store", "Type"]]
stores["Type"] = "Type " + stores["Type"]

hist = r("store_features_sql")[["Store", "Date", "Revenue"]].rename(columns={"Revenue": "Value"})
hist["Series"] = "History"
h = r("holdout_predictions").melt(["Store", "Date"], var_name="Series", value_name="Value")
f = r("forecast_future").rename(columns={"Forecast": "Value", "Lower_80": "Low", "Upper_80": "High"})
f["Series"] = "Forecast"
f["Band"] = f["High"] - f["Low"]  # stacked-area height for the shaded 80% range
s = r("scenario_markdown").rename(columns={"Scenario": "Series", "Revenue_Mid": "Value", "Revenue_Low": "Low", "Revenue_High": "High"})
cols = ["Store", "Date", "Series", "Value", "Low", "High", "Band"]
series = pd.concat([hist, h, f, s]).reindex(columns=cols).replace({"Series": names}).merge(stores, on="Store")

m = r("holdout_summary").melt(["Store", "Best_Model"], var_name="Model", value_name="MAPE")
m["Model"] = m["Model"].str.replace("_MAPE", "")
m = m.replace({"Model": names, "Best_Model": names}).merge(stores, on="Store")
m["Win"] = (m["Model"] == m["Best_Model"]).astype(int)
m["Store name"] = "Store " + m["Store"].astype(str).str.zfill(2)

mean = m.groupby("Model")["MAPE"].mean()
e = r("markdown_elasticity").iloc[0]
kpi = pd.DataFrame([{
    "Prophet error": mean["Prophet"], "Baseline error": mean["Seasonal baseline"],
    "Prophet stores won": int(m.loc[m["Model"] == "Prophet", "Win"].sum()), "Stores": m["Store"].nunique(),
    "Markdown effect": e["Elasticity"], "Markdown CI low": e["CI95_Low"], "Markdown CI high": e["CI95_High"]}])
assert kpi["Prophet stores won"][0] == 30 and len(series["Type"].dropna()) == len(series)

with pd.ExcelWriter("data/powerbi.xlsx") as w:
    series.to_excel(w, sheet_name="Series", index=False)
    m.to_excel(w, sheet_name="ModelError", index=False)
    kpi.to_excel(w, sheet_name="KPI", index=False)
print("wrote data/powerbi.xlsx")
print(kpi.T)
