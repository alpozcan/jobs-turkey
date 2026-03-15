"""
Build a compact JSON for the website by merging CSV stats with AI exposure scores.

Reads occupations.csv (Turkish labor market data) and scores.json (AI exposure).
Writes site/data.json.

Usage:
    uv run python build_site_data.py
"""

import csv
import json
import os


def main():
    # Load AI exposure scores keyed by slug
    with open("scores.json") as f:
        scores_list = json.load(f)
    scores = {s["slug"]: s for s in scores_list}

    # Load CSV stats (Turkish columns)
    with open("occupations.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Merge CSV rows with exposure scores
    data = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        data.append({
            "title": row["title"],
            "title_en": row["title_en"],
            "slug": slug,
            "category": row["category"],
            "isco": row["isco_code"],
            "pay": int(row["median_pay_monthly"]) if row.get("median_pay_monthly") else None,
            "jobs": int(row["num_jobs"]) if row.get("num_jobs") else None,
            "education": row["entry_education"],
            "exposure": score.get("exposure"),
            "exposure_rationale": score.get("rationale"),
            "source": row.get("source", ""),
        })

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"Wrote {len(data)} occupations to site/data.json")

    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Total jobs represented: {total_jobs:,}")

    exposures = [d["exposure"] for d in data if d["exposure"] is not None]
    if exposures:
        avg_exposure = sum(exposures) / len(exposures)
        print(f"Average AI exposure score: {avg_exposure:.1f}")


if __name__ == "__main__":
    main()
