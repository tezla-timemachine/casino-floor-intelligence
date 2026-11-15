"""Connection test: one image to Claude, answered in a fixed format (structured output).

    .venv/bin/python scripts/test_claude.py <image path>

Reads the API key from .env (never printed). Prints the answer, the time taken, the tokens used and the cost.
"""
from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"
PRICE_IN, PRICE_OUT = 4.00 / 1e6, 20.00 / 1e6   # $ per token, Claude Opus 5.5

SCHEMA = {
    "type": "object",
    "properties": {
        "people_count": {"type": "integer", "description": "People visible in the image, including partly visible ones"},
        "visible_floor_objects": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "note": {"type": "string", "description": "One sentence on anything that made counting hard"},
    },
    "required": ["people_count", "visible_floor_objects", "confidence", "note"],
    "additionalProperties": False,
}


def main(image_path: str) -> None:
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    data = base64.standard_b64encode(Path(image_path).read_bytes()).decode()
    start = time.time()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=2000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",                      # if Claude declines, the API retries on a fallback model
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}},
            {"type": "text", "text": "This is a photo of a casino floor. Count the people visible and list the casino floor objects "
                                     "you can see. Do not describe or identify any individual."},
        ]}],
    )
    seconds = time.time() - start
    if response.stop_reason == "refusal":
        print("Claude declined:", response.stop_details)
        return
    answer = json.loads(next(b.text for b in response.content if b.type == "text"))
    u = response.usage
    cost = u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT
    print(json.dumps(answer, indent=2))
    print(f"model {response.model} | {seconds:.1f} s | {u.input_tokens} tokens in, {u.output_tokens} out | ${cost:.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
