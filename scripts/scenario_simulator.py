import pandas as pd

df = pd.read_csv("data/walmart_prepared.csv")

def simulate(df, price_change):
    d = df.copy()
    d["Adj_Revenue"] = d["Revenue"] * (1 + price_change)
    d["Adj_Profit"] = d["Adj_Revenue"] * 0.12
    d["Adj_Margin"] = d["Adj_Profit"] / d["Adj_Revenue"]
    return d

minus3 = simulate(df, -0.03)
plus2 = simulate(df, 0.02)
minus3.to_csv("data/scenario_minus3.csv", index=False)
plus2.to_csv("data/scenario_plus2.csv", index=False)

print("Scenarios saved")
