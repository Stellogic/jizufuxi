from __future__ import annotations

import json
import re
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) != 4:
    raise SystemExit("usage: print_page_range.py <json-file> <start-page> <end-page>")

path = Path(sys.argv[1])
start = int(sys.argv[2])
end = int(sys.argv[3])
data = json.loads(path.read_text(encoding="utf-8"))

for page in data["pages"]:
    page_no = page["page"]
    if not (start <= page_no <= end):
        continue
    text = re.sub(r"\s+", " ", page["text"]).strip()
    if not text:
        continue
    print(f"P{page_no:>3}: {text[:500]}")
