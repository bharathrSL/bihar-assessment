"""Question-wise accuracy benchmark against human corrections."""
from collections import defaultdict
class Benchmark:
    def score(self, predictions: list[dict], gold: list[dict]) -> dict:
        lookup={(x["record_id"],x["question_id"]):x.get("value") for x in gold}; counts=defaultdict(lambda:[0,0])
        for item in predictions:
            key=(item["record_id"],item["question_id"])
            if key in lookup:
                counts[item["question_id"]][1]+=1; counts[item["question_id"]][0]+=item.get("value")==lookup[key]
        return {q:{"correct":v[0],"total":v[1],"accuracy":v[0]/v[1] if v[1] else None} for q,v in counts.items()}
