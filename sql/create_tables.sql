DROP TABLE IF EXISTS walmart_raw;

CREATE TABLE walmart_raw (
    Store INT,
    Date TEXT,
    Dept INT,
    Weekly_Sales REAL,
    IsHoliday INT,
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
