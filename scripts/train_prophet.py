import pandas as pd
from prophet import Prophet

df = pd.read_csv("data/walmart_prepared.csv")
df["Date"] = pd.to_datetime(df["Date"])

store_id = 1
store_df = df[df["Store"] == store_id].copy()

prophet_df = store_df[["Date","Revenue"]]
prophet_df = prophet_df.rename(columns={"Date":"ds", "Revenue":"y"})

m = Prophet(weekly_seasonality=True, yearly_seasonality=True)
m.fit(prophet_df)

future = m.make_future_dataframe(periods=52, freq="W")
forecast = m.predict(future)

forecast.to_csv(f"data/forecast_store_{store_id}.csv", index=False)
print("Saved forecast")
