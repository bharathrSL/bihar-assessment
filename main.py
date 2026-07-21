"""Command-line entry point for fixed-booklet batch processing."""
from __future__ import annotations
import argparse, json, shutil, time
import os
from pathlib import Path
from dotenv import load_dotenv
from core.batch.batch_processor import BatchProcessor
from core.excel.excel_writer import ExcelWriter
from core.analytics.dashboard import Dashboard
from core.merger.json_merger import JsonMerger
def config_path() -> Path: return Path(__file__).parent / "config"
def main() -> None:
    parser=argparse.ArgumentParser(description="21stCenturyTool V2")
    sub=parser.add_subparsers(dest="command",required=True)
    process=sub.add_parser("process"); process.add_argument("--input",required=True); process.add_argument("--output",required=True)
    estimate=sub.add_parser("estimate"); estimate.add_argument("--input",required=True); estimate.add_argument("--output",default=".")
    args=parser.parse_args()
    load_dotenv()
    if args.command == "process" and not os.getenv("GEMINI_API_KEY"):
        parser.error("GEMINI_API_KEY is missing. Create .env from .env.example or set it in this terminal before processing.")
    processor=BatchProcessor(config_path(),args.output); pdfs=list(Path(args.input).glob("*.pdf"))
    if args.command=="estimate": print(json.dumps(processor.estimate(pdfs),indent=2)); return
    started=time.monotonic(); records=JsonMerger().merge(processor.process_folder(args.input))
    workbook=ExcelWriter().write(records,Path(args.output)/processor.settings["output_workbook"])
    metrics=Dashboard().metrics(records,time.monotonic()-started)
    (Path(args.output)/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    print(f"Processed {len(records)} questionnaires. Workbook: {workbook}")
if __name__ == "__main__": main()
