"""Compute dashboard metrics from processed records."""
from core.models import Record
class Dashboard:
    def metrics(self, records: list[Record], elapsed_seconds: float=0, estimated_cost: float=0) -> dict:
        total=len(records)
        return {"questionnaires":total,"average_confidence":sum(r.confidence for r in records)/total if total else 0,
                "review_rate":sum(r.review for r in records)/total if total else 0,"estimated_cost":estimated_cost,
                "processing_speed":total/elapsed_seconds*60 if elapsed_seconds else 0}
