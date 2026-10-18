"""Build the store level features with the SQL in sql/, and check them against the Python pipeline.

Runs create_tables.sql, loads data/walmart_cleaned.csv, runs clean_transform.sql and
feature_engineering.sql, then exports the last query in queries_for_powerbi.sql to
data/store_features_sql.csv. It stops with an error if the SQL results disagree with Python:
  * weekly store revenue must equal the Python sum by store and week
  * Lag_1 must equal the previous week's revenue
  * Rolling_4w must equal the mean of the previous 4 weeks (weeks with a full window only)

Run from the project root, after build_cleaned.py:
    python scripts/build_sql_features.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / 'sql'
DB = ROOT / 'data/walmart.db'
OUT = ROOT / 'data/store_features_sql.csv'


def main():
    DB.unlink(missing_ok=True)
    raw = pd.read_csv(ROOT / 'data/walmart_cleaned.csv')
    with sqlite3.connect(DB) as c:
        c.executescript((SQL / 'create_tables.sql').read_text())
        raw.to_sql('walmart_raw', c, if_exists='append', index=False)  # matched by column name
        c.executescript((SQL / 'clean_transform.sql').read_text())
        c.executescript((SQL / 'feature_engineering.sql').read_text())
        final_query = [q for q in (SQL / 'queries_for_powerbi.sql').read_text().split(';') if q.strip()][-1]
        features = pd.read_sql_query(final_query, c).sort_values(['Store', 'Date']).reset_index(drop=True)

    # the same numbers built in Python
    py = raw.groupby(['Store', 'Date'], as_index=False)['Weekly_Sales'].sum().rename(columns={'Weekly_Sales': 'Revenue'})
    py = py.sort_values(['Store', 'Date']).reset_index(drop=True)
    g = py.groupby('Store')['Revenue']
    py['Lag_1'] = g.shift(1)
    py['Rolling_4w'] = g.transform(lambda s: s.shift(1).rolling(4).mean())

    assert len(features) == len(py), f'{len(features)} SQL rows but {len(py)} Python rows'
    assert (features[['Store', 'Date']].to_numpy() == py[['Store', 'Date']].to_numpy()).all(), 'store weeks differ'
    assert np.allclose(features['Revenue'], py['Revenue']), 'weekly store revenue differs'
    assert np.allclose(features['Lag_1'], py['Lag_1'], equal_nan=True), 'Lag_1 differs'
    full = py['Rolling_4w'].notna()  # SQL averages a shorter window in a store's first weeks
    assert np.allclose(features.loc[full, 'Rolling_4w'], py.loc[full, 'Rolling_4w']), 'Rolling_4w differs'

    features.to_csv(OUT, index=False)
    print(f'SQL features match Python for {len(features)} store weeks. Saved {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
