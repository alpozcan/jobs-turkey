# Türkiye İş Gücü — YZ Maruziyeti

Türkiye iş gücü piyasasındaki mesleklerin yapay zeka ve otomasyona maruziyetini analiz eder.

[Karpathy'nin AI Jobs](https://github.com/karpathy/jobs) projesinin Türkiye adaptasyonudur.

**Canlı demo: [alpozcan.github.io/jobs-turkey](https://alpozcan.github.io/jobs-turkey/)**

![Treemap](jobs.png)

## Ne var burada

**117 meslek**, 18 kategori altında analiz edildi. Her meslek 0–10 arasında YZ maruziyet skoru aldı. İnteraktif treemap'te alan = istihdam sayısı, renk = YZ maruziyeti (koyu mavi = güvenli, turuncu = yüksek risk). Renk paleti renk körü dostu (viridis tabanlı) seçilmiştir.

Herhangi bir mesleğe tıklayarak detaylı analiz dialogunu açabilirsiniz:
- Skor göstergesi ve seviye etiketi
- Aylık ücret, istihdam, eğitim ve kategori karşılaştırması
- YZ maruziyet analizi ve gerekçesi
- Tahmini faktör dağılımı (dijitallik, rutinlik, fiziksellik, yaratıcılık, insan etkileşimi)
- Benzer meslekler (tıklanabilir)
- Ekonomik etki hesaplaması

## Veri kaynakları

### Birincil veriler (repoda)

| Kaynak | Açıklama |
|--------|----------|
| [Önceki Yazılımcı 2025](https://github.com/oncekiyazilimci/2025-yazilim-sektoru-maaslari) | 9.056 teknoloji sektörü maaş anketi (JSON) |
| [@maashesabi](https://x.com/maashesabi) | Anonim maaş DM'leri (ek veri) |

### Resmi kaynaklar

| Kaynak | Açıklama |
|--------|----------|
| [TÜİK İşgücü İstatistikleri](https://data.tuik.gov.tr) | İstihdam sayıları, ücret verileri |
| [TÜİK Kazanç Yapısı Araştırması](https://data.tuik.gov.tr/Bulten/Index?p=Kazanc-Yapisi-Istatistikleri-2023-53700) | Meslek gruplarına göre brüt/net kazanç |
| [İŞKUR Meslek Bilgi Bankası](https://esube.iskur.gov.tr/Meslek/MeslekleriTaniyalim.aspx) | 1.123 meslek tanımı, ISCO-08 kodları |
| [SGK İstatistik Yıllıkları](https://www.sgk.gov.tr/Istatistik/Yillik/) | Kayıtlı istihdam ve prim verileri (2007–2024) |

### Kalibrasyon verileri (HuggingFace)

| Dataset | Açıklama |
|---------|----------|
| [Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex) | O*NET görev düzeyinde YZ maruziyeti, otomasyon/artırma oranları |
| [danieldux/ESCO](https://huggingface.co/datasets/danieldux/ESCO) | 2.942 meslek + 13.485 beceri, ISCO-08 eşlemeli |
| [gpriday/job-titles](https://huggingface.co/datasets/gpriday/job-titles) | 65K meslek unvanı (ESCO + O*NET + OSCA) |

Tüm kaynakların detaylı listesi için [DATASETS.md](DATASETS.md) dosyasına bakın.

## Puanlama

Her meslek, YZ maruziyetini ölçen 0–10 arasında bir puan alır:

| Puan | Anlamı | Örnekler |
|------|--------|----------|
| 0–1 | Minimal | Çiftçi, itfaiyeci, inşaat işçisi |
| 2–3 | Düşük | Elektrikçi, hemşire, garson |
| 4–5 | Orta | Öğretmen, polis, veteriner |
| 6–7 | Yüksek | Avukat, muhasebeci, pazarlamacı |
| 8–9 | Çok yüksek | Yazılımcı, grafik tasarımcı, çevirmen |
| 10 | Maksimum | Veri giriş elemanı |

Puanlama yöntemi:
1. **Sezgisel skorlar** — meslek özelliklerine dayalı tahmini puanlar (`generate_preview_scores.py`)
2. **LLM puanlaması** — her meslek açıklaması Gemini Flash'a gönderilir, Türkiye'ye özgü rubrikle puanlanır (`score.py`)
3. **Kalibrasyon** — HuggingFace'deki Anthropic/EconomicIndex ve ESCO verileriyle skor kalibrasyonu (`calibrate.py`)

## Pipeline

```bash
# 1. Tahmini skorlarla önizleme (API gerektirmez)
python generate_preview_scores.py
python build_site_data.py

# 2. LLM ile gerçek puanlama (API anahtarı gerekli)
#    OPENROUTER_API_KEY ortam değişkenini .env'ye ekleyin
python score.py --model google/gemini-3-flash-preview

# 3. HuggingFace verileriyle kalibrasyon
pip install huggingface_hub datasets
python calibrate.py

# 4. Site verisi oluştur ve yerelde çalıştır
python build_site_data.py
cd site && python -m http.server 8000
```

## Dosya yapısı

```
├── occupations.json           # 117 Türkiye mesleği (ISCO-08 kodlu)
├── occupations.csv            # İstihdam, ücret, eğitim verileri
├── scores.json                # YZ maruziyet skorları (0–10) ve gerekçeler
├── score.py                   # LLM puanlama (Türkiye'ye özgü prompt)
├── calibrate.py               # HuggingFace verileriyle kalibrasyon
├── generate_preview_scores.py # Sezgisel skor üretici
├── build_site_data.py         # CSV + skorlar → site/data.json
├── DATASETS.md                # 17 veri kaynağının detaylı listesi
├── sources/
│   └── onceki_yazilimci_2025.json  # 9.056 teknoloji sektörü maaş verisi
└── site/
    ├── index.html             # İnteraktif treemap (Türkçe, renk körü dostu)
    └── data.json              # Frontend verisi
```

## Katkıda bulunma

PR'lar açıktır. Özellikle:
- Yeni meslek eklemeleri
- Daha iyi maaş/istihdam verileri
- TÜİK/İŞKUR/SGK verilerinin entegrasyonu
- Ek HuggingFace veri setleri ile kalibrasyon

## Lisans

Bu proje [Karpathy'nin jobs](https://github.com/karpathy/jobs) reposunun bir fork'udur.
