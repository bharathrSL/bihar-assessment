"""Streamlit human-review application for a completed run."""
import argparse, json
from pathlib import Path
import streamlit as st
from core.learning.correction_store import CorrectionStore
def main() -> None:
    parser=argparse.ArgumentParser(add_help=False); parser.add_argument("--run-dir",required=True); args,_=parser.parse_known_args()
    root=Path(args.run_dir); state=json.loads((root/"processing_state.json").read_text(encoding="utf-8")); records=list(state["completed"].values()); st.title("21stCenturyTool review")
    if not records: st.info("No processed questionnaires."); return
    record=next(r for r in records if st.selectbox("Questionnaire",[x["record_id"] for x in records])==r["record_id"])
    qid=st.selectbox("Question",[q for q,a in record["answers"].items() if a["review_required"]] or list(record["answers"]))
    answer=record["answers"][qid]; crop=root/"crops"/record["record_id"]/f"{qid}.png"
    if crop.exists(): st.image(str(crop),caption=f"{qid} crop")
    st.json(answer); value=st.text_input("Corrected answer", "; ".join(answer["selected_codes"]) or answer["answer_text"])
    if st.button("Save correction"):
        CorrectionStore(root/"learning").save({"record_id":record["record_id"],"question_id":qid,"value":value,"crop":str(crop),"ai_answer":answer})
        st.success("Correction stored for retrieval and gold-standard dataset building.")
if __name__ == "__main__": main()
