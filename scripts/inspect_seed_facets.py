"""Inspect seed standards facets."""
import json

with open("data/processed/standards_dump.json", "r", encoding="utf-8") as f:
    dump = json.load(f)

stds = dump["standards"]
has_mats = sum(1 for s in stds if s.get("materials"))
has_params = sum(1 for s in stds if s.get("technical_parameters"))
has_app = sum(1 for s in stds if s.get("application"))

print(f"Total standards: {len(stds)}")
print(f"Standards with materials: {has_mats}")
print(f"Standards with technical_parameters: {has_params}")
print(f"Standards with application: {has_app}")

print("\n--- STANDARDS WITH TECHNICAL_PARAMETERS ---")
for s in stds:
    if s.get("technical_parameters"):
        print(f"{s['is_number']}: Title='{s['title']}', Params={s['technical_parameters']}")

print("\n--- STANDARDS WITH MATERIALS ---")
for s in stds:
    if s.get("materials"):
        print(f"{s['is_number']}: Title='{s['title']}', Mats={s['materials']}")

print("\n--- SECTORS AND THEIR STANDARDS ---")
sectors = {}
for s in stds:
    sectors.setdefault(s["sector"], []).append(s)

for sec, items in sorted(sectors.items()):
    print(f"\nSector: {sec} ({len(items)} items)")
    for it in items:
        print(f"  {it['is_number']}: {it['title']}")
