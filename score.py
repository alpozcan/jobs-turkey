"""
Score each occupation's AI exposure using an LLM via OpenRouter.

Reads occupation data from occupations.json (and optionally salary/employment
data from occupations.csv), sends each to an LLM with a Turkey-specific scoring
rubric, and collects structured scores. Results are cached incrementally to
scores.json so the script can be resumed if interrupted.

Usage:
    uv run python score.py
    uv run python score.py --model google/gemini-3-flash-preview
    uv run python score.py --start 0 --end 10   # test on first 10
"""

import argparse
import csv
import json
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "google/gemini-3-flash-preview"
OUTPUT_FILE = "scores.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """\
Sen, farklı mesleklerin yapay zekaya ne kadar açık olduğunu değerlendiren uzman \
bir analistsin. Sana Türkiye iş gücü piyasasındaki bir mesleğin açıklaması \
verilecek.

Mesleğin genel **Yapay Zeka Maruziyeti**ni 0'dan 10'a kadar bir ölçekte \
puanla.

YZ Maruziyeti şunu ölçer: Yapay zeka bu mesleği ne kadar dönüştürecek? Hem \
doğrudan etkileri (yapay zekanın şu anda insanların yaptığı görevleri \
otomatikleştirmesi) hem de dolaylı etkileri (yapay zekanın her çalışanı o \
kadar verimli hale getirmesi ki daha az çalışana ihtiyaç duyulması) göz \
önünde bulundur.

