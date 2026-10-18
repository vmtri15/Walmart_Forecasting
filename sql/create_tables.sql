DROP TABLE IF EXISTS walmart_raw;

-- Columns in the same order as data/walmart_cleaned.csv, so a positional CSV import lands in the right columns.
CREATE TABLE walmart_raw (
    Store INT,
    Date TEXT,
    IsHoliday INT,
    Dept REAL,
    Weekly_Sales REAL,
    Temperature REAL,
    Fuel_Price REAL,
    MarkDown1 REAL,
    MarkDown2 REAL,
    MarkDown3 REAL,
    MarkDown4 REAL,
    MarkDown5 REAL,
    CPI REAL,
    Unemployment REAL,
    Type INT,
    Size INT
);
