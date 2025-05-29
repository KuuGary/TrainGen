# utils/parser.py
import re
import json

def extract_json_block(text):
    match = re.search(r'\{[\s\S]+\}', text)
    if match:
        raw_json = match.group(0)
        raw_json = re.sub(r'(": .*?)"(.*?)"(.*?")', r'\1\"\2\"\3', raw_json)
        raw_json = re.sub(r",\s*([}\]])", r"\1", raw_json)
        raw_json = raw_json.encode("utf-8", errors="ignore").decode("utf-8")
        return json.loads(raw_json)
    raise ValueError("No valid JSON block found")

