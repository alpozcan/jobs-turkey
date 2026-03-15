# Türkiye İş Gücü — YZ Maruziyeti

Türkiye iş gücü piyasasındaki mesleklerin yapay zeka ve otomasyona maruziyetini analiz eder. [Karpathy'nin AI Jobs](https://github.com/karpathy/jobs) projesinin Türkiye adaptasyonudur.

**Canlı demo: [alpozcan.github.io/jobs-turkey](https://alpozcan.github.io/jobs-turkey/)**

## Ne var burada

**117 meslek**, 18 kategori altında analiz edildi. Her meslek 0-10 arasında YZ maruziyet skoru aldı.

## Veri kaynakları

| Kaynak | Açıklama |
|--------|----------|
| TÜİK İşgücü İstatistikleri | İstihdam sayıları, ücret verileri |
| Önceki Yazılımcı 2025 | 9.056 teknoloji sektörü maaş anketi |
| İŞKUR Meslek Bilgi Bankası | Meslek tanımları |
| @maashesabi | Anonim maaş verileri |
| kariyer.net | Piyasa maaş verileri |

Detaylı kaynak listesi için [DATASETS.md](DATASETS.md) dosyasına bakın.

## Puanlama

Her meslek, YZ maruziyetini ölçen 0-10 arasında bir puan alır:

| Puan | Anlamı | Örnekler |
|------|--------|----------|
| 0-1 | Minimal | Çiftçi, itfaiyeci, inşaat işçisi |
| 2-3 | Düşük | Elektrikçi, hemşire, garson |
| 4-5 | Orta | Öğretmen, polis, veteriner |
| 6-7 | Yüksek | Avukat, muhasebeci, pazarlamacı |
| 8-9 | Çok yüksek | Yazılımcı, grafik tasarımcı, çevirmen |
| 10 | Maksimum | Veri giriş elemanı |

## Pipeline

```bash
# Tahmini skorlarla önizleme (API gerektirmez)
python generate_preview_scores.py
python build_site_data.py

# LLM ile gerçek puanlama (API anahtarı gerekli)
python score.py --model google/gemini-3-flash-preview

# Site verisi oluştur
python build_site_data.py

# Yerelde çalıştır
cd site && python -m http.server 8000
```

## Katkıda bulunma

PR'lar açıktır. Özellikle:
- Yeni meslek eklemeleri
- Daha iyi maaş/istihdam verileri
- TÜİK/İŞKUR verilerinin entegrasyonu
