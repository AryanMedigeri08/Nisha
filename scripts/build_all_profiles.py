"""
Merge and validate domain profiles from part 1, part 2, and part 3.
Outputs: data/processed/standards_profiles.json
"""
import json
import sys
from pathlib import Path

# Add scripts directory to path to import parts
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from profiles_part1 import PART1_PROFILES
from profiles_part2 import PART2_PROFILES
from profiles_part3 import PART3_PROFILES

dump_path = Path("data/processed/standards_dump.json")
if not dump_path.exists():
    raise FileNotFoundError(f"{dump_path} does not exist. Run ingest_seed.py first.")

with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

db_standards = {s["is_number"]: s for s in dump["standards"]}
print(f"Loaded {len(db_standards)} standards from database dump.")

# Merge profiles
merged_profiles = {}
merged_profiles.update(PART1_PROFILES)
merged_profiles.update(PART2_PROFILES)
merged_profiles.update(PART3_PROFILES)

print(f"Part 1 profiles: {len(PART1_PROFILES)}")
print(f"Part 2 profiles: {len(PART2_PROFILES)}")
print(f"Part 3 profiles: {len(PART3_PROFILES)}")
print(f"Total merged profiles: {len(merged_profiles)}")

# Verification checks
missing_in_profiles = set(db_standards.keys()) - set(merged_profiles.keys())
extra_in_profiles = set(merged_profiles.keys()) - set(db_standards.keys())

if missing_in_profiles:
    print(f"ERROR: Missing standards in profiles ({len(missing_in_profiles)}): {missing_in_profiles}")
    sys.exit(1)

if extra_in_profiles:
    print(f"ERROR: Extra standards in profiles ({len(extra_in_profiles)}): {extra_in_profiles}")
    sys.exit(1)

# Check all near_match_candidates exist in db_standards
invalid_candidates = {}
for is_num, prof in merged_profiles.items():
    candidates = prof.get("near_match_candidates", [])
    if not candidates:
        print(f"WARNING: No near_match_candidates for {is_num}")
    for cand in candidates:
        if cand not in db_standards:
            invalid_candidates.setdefault(is_num, []).append(cand)

if invalid_candidates:
    print(f"ERROR: Invalid near-match candidates detected: {invalid_candidates}")
    sys.exit(1)

# Combine with standard metadata from dump
final_profiles = {}
for is_num, s in db_standards.items():
    prof = merged_profiles[is_num]
    final_profiles[is_num] = {
        "id": s["id"],
        "standard_id": s["standard_id"],
        "is_number": is_num,
        "title": s["title"],
        "sector": s["sector"],
        "clean_product": prof["clean_product"],
        "paraphrases": prof["paraphrases"],
        "indirect_descriptions": prof["indirect_descriptions"],
        "key_features": prof["key_features"],
        "materials": prof.get("materials", s.get("materials") or []),
        "parameters": prof.get("parameters", {}),
        "application": prof.get("application", s.get("application") or ""),
        "near_match_candidates": prof.get("near_match_candidates", [is_num]),
        "near_match_specs": prof.get("near_match_specs", [])
    }

out_path = Path("data/processed/standards_profiles.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(final_profiles, f, indent=2)

print(f"SUCCESS: Saved {len(final_profiles)} verified standards profiles to {out_path}")
