#!/usr/bin/env python
import sys, json, pandas as pd, pathlib

if len(sys.argv) < 3:
    print("Usage: json_to_csv.py input.json output.csv")
    sys.exit(1)

inp = pathlib.Path(sys.argv[1])
outp = pathlib.Path(sys.argv[2])

with open(inp, "r", encoding="utf-8") as f:
    data = json.load(f)

# minimal validation and normalization
rows = []
seen = set()
for item in data:
    rid = int(item["id"])
    if rid in seen: 
        continue
    seen.add(rid)
    rows.append({
        "id": rid,
        "category": str(item["category"]).strip(),
        "tamil": str(item["tamil"]).strip(),
        "translit": str(item["translit"]).strip(),
        "english": str(item["english"]).strip(),
    })

df = pd.DataFrame(rows, columns=["id","category","tamil","translit","english"])
outp.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(outp, index=False, encoding="utf-8")
print(f"Wrote {len(df)} rows to {outp}")
