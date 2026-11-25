# Beyond Frequent Co-Purchases

A reproducible AIAA3111 Group 11 project on temporal stability of retail association rules.

**Team:** Chi Kit WONG (50012338), Yuxuan OUYANG (50013526), Zhicheng SUN (50012546).

The selected 71-rule cohort has **79.2% mean monthly retention** in August-November 2011; **46 rules persist in all four months**. These are descriptive results under declared thresholds, not a prediction of retail revenue or a causal claim. Restricting the evaluation population to orders with a recorded CustomerID reduces retention to 64.8%; excluding baskets above 100 products reduces it to 62.3%.

## Run locally

Python 3.11 was used. The computations run on CPU; no GPU, server or paid API is required. In PowerShell, from this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe run.py all
```

On Linux/macOS, from this repository:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pytest -q
.venv/bin/python run.py all
```

The source download requires internet access the first time. Subsequent runs verify the existing workbook's SHA-256. Pickle files are **local generated caches**; never replace them with untrusted downloaded pickle files.

The individual stages are available as `download`, `prepare`, `pilot`, `experiment`, `supplement`, `figures`, and `verify`. `all` rebuilds the analysis from the verified raw workbook, including the supplements, figures and verification. The optional `pilot` uses the first 2,000 discovery invoices solely as a feasibility check and is not the reported benchmark. Run it after `prepare`.

```powershell
.\.venv\Scripts\python.exe run.py prepare
.\.venv\Scripts\python.exe run.py pilot
.\.venv\Scripts\python.exe run.py experiment
.\.venv\Scripts\python.exe run.py supplement
.\.venv\Scripts\python.exe run.py figures
.\.venv\Scripts\python.exe run.py verify
```

The measured benchmark workers used under 160 MiB each; mining took approximately 0.3-5.7 seconds per run in the recorded experiment. This is **worker-process memory**, not a measurement of the entire cleaning pipeline. The core experiment took about 71 seconds on the local Ryzen 9 7940H. Timings will vary. The runner enforces a 12 GiB worker limit and a 600-second per-run timeout. Lower support or longer itemsets can be substantially more expensive.

## Data and methodology

- Source: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Daqing Chen (2015), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0.
- The official download contains 541,909 line items, not that many independent orders. The workbook and its checksum are preserved locally; `data/source_manifest.json` records provenance.
- Sequential cleaning produces 522,537 positive-sales lines and 19,773 baskets across all countries; the primary UK population has 17,901 baskets. Cancellation/return rows are removed, but purchases are not netted against later returns.
- Missing CustomerID does not invalidate an order-level basket. Codes, rather than descriptions, identify products. Valid alphanumeric codes and singleton baskets are preserved.
- Discovery: December 2010-May 2011 (7,365 UK orders). Validation: June-July (2,696). Test: August-November (7,096). December 2011 is incomplete and kept only as a supplement.
- Apriori (`low_memory=True`) and FP-Growth use identical Boolean inputs and maximum itemset length 3. Only single-item consequents are generated. Exact bounded itemsets and integer support counts must agree.
- Discovery grid: support 0.5%, 1%, 2%; confidence 30%, 50%, 70%; lift at least 1.2.
- Common monthly evaluation: support at least 0.5%, confidence at least 50%, lift at least 1.2, antecedent count at least 20.
- Selection: maximum mean validation retention, requiring at least 20 discovery rules. Tie-breaks are documented in `configs/experiment.json`. The selected setting is support 2%, confidence 50%.
- A fixed rule cohort is evaluated in every month. Missing and underpowered rules remain in the retention denominator; coverage and conditional retention are reported separately.
- The 14-rule configuration has 100% observed test retention but fails the primary rule-count floor. This trade-off is disclosed, not hidden. Post-hoc diagnostics are labeled in `results/supplemental_protocol.json`.

The detailed experimental definitions and limitations are in [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md).

## Repository contents

