DROP VIEW IF EXISTS store_revenue;

CREATE VIEW store_revenue AS
SELECT 
    Store,
    Date,
    SUM(Weekly_Sales) AS Revenue
FROM walmart_raw
GROUP BY Store, Date;

DROP VIEW IF EXISTS store_features;

CREATE VIEW store_features AS
SELECT
    w.Store,
    w.Date,
    w.Revenue,
    r.IsHoliday,
    r.Temperature,
    r.Fuel_Price,
    r.CPI,
    r.Unemployment
FROM store_revenue w
JOIN walmart_raw r
    ON w.Store = r.Store
    AND w.Date = r.Date
GROUP BY w.Store, w.Date;
