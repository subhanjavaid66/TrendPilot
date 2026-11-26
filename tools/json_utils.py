import json
import re


def extract_json(text):
    """Pull the first JSON object/array out of an LLM response. Returns None on failure."""
    if not text:
        return None

    text = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None