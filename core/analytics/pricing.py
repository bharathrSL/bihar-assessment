from pathlib import Path
import yaml

_PRICING = None


def load_pricing():
    global _PRICING

    if _PRICING is None:
        pricing_file = Path(__file__).parents[2] / "config" / "model_pricing.yaml"

        with open(pricing_file, "r") as f:
            _PRICING = yaml.safe_load(f)

    return _PRICING


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = load_pricing()

    if model not in pricing:
        return 0.0

    model_price = pricing[model]

    input_cost = (
        prompt_tokens / 1_000_000
    ) * model_price["input"]

    output_cost = (
        completion_tokens / 1_000_000
    ) * model_price["output"]

    return round(input_cost + output_cost, 6)