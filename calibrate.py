"""
Extract calibration context from HuggingFace datasets.

Downloads Anthropic/EconomicIndex and danieldux/ESCO, extracts raw data signals
per occupation (observed AI exposure, automation probability, digital skill ratio),
saves to calibration_context.json for use by score.py, then deletes all downloads.

This script does NOT assign scores — it provides evidence for the LLM scorer.

Usage:
    pip install huggingface_hub
    python calibrate.py
"""

import csv
import json
import os
import shutil
import tempfile
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("huggingface_hub kuruluyor...")
    import subprocess
    subprocess.check_call(["pip", "install", "huggingface_hub", "-q"])
    from huggingface_hub import snapshot_download


# ── ISCO-08 2-digit to SOC 2-digit approximate crosswalk ────────────────
ISCO_TO_SOC = {
    "11": "11", "12": "11", "13": "11", "14": "11",
    "21": "15", "22": "29", "23": "25", "24": "13",
    "25": "15", "26": "23",
    "31": "17", "32": "29", "33": "13", "34": "27", "35": "15",
    "41": "43", "42": "43", "43": "43", "44": "43",
    "51": "35", "52": "41", "53": "31", "54": "33",
    "61": "45", "62": "45",
    "71": "47", "72": "49", "73": "51", "74": "49", "75": "51",
    "81": "51", "82": "51", "83": "53",
    "91": "37", "92": "45", "93": "47", "94": "35", "95": "41", "96": "53",
}

OUTPUT_FILE = "calibration_context.json"


def download(repo_id, cache_dir):
    print(f"  {repo_id} indiriliyor...")
    try:
        return snapshot_download(repo_id, repo_type="dataset", cache_dir=cache_dir,
                                 allow_patterns=["*.csv"])
    except Exception as e:
        print(f"  HATA: {e}")
        return None


def csv_files(d):
    if not d:
        return []
    return [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.endswith(".csv")]


def load_anthropic(repo_dir):
    """Extract per-SOC observed exposure and automation probability."""
    if not repo_dir:
        return {}, {}

    # job_exposure.csv: occ_code → observed_exposure (0–0.75)
    observed = {}  # soc_code → {title, exposure}
    for fp in csv_files(repo_dir):
        if os.path.basename(fp) != "job_exposure.csv":
            continue
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                for row in csv.DictReader(f):
                    code = row.get("occ_code", "").strip()
                    title = row.get("title", "").strip()
                    val = row.get("observed_exposure", "").strip()
                    if code and val:
                        try:
                            observed[code] = {"title": title, "exposure": float(val)}
                        except ValueError:
                            pass
            print(f"  job_exposure.csv: {len(observed)} meslek")
        except Exception as e:
            print(f"  job_exposure.csv hata: {e}")

    # wage_data.csv: SOCcode → ChanceAuto (0–99, -1=N/A)
    automation = {}  # soc_code → {title, chance_auto}
    for fp in csv_files(repo_dir):
        if os.path.basename(fp) != "wage_data.csv":
            continue
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                for row in csv.DictReader(f):
                    code = row.get("SOCcode", "").strip()
                    title = row.get("JobName", "").strip()
                    auto = row.get("ChanceAuto", "").strip()
                    if code and auto:
                        try:
                            v = float(auto)
                            if v >= 0:
                                automation[code] = {"title": title, "chance_auto_pct": v}
                        except ValueError:
                            pass
            print(f"  wage_data.csv: {len(automation)} meslek")
        except Exception as e:
            print(f"  wage_data.csv hata: {e}")

    return observed, automation


