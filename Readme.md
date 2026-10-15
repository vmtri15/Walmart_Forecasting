Walmart Revenue Forecasting

This project forecasts weekly revenue for 45 Walmart stores using SQL and Python. It compares Prophet, ARIMA, and XGBoost on a time based holdout, produces a 52 week forecast with prediction intervals, and estimates how revenue responds to markdown spend. A Power BI dashboard is planned and not yet built.

Project Goal

Help finance and operations teams plan inventory and staffing with a forward view of store revenue and an honest range of uncertainty. Analysts can compare models per store and see whether markdown size moves revenue.

Key Results

Evaluated on a time based holdout (last 12 weeks per store, models fit on earlier weeks only, features built from past weeks only). See scripts/holdout_evaluation.py and data/holdout_summary.csv.

• Prophet was best for 30 of 45 stores, ARIMA for 11, XGBoost for 4.
• Mean MAPE: Prophet 4.4%, ARIMA 5.3%, XGBoost 8.0%, seasonal naive (same week last year) 5.5%.
• Prophet beats the seasonal naive baseline in 30 of 45 stores, ARIMA in 21, XGBoost in 13.
• An earlier version scored models on their own training data and reported XGBoost as best for 42 stores. That result was caused by in-sample scoring and by rolling features that included the week being predicted, and has been removed.
• The SQL views in sql/ build lag and rolling features at store level.
• Power BI dashboard: planned, not built yet.

Technologies Used

SQL
SQLite was used to store and prepare raw data. SQL views aggregated revenue, joined economic fields, and removed missing values before Python loaded the final tables.

Python
Pandas
NumPy
Scikit-learn
Prophet
Statsmodels
XGBoost

Python handled feature engineering, lag creation, rolling values, model training, evaluation, forecasting, and the markdown what-if.

Power BI
Power BI is planned for forecasts, model performance, and the markdown what-if. No dashboard file exists yet.

Version Control
Git and GitHub organized notebooks, scripts, and dashboard artifacts.

Dataset

Source: Kaggle Walmart Store Sales
Records: 421,570 weekly store and department observations (Feb 2010 to Oct 2012)
Fields included revenue, holiday flags, fuel price, consumer price index, unemployment, markdown activity, temperature, store type, and size.

Reproduce

Download train.csv, features.csv and stores.csv from the Kaggle competition "Walmart Recruiting - Store Sales Forecasting" into data/raw/, then run:

    pip install -r requirements.txt
    bash run_all.sh

SQL Pipeline

The SQL pipeline loads the raw CSV into a database. SQL views handle aggregation and preparation before Python completes the model steps. The SQL folder contains the full set of queries.

SQL steps

Load raw CSV into walmart_raw.

Create store_revenue to calculate weekly revenue per store.

Create store_features to join holidays and economic values.

Add lag fields and rolling averages using window functions.

Export prepared tables back into Python.

This approach ensures consistent data structures and gives clear visibility into transformations.

Feature Engineering

Python adds additional features that strengthen forecasting performance.
Features include Lag_1, Lag_2, Lag_4, Lag_12, Rolling_4w, Rolling_12w, seasonal fields, and holiday flags. Economic fields help capture external effects.

Feature engineering uses past weeks only (no leakage) and feeds the XGBoost model.

Model Training

Three forecasting models were implemented.

Prophet
Captures weekly and yearly seasonality. Good at holiday patterns.

ARIMA
Works on smooth data. Struggles with heavy noise. Included for comparison.

XGBoost
Uses engineered features and external variables. Handles nonlinear patterns well. Performs best across almost all stores.

Each model is trained per store on store-week revenue. scripts/holdout_evaluation.py writes actual vs predicted holdout weeks for all models to data/holdout_predictions.csv for Power BI.

Model Selection Engine

scripts/holdout_evaluation.py scores each model with MAPE on the held out weeks and picks the best model per store. Results go to data/holdout_summary.csv for Power BI.

Future Forecast

scripts/forecast_future.py fits Prophet on each store and writes a 52 week forecast with 80% prediction intervals to data/forecast_future.csv. On the 12 held out weeks the 80% interval contained 92% of actual values, so the intervals are somewhat wide. The holdout does not include a peak holiday season, so coverage there is untested.

Markdown Elasticity

The dataset has no prices, so price elasticity cannot be estimated. scripts/markdown_elasticity.py instead estimates how weekly store revenue responds to markdown spend (Nov 2011 to Oct 2012, store and week fixed effects). The estimate is 0.008 with a 95% interval of -0.001 to 0.017, so there is no detectable effect of markdown size on revenue.

Markdown What-If

scripts/scenario_simulator.py applies the elasticity and its 95% interval to the 52 week forecast for markdowns 30% lower or higher. The result is within about 1% of baseline in both directions, consistent with no detectable effect. Profit and margin are not modeled because the dataset has no cost data.

Power BI Dashboard

The planned dashboard will include:

• Actual vs forecast lines
• Store filter
• Model performance comparison
• Holiday impact view
• Economic factor trends
• Scenario simulator
• Best model selection table

Managers will be able to review store forecasts with ranges and compare models per store.

Business Impact

Analysts can compare models by store, see how uncertain the forecast is, and check whether markdown spend is associated with revenue.

Repository Structure
Walmart-Revenue-Forecasting/
│
├── data/
├── sql/
├── scripts/
├── notebooks/
├── dashboard/
├── reports/
└── README.md
# Walmart_Forecasting
