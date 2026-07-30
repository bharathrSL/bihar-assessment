"""Command-line entry point for fixed-booklet batch processing."""
from __future__ import annotations
import argparse, json, shutil, time
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from core.batch.batch_processor import BatchProcessor
from core.excel.excel_writer import ExcelWriter
from core.analytics.dashboard import Dashboard
from core.merger.json_merger import JsonMerger

def config_path() -> Path: return Path(__file__).parent / "config"

def openrouter_credentials_present() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_TOKEN") or
                any(os.getenv(f"OPENROUTER_TOKEN{i}") for i in range(1, 100)))

def main() -> None:

    parser=argparse.ArgumentParser(description="21stCenturyTool V2")
    sub=parser.add_subparsers(dest="command",required=True)
    process=sub.add_parser("process"); process.add_argument("--input",required=True); process.add_argument("--output",required=True)
    estimate=sub.add_parser("estimate"); estimate.add_argument("--input",required=True); estimate.add_argument("--output",default=".")
    args=parser.parse_args()
    load_dotenv()

    if args.command == "process" and not openrouter_credentials_present():
        parser.error("OPENROUTER_API_KEY is missing. Set it in .env or in this terminal before processing.")
    print("processing============================================")


    model = os.getenv("OPENROUTER_MODEL", "default").split("/")[-1]

    run_name = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{model}"

    run_output = Path(args.output) / run_name
    run_output.mkdir(parents=True, exist_ok=True)


    processor=BatchProcessor(config_path(),run_output); pdfs=list(Path(args.input).glob("*.pdf"))

    if args.command=="estimate": print(json.dumps(processor.estimate(pdfs),indent=2)); return

    started=time.monotonic(); records=JsonMerger().merge(processor.process_folder(args.input))
    print("Procesed==============================================")
    workbook=ExcelWriter().write(records,run_output/processor.settings["output_workbook"])

    metrics=Dashboard().metrics(records,time.monotonic()-started)

    (run_output/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    print(f"Processed {len(records)} questionnaires. Workbook: {workbook}")
if __name__ == "__main__": main()
