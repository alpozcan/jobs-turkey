"""
Calibrate AI exposure scores using HuggingFace datasets.

Downloads Anthropic/EconomicIndex and danieldux/ESCO, maps Turkish occupations
via ISCO-08 codes, computes data-driven scores, blends with existing heuristic
scores, and cleans up all downloaded data afterwards.

Usage:
    pip install huggingface_hub
    python calibrate.py
"""

import csv
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("huggingface_hub kuruluyor...")
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


def download(repo_id, cache_dir):
    print(f"  {repo_id} indiriliyor...")
    try:
        return snapshot_download(repo_id, repo_type="dataset", cache_dir=cache_dir,
                                 allow_patterns=["*.csv", "*.parquet", "*.json"])
    except Exception as e:
        print(f"  HATA: {e}")
        return None


def csv_files(d):
    if not d:
        return []
    return [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.endswith(".csv")]


def load_anthropic(repo_dir):
    """Get SOC-level AI exposure from job_exposure.csv and wage_data.csv."""
    if not repo_dir:
        return {}

    soc_exposure = {}  # soc2 -> [values]

    for fp in csv_files(repo_dir):
        fname = os.path.basename(fp)

        # job_exposure.csv: observed_exposure is 0–0.75 range → scale to 0-10
        if fname == "job_exposure.csv":
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    for row in csv.DictReader(f):
                        code = row.get("occ_code", "").strip().replace("-", "")
                        val = row.get("observed_exposure", "").strip()
                        if code and val:
                            try:
                                v = min(float(val) * 13.4, 10)  # max ~0.745 → ~10
                                soc_exposure.setdefault(code[:2], []).append(v)
                            except ValueError:
                                pass
                print(f"  job_exposure.csv: {sum(len(v) for v in soc_exposure.values())} meslek")
            except Exception as e:
                print(f"  job_exposure.csv hata: {e}")

        # wage_data.csv: ChanceAuto is 0–99 percentage, -1 = no data
        elif fname == "wage_data.csv":
            auto_count = 0
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    for row in csv.DictReader(f):
                        code = row.get("SOCcode", "").strip().replace("-", "").replace(".", "")
                        auto = row.get("ChanceAuto", "").strip()
                        if code and auto:
                            try:
                                v = float(auto)
                                if v >= 0:  # skip -1 (no data)
                                    soc_exposure.setdefault(code[:2], []).append(v / 10)  # 0-99 → 0-9.9
                                    auto_count += 1
                            except ValueError:
                                pass
                if auto_count:
                    print(f"  wage_data.csv: {auto_count} otomasyon skoru")
            except Exception as e:
                print(f"  wage_data.csv hata: {e}")

    # Average per SOC-2 group
    result = {}
    for s2, vals in soc_exposure.items():
        result[s2] = sum(vals) / len(vals)

    if result:
        print(f"  Anthropic toplam: {len(result)} SOC-2 grup (ort: {sum(result.values())/len(result):.1f})")
    else:
        print("  Anthropic: veri bulunamadı")
    return result


def load_esco(repo_dir):
    """Get digital skill ratio per ISCO-4 from ESCO."""
    if not repo_dir:
        return {}
    digi_kw = {"digital", "software", "programming", "database", "computer", "data",
               "algorithm", "web", "cloud", "network", "cyber", "ict", "coding",
               "automation", "artificial intelligence", "machine learning", "analytics"}

    counts = {}  # isco4 -> [total, digital]
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
                    counts.setdefault(i4, [0, 0])
                    counts[i4][0] += 1
                    if any(k in txt for k in digi_kw):
                        counts[i4][1] += 1
        except Exception:
            continue

    result = {i4: d / t for i4, (t, d) in counts.items() if t > 0}
    if result:
        print(f"  ESCO: {len(result)} ISCO-4 meslek")
    else:
        print("  ESCO: veri bulunamadı")
    return result


def blend(isco, old_score, anthropic, esco):
    """60% data-driven + 40% heuristic."""
    parts = []
    i2, i4 = (isco[:2] if isco else ""), (isco[:4] if isco else "")

    soc2 = ISCO_TO_SOC.get(i2, "")
    if soc2 and soc2 in anthropic:
        parts.append(anthropic[soc2])

    if i4 in esco:
        parts.append(min(esco[i4] * 15, 10))
    elif i2:
        grp = [v for k, v in esco.items() if k[:2] == i2]
        if grp:
            parts.append(min(sum(grp) / len(grp) * 15, 10))

    if parts:
        data = sum(parts) / len(parts)
        return round(min(max(data * 0.6 + old_score * 0.4, 0), 10), 1)
    return old_score


def cleanup(cache_dir):
    """Remove all downloaded data."""
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
    print("  Türkiye İş Gücü — YZ Maruziyet Kalibrasyonu")
    print("=" * 60)

    with open("occupations.json", encoding="utf-8") as f:
        occs = json.load(f)
    with open("scores.json", encoding="utf-8") as f:
        existing = {s["slug"]: s for s in json.load(f)}

    print(f"\n{len(occs)} meslek, {len(existing)} mevcut skor.\n")

    cache_dir = tempfile.mkdtemp(prefix="hf_cal_")

    print("[1/3] HuggingFace veri setleri indiriliyor...")
    anth_dir = download("Anthropic/EconomicIndex", cache_dir)
    esco_dir = download("danieldux/ESCO", cache_dir)

    print("\n[2/3] Ayrıştırılıyor...")
    anth = load_anthropic(anth_dir)
    esco = load_esco(esco_dir)
    has = bool(anth) or bool(esco)

    if not has:
        print("\n  UYARI: Kalibrasyon verisi yüklenemedi. Skorlar korunuyor.\n")

    print(f"\n[3/3] Kalibre ediliyor...")
    calibrated = []
    diffs = []
    for occ in occs:
        slug, isco = occ["slug"], occ.get("isco", "")
        old = existing.get(slug, {})
        old_s = old.get("exposure", 5.0)
        new_s = blend(isco, old_s, anth, esco) if has else old_s
        calibrated.append({"slug": slug, "title": occ["title"],
                           "exposure": new_s, "rationale": old.get("rationale", "")})
        diffs.append((occ["title"], old_s, new_s, new_s - old_s))

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(calibrated, f, indent=2, ensure_ascii=False)

    print(f"\n{'Meslek':<35} {'Eski':>6} {'Yeni':>6} {'Fark':>6}")
    print("-" * 58)
    diffs.sort(key=lambda x: abs(x[3]), reverse=True)
    for t, o, n, d in diffs[:25]:
        print(f"  {t:<33} {o:>5.1f}  {n:>5.1f}  {'+' if d > 0 else ''}{d:>5.1f}")
    if len(diffs) > 25:
        print(f"  ... ve {len(diffs) - 25} meslek daha")

    oa = sum(c[1] for c in diffs) / len(diffs)
    na = sum(c[2] for c in diffs) / len(diffs)
    ac = sum(abs(c[3]) for c in diffs) / len(diffs)
    print(f"\n  Ortalama: {oa:.1f} → {na:.1f} (ort. değişim: {ac:.2f})")

    print("\n  site/data.json yeniden oluşturuluyor...")
    subprocess.run(["python3", "build_site_data.py"], check=True)

    cleanup(cache_dir)
    print("\n  Tamamlandı!")
    print("=" * 60)


if __name__ == "__main__":
    main()