| Path | Purpose |
|---|---|
| `retail_rules/` | Download, cleaning, mining, evaluation, benchmarks, figures and verification |
| `configs/` | Experiment and team metadata |
| `tests/` | Independent toy-data and boundary-case tests |
| `data/source_manifest.json` | Source URL, attribution and checksum |
| `data/raw/`, `data/processed/` | Locally generated, ignored data and caches |
| `results/tables/` | Inspectable calculations and per-rule evidence |
| `results/figures/` | PNG and editable SVG figures |
| `results/protocol.json`, `results/selection.json` | Configuration and pre-test selection records |
| `results/verification.json` | Scope and result of independent numerical checks |
| `docs/PRESENTATION_NOTES.md` | Chinese explanation, English pitch and defense questions |
| `artifacts/Poster.pdf` | V04.0 English vector print poster, 800 x 1000 mm portrait |
| `artifacts/Poster_preview.png` | Screen preview of the V04.0 poster |
| `artifacts/Poster.svg` | Editable vector poster |
| `artifacts/Poster_source.zip` | Current poster source package and bilingual talk with Q&A |
| `poster/` | Current drawing source, rendering engine, data snapshot and build instructions |
| [Bilingual presentation script](poster/Presentation_Script_EN_ZH.md) | Three speakers, three minutes of English, two minutes of Q&A, with Chinese rehearsal text |
| `scripts/` | Optional document build and submission packaging tools |

## Report and submission

The [report repository](https://github.com/Chikit-WONG/AIAA3111-Introduction_to_Data_Mining-Final_Project-Report) contains the editable English `Report.docx`, its print PDF and the collaborative Overleaf manuscript. The Word file uses the teaching team's v2 template. For changes agreed in Overleaf, update the Word file before exporting the PDF. The experiment's `export-report` stage refreshes the evidence, tables and figures in the report repository. The editable manuscripts are maintained by the team.

From this repository on Windows with Microsoft Word installed, rebuild the final and the Canvas archive with the following commands.

```powershell
.\scripts\build_report.ps1
.\.venv\Scripts\python.exe scripts/check_report_layout.py
.\.venv\Scripts\python.exe scripts/package_submission.py
```

The layout check measures the gap below the final main-text line, checks the A4 page size and verifies that Disclosures begins on page 11. The source file, PDF and archive are versioned. The ZIP includes the same PDF at its root, `report_source/Report.docx`, the analysis code, the README, and the public data download instructions and checksum. In an extracted ZIP, pass `-ReportDirectory .\report_source` to the PowerShell builder and `--report-dir report_source` to the layout checker or packager. Exporting in the extracted copy places the PDF next to the Word file.

The separate LaTeX preview is available through `scripts/build_report.ps1 -Overleaf`, after running `python scripts/bootstrap_tex.py` once. That preview goes to `build/main.pdf` in the report repository. With the Tectonic cache populated, add `-Offline` for an offline LaTeX preview.

One member submits [Group_11_Project.zip](dist/Group_11_Project.zip) by **11 December 2026, 23:59 Beijing time**. The main-text limit is 6–10 pages including figures and tables. References, Disclosures and Appendix are excluded. The teaching team does not require a poster in this ZIP.

The V04.0 print poster is **800 x 1000 mm portrait**. Print `artifacts/Poster.pdf` at actual size. Rebuild it on Windows with `python -m pip install -r poster/requirements-render.txt` and `python scripts/build_poster.py`. On other systems, point `POSTER_FONT_DIR` to the same font files. The builder reads the saved results and draws each figure as editable vectors.

The source package includes the build files, editable SVG, print PDF, preview and one bilingual speaking file for the five-minute team slot. The earlier Chinese draft remains in the repository as background. See the [poster build instructions](poster/README.md) and [design notes](docs/POSTER_DESIGN.md).

The course prohibits directly submitting AI-generated work and requires AIGC disclosure. The Word report records assistance from ChatGPT, OpenAI Codex, Antigravity Gemini and Cursor Grok, including the English manuscript's drafting and review. The team has confirmed that there were no external collaborators. Team members remain responsible for reviewing, revising and understanding the work they submit. See [the team review notes](docs/TEAM_REVIEW.md).
