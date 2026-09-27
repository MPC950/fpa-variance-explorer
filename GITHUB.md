# GitHub repository and Pages setup

Prepared locally. No repository or published website has been created.

Suggested repository name: `fpa-variance-explorer`.

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

## When publication is authorized

1. In GitHub Desktop, use **File > Add local repository**, choose `C:\FPA Python`,
   and use the option to create a repository here if prompted. Keep the repository
   root at `C:\FPA Python` rather than making a nested project folder.
2. Review the changed-file list. Commit the app, synthetic workbook, tests, scripts,
   documentation, `.gitignore`, and `.github/workflows/pages.yml`.
3. Publish the repository to the chosen GitHub account as `fpa-variance-explorer`.
   A public repository supports Pages on GitHub Free. Private repository Pages
   depends on your plan; a private source repository does not by itself make the
   Pages website private.
4. On GitHub, open **Settings > Pages** and select **GitHub Actions** as the source.
5. Open **Actions > Publish FP&A report > Run workflow** on the default branch.
   Tests must pass before deployment. The workflow runs only when manually started.
6. Copy the deployed URL from the workflow or Pages settings. Normally it is
   `https://YOUR-USERNAME.github.io/fpa-variance-explorer/`.

For updates, commit and push changes, then manually run the workflow again.
GitHub Desktop handles the Git sign-in; a separate command-line sign-in is not
required for these steps.

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
