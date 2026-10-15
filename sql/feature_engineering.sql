DROP VIEW IF EXISTS lag_features;

CREATE VIEW lag_features AS
SELECT 
    Store,
    Date,
    Revenue,
    LAG(Revenue, 1) OVER (PARTITION BY Store ORDER BY Date) AS Lag_1,
    LAG(Revenue, 2) OVER (PARTITION BY Store ORDER BY Date) AS Lag_2,
    LAG(Revenue, 4) OVER (PARTITION BY Store ORDER BY Date) AS Lag_4,
    LAG(Revenue, 12) OVER (PARTITION BY Store ORDER BY Date) AS Lag_12
FROM store_revenue;

DROP VIEW IF EXISTS rolling_features;

CREATE VIEW rolling_features AS
SELECT
    Store,
    Date,
    Revenue,
    AVG(Revenue) OVER (PARTITION BY Store ORDER BY Date ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING) AS Rolling_4w,
    AVG(Revenue) OVER (PARTITION BY Store ORDER BY Date ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING) AS Rolling_12w
FROM store_revenue;