Türkiye'ye özgü faktörleri de dikkate al:
- Kayıt dışı ekonomi (iş gücünün yaklaşık %25'i): Kayıt dışı çalışanlar \
dijital araçlara daha az erişime sahiptir ve YZ benimsemesi daha yavaş olabilir.
- Kırsal/kentsel dijital uçurum: Kırsal bölgelerdeki meslekler dijital \
altyapı eksikliği nedeniyle YZ'den daha az etkilenebilir.
- İmalat ağırlıklı ekonomi: Türkiye'nin güçlü imalat sektörü (otomotiv, \
tekstil, beyaz eşya) otomasyon açısından önemli bir faktördür.
- Büyük tarım sektörü: Tarım sektörü hâlâ önemli bir istihdam kaynağıdır ve \
genellikle düşük dijitalleşme seviyesine sahiptir.
- Turizm sektörünün önemi: Turizm Türkiye ekonomisinde kritik bir rol oynar \
ve çoğunlukla yüz yüze insan etkileşimi gerektirir.

Önemli bir gösterge, işin ürününün temelde dijital olup olmadığıdır. Eğer iş \
tamamen ev ofisinden bilgisayar başında yapılabiliyorsa — yazma, kodlama, \
analiz etme, iletişim kurma — o zaman YZ maruziyeti doğası gereği yüksektir \
(7+), çünkü dijital alanlardaki YZ yetenekleri hızla ilerlemektedir. Bugünün \
YZ'si böyle bir işin her yönünü halledemese bile, ilerleme hızı dikkat \
çekicidir. Tersine, fiziksel varlık, el becerisi veya fiziksel dünyada anlık \
insan etkileşimi gerektiren işlerin YZ maruziyetine karşı doğal bir engeli \
vardır.

Puanını kalibre etmek için şu referans noktalarını kullan:

- **0–1: Minimum maruziyet.** İş neredeyse tamamen fiziksel, el becerisi \
gerektiren veya öngörülemeyen ortamlarda anlık insan varlığı gerektiren bir iş. \
YZ'nin günlük işe etkisi yok denecek kadar az. \
Örnekler: çiftçi, balıkçı, inşaat işçisi.

- **2–3: Düşük maruziyet.** Çoğunlukla fiziksel veya kişilerarası iş. YZ \
küçük çevresel görevlere (planlama, evrak işleri) yardımcı olabilir ama işin \
özüne dokunmaz. \
Örnekler: tesisatçı, elektrikçi, güvenlik görevlisi, kuaför.

- **4–5: Orta düzey maruziyet.** Fiziksel/kişilerarası iş ile bilgi işçiliğinin \
karışımı. YZ, bilgi işleme kısımlarına anlamlı bir şekilde yardımcı olabilir \
ama işin önemli bir bölümü hâlâ insan varlığı gerektirir. \
Örnekler: hemşire, veteriner, eczacı, polis memuru.

- **6–7: Yüksek maruziyet.** Ağırlıklı olarak bilgi işçiliği, bir miktar \
insan muhakemesi, ilişki veya fiziksel varlık gerektiren. YZ araçları zaten \
kullanışlı ve YZ kullanan çalışanlar önemli ölçüde daha verimli olabilir. \
Örnekler: öğretmen, muhasebeci, avukat, gazeteci, pazarlama uzmanı.

- **8–9: Çok yüksek maruziyet.** İş neredeyse tamamen bilgisayar başında \
yapılıyor. Tüm temel görevler — yazma, kodlama, analiz, tasarım, iletişim — \
YZ'nin hızla geliştiği alanlarda. Meslek büyük bir yeniden yapılanmayla karşı \
karşıya. \
Örnekler: yazılım geliştirici, grafik tasarımcı, çevirmen, veri analisti, \
sosyal medya uzmanı, mali müşavir.

- **10: Maksimum maruziyet.** Rutin bilgi işleme, tamamen dijital, fiziksel \
bileşeni yok. YZ'nin çoğunu bugün bile yapabildiği işler. \
Örnekler: veri giriş elemanı, çağrı merkezi elemanı.

YALNIZCA aşağıdaki formatta bir JSON nesnesi ile yanıt ver, başka metin yok:
{
  "exposure": <0-10>,
  "rationale": "<2-3 cümle ile temel faktörleri açıklayın>"
}\
"""


def load_csv_data(csv_path="occupations.csv"):
    """Load salary/employment data from occupations.csv if available."""
    data = {}
    if not os.path.exists(csv_path):
        return data
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row.get("slug", "")
            if slug:
                data[slug] = row
    return data


def load_calibration_context(path="calibration_context.json"):
    """Load calibration data extracted from HuggingFace datasets."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_occupation_text(occ, csv_data, cal_context):
    """Build a description string from all available data sources.

    Includes occupation metadata, Turkish labor market stats, and
    calibration evidence from HuggingFace datasets (if available).
    The LLM uses all of this to determine the final score.
    """
    slug = occ.get("slug", "")

    lines = [
        f"Meslek: {occ.get('title', '')}",
        f"İngilizce Adı: {occ.get('title_en', '')}",
        f"ISCO Kodu: {occ.get('isco', '')}",
        f"Kategori: {occ.get('category', '')}",
    ]

    # Turkish labor market data
    csv_row = csv_data.get(slug, {})
    if csv_row:
        if csv_row.get("median_pay_monthly"):
            lines.append(f"Medyan Aylık Ücret (Türkiye): ₺{csv_row['median_pay_monthly']}")
        if csv_row.get("num_jobs"):
            lines.append(f"Tahmini İstihdam (Türkiye): {csv_row['num_jobs']}")
        if csv_row.get("entry_education"):
            lines.append(f"Giriş Eğitimi: {csv_row['entry_education']}")

    # Calibration evidence from HuggingFace datasets
    cal = cal_context.get(slug, {})
    if cal:
        lines.append("")
        lines.append("── Kalibrasyon Verileri (referans, ABD piyasası) ──")

        obs = cal.get("anthropic_observed_exposure")
        if obs:
            lines.append(
                f"Gözlemlenen YZ Kullanım Oranı: {obs['avg_exposure']:.3f} "
                f"(aralık: {obs['min']:.3f}–{obs['max']:.3f}, "
                f"{obs['n_occupations']} benzer meslek)")
            lines.append(f"  Not: {obs['note']}")
            if obs.get("sample_titles"):
                lines.append(f"  Örnek eşleşen meslekler: {', '.join(obs['sample_titles'])}")

        auto = cal.get("automation_probability")
        if auto:
            lines.append(
                f"Otomasyon Olasılığı: %{auto['avg_pct']:.0f} "
                f"(aralık: %{auto['min_pct']:.0f}–%{auto['max_pct']:.0f}, "
                f"{auto['n_occupations']} benzer meslek)")
            lines.append(f"  Not: {auto['note']}")

        esco = cal.get("esco_skill_profile")
        if esco:
            lines.append(
                f"ESCO Dijital Beceri Oranı: {esco['digital_ratio']:.1%}"
                f"{' (grup ortalaması)' if esco.get('is_group_average') else ''}")
            if esco.get("note"):
                lines.append(f"  Not: {esco['note']}")

        lines.append("")
        lines.append(
            "ÖNEMLİ: Yukarıdaki veriler ABD piyasasına aittir ve gözlemlenen "
            "MEVCUT durumu yansıtır. Türkiye'nin koşullarını ve GELECEK "
            "potansiyelini de göz önünde bulundurarak nihai puanını belirle."
        )

    return "\n".join(lines)


def score_occupation(client, text, model):
    """Send one occupation to the LLM and parse the structured response."""
    response = client.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]  # remove first line
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    return json.loads(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--force", action="store_true",
                        help="Re-score even if already cached")
    args = parser.parse_args()

    with open("occupations.json", encoding="utf-8") as f:
        occupations = json.load(f)

    csv_data = load_csv_data()
    cal_context = load_calibration_context()
    if cal_context:
        print(f"Calibration context loaded: {len(cal_context)} occupations")
    else:
        print("No calibration_context.json found — run calibrate.py first for better results")

    subset = occupations[args.start:args.end]

    # Load existing scores
    scores = {}
    if os.path.exists(OUTPUT_FILE) and not args.force:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for entry in json.load(f):
                scores[entry["slug"]] = entry

    print(f"Scoring {len(subset)} occupations with {args.model}")
    print(f"Already cached: {len(scores)}")

    errors = []
    client = httpx.Client()

    for i, occ in enumerate(subset):
        slug = occ["slug"]

        if slug in scores:
            continue

        text = build_occupation_text(occ, csv_data, cal_context)

        print(f"  [{i+1}/{len(subset)}] {occ['title']}...", end=" ", flush=True)

        try:
            result = score_occupation(client, text, args.model)
            scores[slug] = {
                "slug": slug,
                "title": occ["title"],
                "title_en": occ.get("title_en", ""),
                "category": occ.get("category", ""),
                "isco": occ.get("isco", ""),
                **result,
            }
            print(f"exposure={result['exposure']}")
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(slug)

        # Save after each one (incremental checkpoint)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(scores.values()), f, indent=2, ensure_ascii=False)

        if i < len(subset) - 1:
            time.sleep(args.delay)

    client.close()

    print(f"\nDone. Scored {len(scores)} occupations, {len(errors)} errors.")
    if errors:
        print(f"Errors: {errors}")

    # Summary stats
    vals = [s for s in scores.values() if "exposure" in s]
    if vals:
        avg = sum(s["exposure"] for s in vals) / len(vals)
        by_score = {}
        for s in vals:
            bucket = s["exposure"]
            by_score[bucket] = by_score.get(bucket, 0) + 1
        print(f"\nAverage exposure across {len(vals)} occupations: {avg:.1f}")
        print("Distribution:")
        for k in sorted(by_score):
            print(f"  {k}: {'█' * by_score[k]} ({by_score[k]})")


if __name__ == "__main__":
    main()
