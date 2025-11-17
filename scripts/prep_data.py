import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/walmart_cleaned.csv")

# Drop auto index column
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Convert to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Basic financial features
df["Revenue"] = df["Weekly_Sales"]
df["Profit"] = df["Revenue"] * 0.12           # simple placeholder profit
df["Margin"] = df["Profit"] / df["Revenue"]

# Lag features
df["Lag_1"] = df["Revenue"].shift(1)
df["Lag_2"] = df["Revenue"].shift(2)
df["Lag_4"] = df["Revenue"].shift(4)
df["Lag_12"] = df["Revenue"].shift(12)

# Rolling features
df["Rolling_4w"] = df["Revenue"].rolling(window=4).mean()
df["Rolling_12w"] = df["Revenue"].rolling(window=12).mean()

# Seasonal features
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Week"] = df["Date"].dt.isocalendar().week

# Save output
df.to_csv("data/walmart_prepared.csv", index=False)

print("Saved data/walmart_prepared.csv")
