"""Writes data/powerbi.xlsx: tidy tables (one sheet each) to load into Power BI."""
import pandas as pd

r = lambda n: pd.read_csv(f"data/{n}.csv", parse_dates=["Date"] if n != "holdout_summary" else [])

h = r("holdout_predictions").melt(["Store", "Date"], var_name="Series", value_name="Value")
f = r("forecast_future").rename(columns={"Forecast": "Value", "Lower_80": "Low", "Upper_80": "High"})
f["Series"] = "Forecast"
s = r("scenario_markdown").rename(columns={"Scenario": "Series", "Revenue_Mid": "Value", "Revenue_Low": "Low", "Revenue_High": "High"})
s = s[["Store", "Date", "Series", "Value", "Low", "High"]]
series = pd.concat([h, f[["Store", "Date", "Series", "Value", "Low", "High"]], s])

m = r("holdout_summary").melt(["Store", "Best_Model"], var_name="Model", value_name="MAPE")
m["Model"] = m["Model"].str.replace("_MAPE", "")
with pd.ExcelWriter("data/powerbi.xlsx") as w:
    series.to_excel(w, sheet_name="Series", index=False)
    m.to_excel(w, sheet_name="ModelError", index=False)
print("wrote data/powerbi.xlsx")
