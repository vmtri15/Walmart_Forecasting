# Walmart_Forecasting
Walmart Revenue Forecasting and Profitability Optimization

This project builds a complete revenue forecasting and profitability system using SQL, Python, and Power BI. It predicts weekly sales for 45 Walmart stores, evaluates markdown and holiday effects, and measures model accuracy across Prophet, ARIMA, and XGBoost. The system includes SQL-based preprocessing, feature engineering, multi model training, scenario testing, and a full business dashboard.

Project Goal

Help finance and operations teams plan inventory, adjust pricing, and understand how economic factors influence store performance. Forecasts support margin planning and provide a forward view of store health. Managers can compare models, test price adjustments, and review promotional return on investment.

Key Results

• XGBoost achieved the best accuracy for 42 of 45 stores.
• Prophet performed best for three stores with heavy seasonal behavior.
• ARIMA did not outperform the other models.
• SQL preprocessing reduced Python cleaning time by removing repeated data steps.
• Power BI delivered interactive forecasting with price and markdown sliders.

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

Python handled feature engineering, lag creation, rolling values, model training, evaluation, and scenario testing.

Power BI
Power BI visualized forecasts, model performance, economic influences, and price simulations.

Version Control
Git and GitHub organized notebooks, scripts, and dashboard artifacts.

Dataset

Source: Kaggle Walmart Store Sales
Records: More than 600k weekly observations
Fields included revenue, holiday flags, fuel price, consumer price index, unemployment, markdown activity, temperature, store type, and size.

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

Feature engineering improves model accuracy for all three models and supports scenario simulations.

Model Training

Three forecasting models were implemented.

Prophet
Captures weekly and yearly seasonality. Good at holiday patterns.

ARIMA
Works on smooth data. Struggles with heavy noise. Included for comparison.

XGBoost
Uses engineered features and external variables. Handles nonlinear patterns well. Performs best across almost all stores.

Each model was trained per store. Predictions were saved into the data folder for Power BI integration.

Model Selection Engine

A selection engine evaluates the accuracy of each model using MAPE. The engine identifies the best model for each store. Results are exported to a summary file used in Power BI.

Scenario Simulation

A Python script builds price and markdown simulations. Users can test two percent or three percent changes and see the effect on revenue and margin. Power BI includes interactive sliders linked to these results.

Power BI Dashboard

The dashboard includes:

• Actual vs forecast lines
• Store filter
• Model performance comparison
• Holiday impact view
• Economic factor trends
• Scenario simulator
• Best model selection table

Managers can review store health, project margin expectations, and test price ideas with immediate feedback.

Business Impact

The system gives Walmart style decision support for planning and pricing. Analysts can compare stores, understand economic sensitivity, and measure promotional return. Dynamic forecasting helps reduce overstock, improve timing of markdowns, and raise margin stability.

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

