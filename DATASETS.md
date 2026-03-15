# Turkish Labor Market Data Sources

## Primary Data (in repo)

| # | Source | Records | Format | Coverage |
|---|--------|---------|--------|----------|
| 1 | **Önceki Yazılımcı 2025** | 9,056 | JSON | 59 tech positions, salary by level/city |
| 2 | **@maashesabi** | 38 | Images/OCR | Crowdsourced informal salary DMs |

## Official Government Sources

| # | Source | URL | Download | Coverage |
|---|--------|-----|----------|----------|
| 3 | **TÜİK Kazanç Yapısı İstatistikleri** | [data.tuik.gov.tr](https://data.tuik.gov.tr/Bulten/Index?p=Kazanc-Yapisi-Istatistikleri-2023-53700) | Excel | Annual gross/net by ISCO-08 (43-436 groups) |
| 4 | **TÜİK İşgücü İstatistikleri** | [data.tuik.gov.tr](https://data.tuik.gov.tr/Kategori/GetKategori?p=istihdam-issizlik-ve-ucret-108&dil=2) | Excel, microdata | Employment/unemployment by ISCO-08 |
| 5 | **İŞKUR Meslek Bilgi Sistemi** | [esube.iskur.gov.tr](https://esube.iskur.gov.tr/Meslek/MeslekleriTaniyalim.aspx) | Excel/XML/PDF | 1,123 occupations (7,138 at 6-digit ISCO) |
| 6 | **SGK İstatistik Yıllıkları** | [sgk.gov.tr](https://www.sgk.gov.tr/Istatistik/Yillik/fcd5e59b-6af9-4d90-a451-ee7500eb1cb4/) | ZIP (2007-2024) | All formal employment, premium/earnings |
| 7 | **HMB/BUMKO Maaş İstatistikleri** | [hmb.gov.tr](https://www.hmb.gov.tr/bumko-maas-istatistikleri-verileri) | Download | All ~3.5M civil servants by grade/rank |
| 8 | **YÖK/TÜİK İstihdam Göstergeleri** | [data.tuik.gov.tr](https://data.tuik.gov.tr/Bulten/Index?p=Yuksekogretim-Istihdam-Gostergeleri-2024-54096) | Bulletin | 200+ degree fields → employment rates |

## Crowdsourced / Survey Data

| # | Source | URL | Download | Coverage |
|---|--------|-----|----------|----------|
| 9 | **yazilimcimaaslari.org** | [yazilimcimaaslari.org](https://yazilimcimaaslari.org) | **Google Sheets** | 27 tech roles, 1,223 responses (2026) |
| 10 | **Kariyer.net** | [kariyer.net/maaslar](https://www.kariyer.net/maaslar) | Apify scraper API | 9,132+ positions |
| 11 | **Glassdoor Turkey** | [glassdoor.com](https://www.glassdoor.com/Salaries/turkey-salary-SRCH_IL.0,6_IN238.htm) | No (commercial) | Hundreds of job titles |
| 12 | **PayScale Turkey** | [payscale.com](https://www.payscale.com/research/TR/Job) | No (commercial) | 120+ job titles |
| 13 | **Levels.fyi Turkey** | [levels.fyi](https://www.levels.fyi/t/software-engineer/locations/turkey) | No | 15-20 tech roles (verified) |
| 14 | **Memurlar.net** | [memurlar.net/maas](https://www.memurlar.net/maas/) | No (web calc) | All civil service positions |

## Union / Baseline Reports

| # | Source | URL | Coverage |
|---|--------|-----|----------|
| 15 | **TÜRK-İŞ Açlık/Yoksulluk Sınırı** | [turkis.org.tr](https://www.turkis.org.tr/category/aclik-yoksulluk/) | Monthly living cost baseline |
| 16 | **DİSK Ücret Raporları** | [disk.org.tr](https://disk.org.tr/) | Wage analysis by sector |
| 17 | **SalaryInsights.com.tr** | [salaryinsights.com.tr](https://www.salaryinsights.com.tr/) | Anonymous salary comparisons |

## Best for Automation (downloadable/API)

1. **yazilimcimaaslari.org** — raw data freely available via Google Sheets
2. **TÜİK Kazanç Yapısı** — official Excel tables, microdata on request
3. **SGK Yıllıkları** — downloadable ZIP archives (2007-2024)
4. **HMB/BUMKO** — official civil servant salary parameters
5. **Kariyer.net via Apify** — third-party scraper with OpenAPI spec
6. **Önceki Yazılımcı** — JSON dataset in this repo
