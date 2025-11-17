import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

df = pd.read_csv("data/walmart_prepared.csv")
df["Date"] = pd.to_datetime(df["Date"])

stores = df["Store"].unique()

for store_id in stores:
    store_df = df[df["Store"] == store_id].copy()
    store_df = store_df.groupby("Date")["Revenue"].sum().reset_index()
    store_df = store_df.sort_values("Date").reset_index(drop=True)

    series = store_df["Revenue"]

    try:
        model = ARIMA(series, order=(3,1,3))
        fit = model.fit()
        store_df["forecast"] = fit.predict(start=1, end=len(series))
        store_df["forecast"] = store_df["forecast"].clip(lower=0)

        store_df.to_csv(f"data/arima_store_{store_id}.csv", index=False)
        print(f"Saved ARIMA forecast for store {store_id}")

    except:
        print(f"Skipping store {store_id} due to error")
