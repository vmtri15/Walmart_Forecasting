# Power BI dashboard

Run `python scripts/build_powerbi.py`, then in Power BI Desktop: **Get data > Excel** and load
`data/powerbi.xlsx` (sheets `Series` and `ModelError`).
Create a `Stores` table (`Stores = DISTINCT(ModelError[Store])`) and relate it to each table on `Store`; use `Stores[Store]` in a slicer.

| Page | Visual | Fields |
| --- | --- | --- |
| Models | Clustered column | Axis `Model`, Values `Average of MAPE` (format %) |
| Models | Card | `Wins = COUNTROWS(FILTER(ModelError, ModelError[Model] = ModelError[Best_Model]))` in a column chart by Model |
| Holdout | Line | Axis `Date`, Legend `Series`, Values `Value`; filter Series to Actual, Prophet, ARIMA, XGB, SeasonalNaive |
| Forecast | Line + band | Series = Forecast; Values `Value`, `Low`, `High` (Min/Max) |
| Markdown | Line | Series in Forecast, markdown_minus30, markdown_plus30 |

Built in Power BI on the web as the **Walmart Forecast** report (My workspace > Walmart), pages Models, Holdout, Forecast, Markdown. Win is a Power Query column: `if [Model] = [Best_Model] then 1 else 0`. To refresh, rerun the script and re-upload `powerbi.xlsx`.
