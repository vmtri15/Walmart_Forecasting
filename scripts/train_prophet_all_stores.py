import pandas as pd
from prophet import Prophet

df = pd.read_csv("data/walmart_prepared.csv")
df["Date"] = pd.to_datetime(df["Date"])

stores = df["Store"].unique()

for store_id in stores:
    store_df = df[df["Store"] == store_id].copy()
    store_df = store_df.groupby("Date")["Revenue"].sum().reset_index()

    prophet_df = store_df.rename(columns={"Date":"ds", "Revenue":"y"})

    m = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    m.fit(prophet_df)

    future = m.make_future_dataframe(periods=52, freq="W")
    forecast = m.predict(future)

    out_path = f"data/forecast_prophet_store_{store_id}.csv"
    forecast.to_csv(out_path, index=False)
    print("Saved", out_path)
