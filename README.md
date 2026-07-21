# 21stCenturyTool V2

Fixed-layout, AI-assisted questionnaire digitization for one 34-question booklet.

## Booklet scan format

The supplied questionnaire is a 12-page physical booklet scanned as six
two-page spreads. Keep `reference_master.pdf` one directory above this project
folder (`D:\21stCenturyTool\reference_master.pdf`). The processor splits every
incoming six-page PDF into twelve logical pages in this order: `12|1`, `2|3`,
`4|5`, `6|7`, `8|9`, and `10|11`. It then aligns each logical page to the
master before generating answer crops.

## Install and run

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY = "..." # optional; deterministic local extraction still runs
python main.py process --input C:\scans --output C:\results
streamlit run core/review/streamlit_review.py -- --run-dir C:\results
```

The calibrated answer regions are saved once in `config/pages.json`; they are
not edited for individual student PDFs. The system deliberately supports only
this format. It records intermediate crops and JSON audit records in the output
directory and can resume completed PDFs.
