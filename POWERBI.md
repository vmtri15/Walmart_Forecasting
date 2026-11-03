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

Built in Power BI on the web as the **Walmart Forecast** report (My workspace > Walmart), pages Models, Holdout, Forecast, Markdown. Win is a Power Query column: `if [Model] = [Best_Model] then 1 else 0`. To refresh, rerun the script and re-upload `powerbi.xlsx`. Colors and card borders come from `powerbi_theme.json` (Design > Import theme); the store and store-type drop-downs are synced across the Holdout, Forecast and Markdown pages. The model has two DAX measures, `Actual revenue` (Series = History) and `Forecast revenue` (Series = Forecast); the Forecast page draws the 80% range as error bars (band) on `Forecast revenue` with `High`/`Low` as bounds.

Formats live in the semantic model (errors as %, revenue as currency, markdown effect to 3 decimals), so cards, tables and hover tooltips all pick them up. The Models page has an error-by-store matrix (shaded: darker = worse) and a store-type drop-down; the Forecast page has a dashed constant line at 2012-11-02 where the forecast starts. Each page has a phone layout (Optimize page for mobile).

## One-click refresh (not set up yet)

The model currently reads a copy Power BI made at upload (`Apps/Microsoft Power Query/Uploaded Files/powerbi 1.xlsx`), which OneDrive does not let you replace. To make refresh one click:

1. Upload `data/powerbi.xlsx` to a normal OneDrive folder, e.g. `Documents/Walmart/`.
2. In the semantic model: Transform data > each query's Source step > Link to file > Browse OneDrive > pick that file.
3. Afterwards, rerun `python scripts/build_powerbi.py`, upload the new file over the old one, and click Refresh.

Saved slicer selections persist: clear the Store drop-down before saving or the report opens filtered to one store.
