# Walmart Revenue Forecasting

**How accurately can weekly revenue be forecast for 45 Walmart stores, and which model should a planner trust?**

## The answer

- **Prophet is the model to use.** On the last 12 weeks of each store, held out and never seen in training, Prophet was the most accurate model in 30 of 45 stores, with a mean error (MAPE) of 4.4%. ARIMA was best in 11 stores and XGBoost in 4.
- **A simple baseline is hard to beat.** "Same week last year" has a mean error of 5.5%. Prophet beats it in 30 stores, ARIMA in 21, and XGBoost in only 13.
- **An earlier version of this project was wrong.** It reported XGBoost as best in 42 stores because it tested models on their own training data and used features that included the week being predicted. Both problems are fixed, and the results above come from a clean holdout.
- **A 52 week forecast with a range.** Every store has a weekly forecast for the next year with an 80% range. On the held out weeks the range contained 93% of actual values, so it is a little wide.
- **Markdowns show no measurable effect on revenue.** The data has no prices, so price elasticity cannot be estimated. Revenue does not move with markdown size: the estimate is 0.008 with a 95% interval of -0.001 to 0.017.

## Data

Kaggle competition "Walmart Recruiting - Store Sales Forecasting": 421,570 weekly records for 45 stores and their departments, February 2010 to October 2012. Fields include weekly sales, holiday weeks, temperature, fuel price, CPI, unemployment, markdowns, store type and size.

## How it works

1. `build_cleaned.py` merges the three Kaggle files into one cleaned table.
2. `build_sql_features.py` builds weekly store revenue, lags and rolling averages with the SQL in `sql/`, and checks them against the Python numbers. They match on all 6,435 store weeks.
3. `prep_data.py` adds lag and rolling features from past weeks only.
4. `holdout_evaluation.py` fits Prophet, ARIMA and XGBoost on each store's history, forecasts the last 12 weeks, and compares them with a seasonal baseline.
5. `forecast_future.py` fits Prophet on all history and forecasts 52 weeks with an 80% range.
6. `markdown_elasticity.py` estimates how weekly revenue responds to markdown spend, using store and week fixed effects.
7. `scenario_simulator.py` applies that estimate to the forecast for markdowns 30% lower or higher. Both stay within about 1% of the baseline.

## Outputs

| File | Contents |
| --- | --- |
| `data/holdout_summary.csv` | Error of each model for each store, and the best model |
| `data/holdout_predictions.csv` | Actual and predicted revenue for the held out weeks |
| `data/forecast_future.csv` | 52 week forecast with low and high values for each store |
| `data/markdown_elasticity.csv` | The markdown estimate and its interval |
| `data/scenario_markdown.csv` | Revenue under markdowns 30% lower or higher |
| `data/store_features_sql.csv` | Weekly store revenue and features built in SQL |

## Limits

- The holdout is one 12 week window that does not include the holiday peak, so accuracy in November and December is untested.
- The markdown estimate covers November 2011 to October 2012, the only period with markdown data.
- The data has no prices or costs, so profit, margin and price changes cannot be modeled.
- There is no dashboard yet. The output files above are ready to load into one.

## Reproduce

Download `train.csv`, `features.csv` and `stores.csv` from the Kaggle competition into `data/raw/`, then run:

```bash
pip install -r requirements.txt
bash run_all.sh
```

The full run takes a few minutes. `notebooks/eda.ipynb` explores the cleaned data.

## Repository structure

```
data/        outputs (raw Kaggle files go in data/raw/, not included)
notebooks/   exploratory analysis
scripts/     the pipeline, in the order of run_all.sh
sql/         table, feature and export queries for SQLite
run_all.sh   runs the whole pipeline
```