def load_esco_skills(repo_dir):
    """Extract skill counts per ISCO-4 from ESCO."""
    if not repo_dir:
        return {}

    digital_kw = {"digital", "software", "programming", "database", "computer", "data",
                  "algorithm", "web", "cloud", "network", "cyber", "ict", "coding",
                  "automation", "artificial intelligence", "machine learning", "analytics"}

    counts = {}  # isco4 → {total, digital, sample_skills}
    for fp in csv_files(repo_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                hdrs = reader.fieldnames or []
                isco_col = next((h for h in hdrs if "isco" in h.lower()), None)
                txt_cols = [h for h in hdrs if any(k in h.lower() for k in
                            ["skill", "competence", "label", "description", "title"])]
                if not isco_col or not txt_cols:
                    continue
                for row in reader:
                    isco = row.get(isco_col, "").strip()
                    if len(isco) < 4:
                        continue
                    i4 = isco[:4]
                    txt = " ".join(row.get(c, "") for c in txt_cols).lower()
                    if not txt.strip():
                        continue
                    if i4 not in counts:
                        counts[i4] = {"total": 0, "digital": 0}
                    counts[i4]["total"] += 1
                    if any(k in txt for k in digital_kw):
                        counts[i4]["digital"] += 1
        except Exception:
            continue

    result = {}
    for i4, c in counts.items():
        if c["total"] > 0:
            result[i4] = {
                "total_skills": c["total"],
                "digital_skills": c["digital"],
                "digital_ratio": round(c["digital"] / c["total"], 3),
            }

    if result:
        print(f"  ESCO: {len(result)} ISCO-4 meslek")
    else:
        print("  ESCO: veri bulunamadı")
    return result


def build_context(occs, observed, automation, esco_skills):
    """Build per-occupation calibration context from all data sources."""
    context = {}

    for occ in occs:
        slug = occ["slug"]
        isco = occ.get("isco", "")
        i2 = isco[:2] if isco else ""
        soc2 = ISCO_TO_SOC.get(i2, "")

        entry = {}

        # Anthropic observed exposure — find closest SOC match
        if soc2:
            # Average all SOC codes starting with this 2-digit prefix
            matches = {k: v for k, v in observed.items()
                       if k.replace("-", "").startswith(soc2)}
            if matches:
                vals = [v["exposure"] for v in matches.values()]
                titles = [v["title"] for v in list(matches.values())[:3]]
                entry["anthropic_observed_exposure"] = {
                    "soc_group": soc2,
                    "avg_exposure": round(sum(vals) / len(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4),
                    "n_occupations": len(vals),
                    "sample_titles": titles,
                    "note": "Observed current AI usage rate (0=none, 0.75=highest observed). "
                            "This measures TODAY's adoption, not future potential."
                }

            # Automation probability from wage_data
            auto_matches = {k: v for k, v in automation.items()
                           if k.replace("-", "").replace(".", "").startswith(soc2)}
            if auto_matches:
                vals = [v["chance_auto_pct"] for v in auto_matches.values()]
                entry["automation_probability"] = {
                    "soc_group": soc2,
                    "avg_pct": round(sum(vals) / len(vals), 1),
                    "min_pct": round(min(vals), 1),
                    "max_pct": round(max(vals), 1),
                    "n_occupations": len(vals),
                    "note": "Estimated probability of automation (0-99%). "
                            "From Oxford/Frey & Osborne methodology."
                }

        # ESCO digital skill ratio
        i4 = isco[:4] if isco else ""
        if i4 in esco_skills:
            entry["esco_skill_profile"] = esco_skills[i4]
            entry["esco_skill_profile"]["note"] = (
                "Ratio of digital/ICT skills in this occupation's ESCO profile. "
                "Higher ratio suggests more screen-based work."
            )
        elif i2:
            # Fall back to ISCO-2 group average
            group = {k: v for k, v in esco_skills.items() if k[:2] == i2}
            if group:
                avg_ratio = sum(v["digital_ratio"] for v in group.values()) / len(group)
                entry["esco_skill_profile"] = {
                    "digital_ratio": round(avg_ratio, 3),
                    "note": f"ISCO-2 group average ({len(group)} occupations). "
                            "Exact ISCO-4 match not found.",
                    "is_group_average": True,
                }

        if entry:
            context[slug] = entry

    return context


def cleanup(cache_dir):
    print(f"\n  Geçici dosyalar temizleniyor...")
    shutil.rmtree(cache_dir, ignore_errors=True)
    hf = Path.home() / ".cache" / "huggingface" / "hub"
    for name in ["datasets--Anthropic--EconomicIndex", "datasets--danieldux--ESCO"]:
        p = hf / name
        if p.exists():
            print(f"  Siliniyor: {name}")
            shutil.rmtree(p, ignore_errors=True)


def main():
    print("=" * 60)
    print("  Kalibrasyon Bağlamı Oluşturuluyor")
    print("=" * 60)

    with open("occupations.json", encoding="utf-8") as f:
        occs = json.load(f)
    print(f"\n{len(occs)} meslek yüklendi.\n")

    cache_dir = tempfile.mkdtemp(prefix="hf_cal_")

    print("[1/2] HuggingFace veri setleri indiriliyor...")
    anth_dir = download("Anthropic/EconomicIndex", cache_dir)
    esco_dir = download("danieldux/ESCO", cache_dir)

    print("\n[2/2] Bağlam verisi çıkartılıyor...")
    observed, automation = load_anthropic(anth_dir)
    esco = load_esco_skills(esco_dir)

    context = build_context(occs, observed, automation, esco)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    # Summary
    has_anthropic = sum(1 for v in context.values() if "anthropic_observed_exposure" in v)
    has_auto = sum(1 for v in context.values() if "automation_probability" in v)
    has_esco = sum(1 for v in context.values() if "esco_skill_profile" in v)
    print(f"\n  {len(context)} meslek için bağlam oluşturuldu:")
    print(f"    Anthropic gözlemlenen maruziyet: {has_anthropic}")
    print(f"    Otomasyon olasılığı: {has_auto}")
    print(f"    ESCO beceri profili: {has_esco}")
    print(f"\n  Kaydedildi: {OUTPUT_FILE}")
    print(f"  score.py bu dosyayı LLM puanlamasında bağlam olarak kullanacak.")

    cleanup(cache_dir)
    print("\n  Tamamlandı!")
    print("=" * 60)


if __name__ == "__main__":
    main()
