# Power BI dashboard

Run `python scripts/build_powerbi.py`, then in Power BI Desktop: **Get data > Excel** and load
`data/powerbi.xlsx` (sheets `Series` and `ModelError`).
Create the `Stores` and `Calendar` tables and the measures described in [Semantic model](#semantic-model) below; use `Stores[Store]` in a slicer.

| Page | Visual | Fields |
| --- | --- | --- |
| Models | Clustered column | Axis `Model`, Values `Average of MAPE` (format %) |
| Models | Card | `Wins = COUNTROWS(FILTER(ModelError, ModelError[Model] = ModelError[Best_Model]))` in a column chart by Model |
| Holdout | Line | Axis `Date`, Legend `Series`, Values `Value`; filter Series to Actual, Prophet, ARIMA, XGB, SeasonalNaive |
| Forecast | Line + band | Series = Forecast; Values `Value`, `Low`, `High` (Min/Max) |
| Markdown | Line | Series in Forecast, markdown_minus30, markdown_plus30 |

Built in Power BI on the web as the **Walmart Forecast** report (My workspace > Walmart), pages Models, Holdout, Forecast, Markdown, Trends. Win is a Power Query column: `if [Model] = [Best_Model] then 1 else 0`. To refresh, rerun the script and re-upload `powerbi.xlsx`. Colors and card borders come from `powerbi_theme.json` (Design > Import theme); the store and store-type drop-downs are synced across the Holdout, Forecast and Markdown pages. The model has two DAX measures, `Actual revenue` (Series = History) and `Forecast revenue` (Series = Forecast); the Forecast page draws the 80% range as error bars (band) on `Forecast revenue` with `High`/`Low` as bounds.

Formats live in the semantic model (errors as %, revenue as currency, markdown effect to 3 decimals), so cards, tables and hover tooltips all pick them up. The Models page has an error-by-store matrix (shaded: darker = worse) and a store-type drop-down; the Forecast page has a dashed constant line at 2012-11-02 where the forecast starts. Each page has a phone layout (Optimize page for mobile).

## Semantic model

Star schema: fact tables `Series` and `ModelError`, dimensions `Stores` and `Calendar`. All three new objects below are calculated tables, so refresh the model after re-uploading the data.

| Table | Definition | Relationship |
| --- | --- | --- |
| `Calendar` | `ADDCOLUMNS(CALENDAR(DATE(2010,1,1), DATE(2013,12,31)), "Year", ..., "Month", FORMAT([Date],"MMM yyyy"), "Month Number", ..., "Quarter", ...)`; marked as date table, `Month` sorted by `Month Number` | `Calendar[Date]` to `Series[Date]` (one to many) |
| `Stores` | `DISTINCT(SELECTCOLUMNS(ModelError, "Store", [Store], "Store name", [Store name], "Store Type", [Type]))` | `Stores[Store]` to `Series[Store]` and `ModelError[Store]` |
| `_Measures` | Holds the measures below (display folder `Measures`); its `Dummy` column is hidden | none |

Measures (all in `_Measures`):

| Measure | What it does |
| --- | --- |
| `Revenue LY` | `Actual revenue` shifted back 364 days (weekly data falls on Fridays, so weeks line up) |
| `Avg Weekly Revenue`, `Avg Weekly Revenue LY` | Revenue per history week, so months with 4 or 5 Fridays compare fairly |
| `Revenue YoY %` | Change in `Avg Weekly Revenue` vs last year; blank where there is no actual revenue |
| `Revenue YoY % (total)` | Same but on total revenue; noisy by month, fine by week |
| `Revenue YTD` | `TOTALYTD` when a date is in context; unfiltered, 2012 up to the last history week |
| `Avg Weekly Revenue per Store` | Average of `Value` over History rows |
| `Prophet MAPE`, `Baseline MAPE` | Average holdout error for Prophet and `Seasonal baseline` |
| `Error Reduction vs Baseline` | (Baseline - Prophet) / Baseline |
| `Prophet Win Rate` | Stores where Prophet won / stores |
| `Forecast Range Width %` | (High - Low) / `Forecast revenue` on Forecast rows |
| `Markdown -30% Revenue`, `Markdown -30% Effect %` | Revenue under the -30% scenario and its difference from `Forecast revenue` |

Checks against the `KPI` sheet: `Prophet MAPE` 4.4%, `Baseline MAPE` 5.5%, `Prophet Win Rate` x 45 = 30 stores.

Report additions: a **Trends** page (monthly `Revenue YoY %` line, `Revenue YTD` card, store matrix of `Avg Weekly Revenue per Store`); an `Error Reduction vs Baseline` card on Models; `Forecast Range Width %` on Forecast; `Markdown -30% Effect %` on Markdown; the Holdout line axis uses `Calendar[Date]`. New cards are copies of the styled cards, so keep them as Card visuals (a stray visual-type change to KPI hides the value).

## Refreshing the data

All three queries read `My files/powerbi.xlsx` in OneDrive (`https://purdue0-my.sharepoint.com/personal/vit_purdue_edu/Documents/powerbi.xlsx`). To update the report:

1. Run `python scripts/build_powerbi.py` (or `bash run_all.sh`).
2. Upload the new `data/powerbi.xlsx` to OneDrive My files, replacing the old one (keep the name).
3. In Power BI, open the Walmart Forecast semantic model and click Refresh.

Saved slicer selections persist: clear the Store drop-down before saving or the report opens filtered to one store.
