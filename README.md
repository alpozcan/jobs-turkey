# Türkiye İş Gücü — YZ Maruziyeti

Türkiye iş gücü piyasasındaki 117 mesleğin yapay zeka ve otomasyona maruziyetini analiz eden interaktif bir görselleştirme.

[Andrej Karpathy](https://karpathy.ai)'nin [AI Exposure of the US Job Market](https://karpathy.ai/jobs/) projesinin Türkiye uyarlamasıdır.

**Canlı demo: [alpozcan.github.io/jobs-turkey](https://alpozcan.github.io/jobs-turkey/)**

![Treemap](jobs.png)

## İçindekiler

- [Hakkında](#hakkında)
- [Veri Kaynakları](#veri-kaynakları)
- [Puanlama](#puanlama)
- [Başlarken](#başlarken)
- [Dosya Yapısı](#dosya-yapısı)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

## Hakkında

18 kategori altında **117 meslek** analiz edilmiştir. Her mesleğe 0–10 arasında bir YZ maruziyet skoru atanmıştır.

İnteraktif treemap'te dikdörtgen alanı istihdam sayısını, rengi ise YZ maruziyet düzeyini temsil eder (yeşil = güvenli, kırmızı = yüksek risk). Renk paleti, tüm renk körlüğü tiplerinde okunabilecek şekilde tasarlanmıştır.

Herhangi bir mesleğe tıklayarak detay dialogunu açabilirsiniz:

- Maruziyet skoru ve seviye göstergesi
- Aylık ücret, istihdam, eğitim düzeyi ve kategori karşılaştırması
- Akademik referanslarla desteklenen YZ maruziyet gerekçesi
- Tahmini faktör dağılımı (dijitallik, rutinlik, fiziksellik, yaratıcılık, insan etkileşimi)
- Çoklu kaynaklı ücret karşılaştırması (Önceki Yazılımcı, Levels.fyi, yazilimcimaaslari.org)
- Benzer meslekler (tıklanarak geçiş yapılabilir)
- Akademik referanslı ekonomik etki hesaplaması

## Veri Kaynakları

### Ücret ve İstihdam Verileri

| Kaynak | Açıklama |
|--------|----------|
| [Önceki Yazılımcı 2025](https://github.com/oncekiyazilimci/2025-yazilim-sektoru-maaslari) | 9.056 katılımcılı teknoloji sektörü maaş anketi |
| [Levels.fyi Turkey](https://www.levels.fyi/t/software-engineer/locations/turkey) | 327 yazılım mühendisi için doğrulanmış ücret verisi |
| [yazilimcimaaslari.org](https://yazilimcimaaslari.org) | 1.223 katılımcılı yazılım maaş anketi (2026) |
| [@maashesabi](https://x.com/maashesabi) | Anonim maaş paylaşımları (ek veri) |

### Resmi Kaynaklar

| Kaynak | Açıklama |
|--------|----------|
| [TÜİK İşgücü İstatistikleri](https://data.tuik.gov.tr) | Meslek gruplarına göre istihdam sayıları ve ücret verileri |
| [TÜİK Kazanç Yapısı Araştırması](https://data.tuik.gov.tr/Bulten/Index?p=Kazanc-Yapisi-Istatistikleri-2023-53700) | Meslek gruplarına göre brüt ve net kazanç dağılımı |
| [İŞKUR Meslek Bilgi Bankası](https://esube.iskur.gov.tr/Meslek/MeslekleriTaniyalim.aspx) | 1.123 meslek tanımı ve ISCO-08 sınıflandırması |
| [SGK İstatistik Yıllıkları](https://www.sgk.gov.tr/Istatistik/Yillik/) | Kayıtlı istihdam ve prim verileri (2007–2024) |

### Kalibrasyon Verisi

| Veri Seti | Açıklama |
|-----------|----------|
| [Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex) | 756 meslek için gözlemlenen YZ kullanım oranı ve otomasyon olasılığı |

Tüm kaynakların detaylı listesi için [DATASETS.md](DATASETS.md) dosyasına, akademik referanslar için [REFERENCES.md](REFERENCES.md) dosyasına bakabilirsiniz.

## Puanlama

Her meslek, yapay zeka maruziyetini ölçen 0–10 arasında bir puan alır:

| Puan | Seviye | Örnekler |
|------|--------|----------|
| 0–1 | Minimal | Çiftçi, itfaiyeci, inşaat işçisi |
| 2–3 | Düşük | Elektrikçi, hemşire, garson |
| 4–5 | Orta | Öğretmen, polis, veteriner |
| 6–7 | Yüksek | Avukat, muhasebeci, pazarlamacı |
| 8–9 | Çok yüksek | Yazılımcı, grafik tasarımcı, çevirmen |
| 10 | Maksimum | Veri giriş elemanı |

Puanlama üç aşamada gerçekleştirilir:

1. **Sezgisel skorlama** — Her meslek; dijitallik, rutinlik ve fiziksellik gibi özelliklerine göre bir başlangıç puanı alır (`generate_preview_scores.py`).
2. **Kalibrasyon** — Anthropic/EconomicIndex veri setinden gözlemlenen YZ kullanım oranları ve otomasyon olasılıkları çıkarılarak kalibrasyon bağlamı oluşturulur (`calibrate.py`).
3. **LLM değerlendirmesi** — Meslek açıklaması, kalibrasyon bağlamı ve Türkiye'ye özgü değerlendirme ölçütleri bir LLM'e gönderilir (`score.py`). Puanlama scripti OpenRouter aracılığıyla farklı modelleri destekler; varsayılan olarak Gemini Flash kullanılır. Mevcut skorlar Claude Opus 4.6 ile üretilmiştir.

Her gerekçe; Frey & Osborne (2017), Eloundou ve ark. (2024), Goldman Sachs (2023) gibi hakemli araştırmalara atıfla desteklenmektedir.

## Başlarken

### Gereksinimler

- Python 3.9+
- [huggingface_hub](https://pypi.org/project/huggingface-hub/) (yalnızca kalibrasyon için)
- [OpenRouter](https://openrouter.ai) API anahtarı (yalnızca LLM puanlaması için)

### Kurulum ve Kullanım

```bash
# 1. Sezgisel skorlarla önizleme oluşturma
python generate_preview_scores.py
python build_site_data.py

# 2. Kalibrasyon bağlamını oluşturma
#    (HuggingFace verileri indirilir, işlenir ve ardından silinir)
pip install huggingface_hub
python calibrate.py

# 3. LLM ile puanlama
#    OPENROUTER_API_KEY ortam değişkenini .env dosyasına ekleyin
python score.py --model google/gemini-3-flash-preview

# 4. Site verisini oluşturma ve yerelde çalıştırma
python build_site_data.py
cd site && python -m http.server 8000
```

## Dosya Yapısı

```
├── occupations.json             # 117 Türkiye mesleği (ISCO-08 kodlu)
├── occupations.csv              # İstihdam, ücret ve eğitim verileri
├── scores.json                  # YZ maruziyet skorları (0–10) ve gerekçeler
├── calibration_context.json     # Kalibrasyon verileri (HuggingFace kaynaklı)
├── score.py                     # LLM puanlama scripti (Türkiye'ye özgü prompt)
├── calibrate.py                 # Kalibrasyon bağlamı çıkarma scripti
├── generate_preview_scores.py   # Sezgisel skor üretici
├── build_site_data.py           # CSV + skorlar → site/data.json
├── DATASETS.md                  # 17 veri kaynağının detaylı listesi
├── REFERENCES.md                # 13 akademik referans (DOI bağlantılı)
├── sources/
│   └── onceki_yazilimci_2025.json   # 9.056 teknoloji sektörü maaş verisi
└── site/
    ├── index.html               # İnteraktif treemap (erişilebilir, renk körü dostu)
    ├── about.html               # Metodoloji ve proje hikayesi
    └── data.json                # Ön yüz verisi
```

## Katkıda Bulunma

Katkılarınızı bekliyoruz. Özellikle aşağıdaki alanlarda PR'lar memnuniyetle karşılanır:

- Yeni meslek eklemeleri
- Daha güncel veya kapsamlı maaş ve istihdam verileri
- TÜİK, İŞKUR ve SGK verilerinin doğrudan entegrasyonu
- Ek HuggingFace veri setleri ile kalibrasyon iyileştirmeleri

## Lisans

Bu proje, [arosstale/jobs](https://github.com/arosstale/jobs) deposunun fork'udur. Söz konusu depo, [Karpathy'nin jobs](https://github.com/karpathy/jobs) projesinin açık kaynak yeniden uygulamasıdır.
