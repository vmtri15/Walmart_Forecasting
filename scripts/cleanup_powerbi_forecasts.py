import pandas as pd
import glob
import os

# -----------------------------------------------------
# CONFIG: Folder containing all your forecast CSVs
# -----------------------------------------------------
INPUT_FOLDER = "data/"
OUTPUT_FOLDER = "data/powerbi_ready/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------------------------------
# Helper function: clean each forecast file
# -----------------------------------------------------
def clean_forecast_file(filepath):
    df = pd.read_csv(filepath)

    filename = os.path.basename(filepath)
    print(f"Cleaning: {filename}")

    # Detect model type from filename
    if "prophet" in filename.lower():
        model = "prophet"
    elif "arima" in filename.lower():
        model = "arima"
    elif "xgb" in filename.lower():
        model = "xgb"
    else:
        print(f"Skipping unknown file: {filename}")
        return

    # -------------------------------------------------
    # Rename date column if needed
    # -------------------------------------------------
    if "ds" in df.columns:
        df = df.rename(columns={"ds": "Date"})
    if "date" in df.columns:
        df = df.rename(columns={"date": "Date"})

    # Convert Date to datetime
    df["Date"] = pd.to_datetime(df["Date"])

    # -------------------------------------------------
    # Rename prediction columns
    # -------------------------------------------------
    if model == "prophet":
        # Prophet's main forecast column is "yhat"
        if "yhat" in df.columns:
            df = df.rename(columns={"yhat": "prophet_pred"})
        else:
            raise ValueError("yhat column missing in Prophet file.")

    elif model == "arima":
        if "forecast" in df.columns:
            df = df.rename(columns={"forecast": "arima_pred"})
        else:
            raise ValueError("forecast column missing in ARIMA file.")

    elif model == "xgb":
        if "xgb_pred" not in df.columns:
            raise ValueError("xgb_pred column missing in XGB file.")

    # -------------------------------------------------
    # Add Store column if missing
    # -------------------------------------------------
    if "Store" not in df.columns:
        # Detect store number from filename: e.g. _store_1.csv
        try:
            store_num = int("".join([c for c in filename if c.isdigit()])) 
        except:
            store_num = 1  # fallback
        df["Store"] = store_num

    # -------------------------------------------------
    # Keep only columns important for Power BI
    # -------------------------------------------------
    keep_cols = ["Date", "Store"]

    if model == "prophet":
        keep_cols.append("prophet_pred")
    if model == "arima":
        keep_cols.append("arima_pred")
    if model == "xgb":
        keep_cols.append("xgb_pred")

    df = df[keep_cols]

    # -------------------------------------------------
    # Output cleaned file
    # -------------------------------------------------
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    df.to_csv(output_path, index=False)

    print(f"Saved cleaned file: {output_path}")


# -----------------------------------------------------
# Clean all forecast files in INPUT_FOLDER
# -----------------------------------------------------
forecast_files = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

for file in forecast_files:
    clean_forecast_file(file)

print("\nALL CLEANED AND READY FOR POWER BI.")
