# FP&A variance explorer

## Open the completed analysis

Open `report/variance_report.html` in a browser. It works offline and does not require Python to view.

Choose a month range, cost center, account group, and reporting level. Click a variance row to inspect the bridge, observed exceptions, vendors and transactions. Export the current table or transaction selection as CSV.

The **Period** selector supports Full year, Specific month, Specific quarter, H1 (January–June), H2 (July–December), and a Custom range with inclusive start/end months. Only the relevant month or quarter controls are shown. All cards, rankings, bridges, detail filters and transaction exports use that selection. Periods follow calendar year 2026.

## Forecast comparisons

Use **Comparison** to choose:

- **Actual vs Budget** — the original comparison and operational variance bridge.
- **Actual vs Forecast** — choose Q1, Q2 or Q3 in **Forecast snapshot**.
- **Actual vs Budget and Forecast** — both variances side by side, plus forecast versus budget. Ranking order and the minimum variance threshold use Actual vs Budget in this mode.
- **Forecast vs Budget** — shows revisions between the selected snapshot and the original plan.

Each snapshot has 3,120 monthly rows in the workbook's **Forecasts** table:

| Snapshot | As of | Closed actuals | Estimates |
|---|---|---|---|
| Q1 forecast | March 31, 2026 | January–March | April–December |
| Q2 forecast | June 30, 2026 | January–June | July–December |
| Q3 forecast | September 30, 2026 | January–September | October–December |

Closed-month amounts equal actual postings at the snapshot, so Actual vs Forecast is zero in those months by construction. Estimates blend budget with recent observed usage/rates and synthetic planning adjustments. Future actuals and the Scenario Guide are excluded from generation. These are full-year outlook snapshots, not independent predictions of already closed months.

Forecast vs Budget is split into closed actual variances and remaining estimate revisions. Actual vs Forecast is reconciled as Actual vs Budget minus Forecast vs Budget. Forecast supporting rows include period type, vendor, assumption, and all three amounts. Detail filters and CSV exports apply to the selected snapshot and period.

The **Forecast Summary** sheet provides full-year totals. The report folder also includes `forecast_comparisons_monthly.csv`. Forecast snapshots are fixed workbook inputs: changing closed actuals requires an intentional corresponding update to snapshot rows; mismatches stop analysis. `generate_forecasts.py` can reproduce synthetic records as JSON but does not edit the workbook.

The ranking includes a total row. A minimum absolute variance combines smaller rows into **Other expenses**, preserving actual, budget and variance totals. The reporting level appears below the heading. Detail filters for cost center, account group, account and Budget ID narrow the Other row without changing the ranking totals. Other supports the same drilldown and export as individual rows. Search restricts the table total to matching rows; clear search to reconcile to the summary cards. The CSV includes Other and a separate TOTAL row, so exclude TOTAL when summing the exported detail rows.

Detail filters are available for every ranking row, including individual account groups. They cascade in this order: Cost center → Account group → Account → Budget ID. Options stay within the selected ranking row and upstream selections. Changing a parent clears any incompatible account or Budget ID selection. Reset detail filters restores the full selected row.

## Rerun after changing the workbook

Use Python 3.10 or later. From this folder:

On this Windows computer, double-click `Run analysis.cmd` to regenerate and open the report using the available Python environment. On other computers, install the packages below first.

```text
python -m pip install -r requirements.txt
python analyze.py Synthetic_FPA_2026_Grouped.xlsx --open
```

To analyze another workbook with the same columns:

```text
python analyze.py "path/to/workbook.xlsx" --out "report_new" --open
```

The original workbook is never modified. The script overwrites files in the selected report folder. Output includes the interactive HTML report, monthly ID bridges, annual group/account/cost-center/ID CSV summaries, and validation results.

## Interpreting the results

- Positive expense variance is unfavorable. Negative is favorable.
- Actuals use posting month. Service month is used to separate timing from service activity.
- The bridge reconciles to cents: signed-unit volume + rate/vendor mix + unbudgeted service spend + posting timing = actual minus budget.
- Volume and rate calculations are performed separately for each Budget ID/month before aggregation. Units are never combined across unrelated accounts to infer a shared price.
- Credits and accrual reversals affect net units. They are flagged, but the app does not assert a business cause without supporting evidence.
- A planned month with no posting is an exception, not proof of cancellation or a missing invoice.
- Explanations use Register, Budget, Actuals and Forecasts. The Scenario Guide is used solely by the test suite to check planted outcomes.
- Budget and actual amounts are original inputs. The report is a snapshot; rerun to reflect edits. Group labels must agree across source sheets and the register.

## Amount display

Use **Dollars**, **Thousands**, or **Millions** to change monetary displays throughout the report. Dollars use standard whole-dollar rounding; thousands and millions show one decimal with K or M. For example, $125,600 displays as $125.6K or $0.1M. Small amounts can display as zero in scaled views.

The variance threshold remains in dollars. Calculations and CSV exports retain full-precision USD amounts, so rounded rows may not sum exactly to the displayed total. Bridge cards show the starting amount, signed changes, and ending amount; arrows indicate the direction of reconciliation.

## Supported input contract

This version is tailored to the supplied 2026 USD workbook, including the Account Group fields. It requires a unique register, all 12 budget months per ID (including explicit zero budgets), one budget line per ID/month, unique transaction IDs, and consistent dimensions. Schema/data errors stop generation rather than produce misleading results. Future-year or multi-currency workbooks require an extension.

## Tests

```text
python -m unittest -v test_analysis.py test_forecasts.py
```

Tests check source totals, every monthly bridge, planted rate/volume/timing/vendor outcomes, zero-actual and unbudgeted cases, and rejection of duplicate/unknown keys.

