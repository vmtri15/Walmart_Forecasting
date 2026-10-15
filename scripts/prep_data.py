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

# Lag and rolling features, built per Store/Dept series and using past weeks only
df = df.sort_values(["Store", "Dept", "Date"]).reset_index(drop=True)
g = df.groupby(["Store", "Dept"])["Revenue"]
for k in (1, 2, 4, 12):
    df[f"Lag_{k}"] = g.shift(k)
# shift(1) first so the window excludes the week being predicted
df["Rolling_4w"] = g.transform(lambda s: s.shift(1).rolling(4).mean())
df["Rolling_12w"] = g.transform(lambda s: s.shift(1).rolling(12).mean())

# Seasonal features
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Week"] = df["Date"].dt.isocalendar().week

# Save output
df.to_csv("data/walmart_prepared.csv", index=False)

print("Saved data/walmart_prepared.csv")
