"""Rebuild data/walmart_cleaned.csv from the Kaggle files in data/raw/ (train, features, stores).

Run from the project root:
    python scripts/build_cleaned.py [out_path]
"""
import sys

import pandas as pd

RAW = "data/raw/"
OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/walmart_cleaned.csv"
MARKDOWNS = [f"MarkDown{i}" for i in range(1, 6)]
TYPE_CODE = {"A": 3, "B": 2, "C": 1}  # matches the encoding of the original cleaned file

train = pd.read_csv(RAW + "train.csv", parse_dates=["Date"])
features = pd.read_csv(RAW + "features.csv", parse_dates=["Date"])
stores = pd.read_csv(RAW + "stores.csv")

# IsHoliday exists in both train and features; keep one copy
df = train.merge(features.drop(columns="IsHoliday"), on=["Store", "Date"], how="left", validate="m:1")
df = df.merge(stores, on="Store", how="left", validate="m:1")

assert len(df) == len(train), "merge changed the row count"
assert df["Type"].notna().all(), "store missing from stores.csv"

df["IsHoliday"] = df["IsHoliday"].astype(int)
df["Dept"] = df["Dept"].astype(float)
df["Type"] = df["Type"].map(TYPE_CODE)
# Markdowns were only recorded from Nov 2011, so missing means "no markdown data", filled with 0
df[MARKDOWNS] = df[MARKDOWNS].fillna(0)
# CPI and Unemployment have gaps in the last weeks of the features file: carry the last value forward per store
df = df.sort_values(["Store", "Date"])
df[["CPI", "Unemployment"]] = df.groupby("Store")[["CPI", "Unemployment"]].ffill()

cols = ["Store", "Date", "IsHoliday", "Dept", "Weekly_Sales", "Temperature", "Fuel_Price", *MARKDOWNS,
        "CPI", "Unemployment", "Type", "Size"]
df = df[cols].reset_index(drop=True)
df.to_csv(OUT_PATH, index=False)
print("Saved", OUT_PATH, df.shape)
