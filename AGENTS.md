# FP&A project

- Use the root README for entry points and file ownership. Current code and input data live in `app/`.
- Edit `app/report_template.html`, then regenerate the HTML with `app/analyze.py`; avoid edits solely to the generated report.
- The workbook in `app/` is the current input. `archive/` contains historical artifacts, not alternate editable masters.
- Preserve the user-supplied data-hygiene reference. Apply its guidance selectively; keep changes proportional.
- After changes, run the relevant analysis or report tests. Package updates with `scripts/package.py` when updating the downloadable app.
- Generated reports, caches, diagnostics and distribution ZIPs are excluded from source control. Never put real financial data or secrets in version control without explicit authorization.

## Delegation and design review

- Delegate substantive project assignments to subagents, choosing available models appropriate to each assignment's complexity and specialty. The lead agent coordinates their work, reviews results, and verifies the integrated outcome.
- Use Claude for design elements and UI design. Have Claude produce mockups for the user to review before implementing design changes in the app.
- Keep proposed designs separate from the working app until the user approves the mockups. After approval, implement the approved design and run the relevant checks.
- If Claude is unavailable, explain the limitation and ask the user how to proceed with design work. Do not silently substitute another model for Claude.
- Use Claude only through the user's existing Pro subscription and its included usage. Do not use API billing, paid extra usage, credits, token purchases, upgrades, or other additional charges. Stop if included usage is exhausted or the billing route cannot be verified.
- The user confirmed Usage credits / Extra usage is off on September 27, 2026. Keep it off; do not enable paid fallback. Verify subscription authentication before delegated Claude runs.
