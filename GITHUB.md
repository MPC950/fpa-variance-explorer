# GitHub repository and Pages

Repository: [MPC950/fpa-variance-explorer](https://github.com/MPC950/fpa-variance-explorer)

Live report: [Open FP&A variance explorer](https://mpc950.github.io/fpa-variance-explorer/).
The first deployment passed on September 27, 2026. The public report and period
filters were verified after deployment.

The repository holds the Python app, template, tests, and synthetic workbook.
Pages serves the generated interactive report. Viewers can use its filters on
desktop or phone without installing Python. Refreshing the published data requires
rebuilding and deploying the report.

## Publication boundary

The report embeds the underlying dataset. Filters do not hide that data from
someone who downloads the page. Only the synthetic demonstration workbook is
intended for this repository and site. Review any replacement workbook before
committing or publishing it.

Generated reports, archives, ZIPs, local environment files, and the supplied
data-hygiene reference are excluded by `.gitignore`. The reference stays on disk.

## Publish an update

1. In GitHub Desktop, review and commit the intended project changes, then push them.
2. On GitHub, open **Actions > Publish FP&A report > Run workflow** and start it
   from the default branch. The workflow runs tests before building and deploying.
3. Check the run completes successfully, then open the Pages address above.

The workflow starts only when manually run. GitHub Desktop handles Git sign-in.

## Local verification

Use Python 3.12 or later with `app/requirements.txt` installed, and Node.js available.
Dependencies are pinned to the versions used for local verification.

```text
python scripts/build_pages.py
cd app
python -m unittest -v test_analysis.py test_forecasts.py
node test_ranking.mjs
```

The local site is `_site/index.html`; creating it does not upload anything.
The workflow uploads only `_site/`, not the project folder or workbook file.

References: [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
