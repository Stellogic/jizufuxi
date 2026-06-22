from __future__ import annotations

import json
import re
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")

for path in Path("tmp/pdfs").glob("计算机组成原理习题解答*.json"):
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"\n## {data['file']}")
    for page in data["pages"]:
        text = re.sub(r"\s+", " ", page["text"]).strip()
        if not text:
            continue
        lead = text[:100]
        if any(key in lead for key in ["学习要求", "习题", "补充题目", "解答"]) or re.match(r"第.章", lead):
            print(f"P{page['page']:>3}: {text[:220]}")
