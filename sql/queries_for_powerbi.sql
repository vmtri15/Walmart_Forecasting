SELECT *
FROM store_features;

SELECT *
FROM lag_features;

SELECT *
FROM rolling_features;
SELECT
    sf.Store,
    sf.Date,
    sf.Revenue,
    sf.CPI,
    sf.Fuel_Price,
    sf.Unemployment,
    lf.Lag_1,
    lf.Lag_4,
    rf.Rolling_4w,
    rf.Rolling_12w
FROM store_features sf
LEFT JOIN lag_features lf
    ON sf.Store = lf.Store AND sf.Date = lf.Date
LEFT JOIN rolling_features rf
    ON sf.Store = rf.Store AND sf.Date = rf.Date;
