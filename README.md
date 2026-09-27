# FP&A variance explorer

## Open or run

- **Open report.cmd** opens the existing interactive report in your browser.
- **Run analysis.cmd** regenerates the report from the workbook and opens it.
- [App instructions](app/README.md) explain Python setup, comparisons, filters and tests.
- Repository: [MPC950/fpa-variance-explorer](https://github.com/MPC950/fpa-variance-explorer).
- Live report: [Open FP&A variance explorer](https://mpc950.github.io/fpa-variance-explorer/) on desktop or phone.
- [GitHub and Pages instructions](GITHUB.md) explain how to publish updates.

## Project layout and ownership

| Location | Purpose |
|---|---|
| `app/analyze.py` | Current Python analysis code |
| `app/report_template.html` | Current interactive report template; edit this to change the view |
| `app/Synthetic_FPA_2026_Grouped.xlsx` | Current input workbook, including budget, actuals and three quarterly forecasts |
| `app/test_*.py`, `app/test_ranking.mjs` | Analysis and report behavior tests |
| `app/report/` | Generated HTML, CSV exports and validation results; regenerate from the app |
| `dist/FPA_Variance_Explorer.zip` | Shareable app snapshot; rebuild after changing the app |
| `archive/` | Earlier workbooks, builder scripts, previews, caches, diagnostics and migration evidence; historical reference, not current inputs |
| `AI-First-Repository-Data-Hygiene.md` | User-supplied design reference, retained unchanged |

The current input workbook and app source are authoritative. Reports and ZIP packages are derived snapshots. Historical builder scripts may retain their original relative paths and should not be run against current data without adapting them. They are retained to explain how the synthetic workbook was assembled.

The migration manifest records every transferred file's original path, destination, size and SHA256 hash at transfer. External shared runtime dependencies were not copied. Python and Node remain installed dependencies, not part of this project.

## Verification

From the `app` folder, using an environment with `requirements.txt` installed:

```text
python -m unittest -v test_analysis.py test_forecasts.py
python analyze.py
node test_ranking.mjs
```

Run relevant tests when changing calculations or filter behavior. The app works offline and currently uses synthetic 2026 USD data. A report contains all underlying data; filtering does not remove it from a shared file.
