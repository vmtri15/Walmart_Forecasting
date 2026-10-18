-- For the sqlite3 command line, run from the project root after create_tables.sql.
-- --skip 1 leaves out the header row. scripts/build_sql_features.py does the same load from Python.
.import --csv --skip 1 data/walmart_cleaned.csv walmart_raw
