"""Merge per-PDF records with duplicate record protection."""
from core.models import Record
class JsonMerger:
    def merge(self, records: list[Record]) -> list[Record]:
        seen=set(); result=[]
        for record in records:
            if record.record_id not in seen: seen.add(record.record_id); result.append(record)
        return result
