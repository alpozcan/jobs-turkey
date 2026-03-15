"""Generate heuristic AI exposure scores for preview (no API key needed)."""
import json

HEURISTIC_SCORES = {
    # teknoloji
    "yazilim-gelistirici": (8.5, "Yazılım geliştirme tamamen dijital bir meslektir. YZ kod yazma, hata ayıklama ve mimari tasarım konularında hızla ilerlemektedir. Mesleğin yeniden yapılanması kaçınılmazdır."),
    "veri-bilimci": (8.0, "Veri analizi, model oluşturma ve raporlama görevlerinin çoğu YZ tarafından otomatikleştirilebilir. Ancak iş problemlerini anlama ve yorumlama hâlâ insan yargısı gerektirir."),
    "veri-muhendisi": (7.5, "Veri boru hatları ve ETL süreçleri otomasyona oldukça açıktır. Altyapı tasarımı ve karmaşık sistem entegrasyonu hâlâ insan uzmanlığı gerektirir."),
    "veri-analisti": (8.5, "Veri analizi ve raporlama, YZ'nin en güçlü olduğu alanlardan biridir. Rutin analizler büyük ölçüde otomatikleştirilebilir."),
    "yapay-zeka-muhendisi": (7.0, "YZ mühendisliği paradoks olarak YZ tarafından en çok etkilenecek alanlardan biridir, ancak son teknoloji araştırma ve yenilik hâlâ insan yaratıcılığı gerektirir."),
    "makine-ogrenmesi-muhendisi": (7.5, "Model eğitimi ve optimizasyonu giderek daha fazla otomatikleştiriliyor. AutoML araçları birçok standart görevi halledebiliyor."),
    "devops-muhendisi": (7.0, "Altyapı yönetimi, CI/CD ve izleme süreçleri YZ destekli araçlarla otomatikleştiriliyor. Karmaşık sistem tasarımı hâlâ insan gerektirir."),
    "sistem-yoneticisi": (6.5, "Sistem izleme ve rutin bakım otomatikleştirilebilir. Ancak fiziksel donanım müdahalesi ve karmaşık sorun giderme insan gerektirir."),
    "bilgi-guvenligi-uzmani": (6.0, "Tehdit tespiti ve analizi YZ ile güçlendirilebilir ancak güvenlik stratejisi, olay müdahalesi ve etik hacking insan uzmanlığı gerektirir."),
    "mobil-uygulama-gelistirici": (8.5, "Mobil uygulama geliştirme tamamen dijital bir iştir. YZ kod üretimi ve tasarım araçları bu alanda hızla ilerliyor."),
    "oyun-gelistiricisi": (7.0, "Oyun mekanikleri ve asset üretimi YZ ile desteklenebilir ancak yaratıcı tasarım ve oyuncu deneyimi tasarımı hâlâ insan yaratıcılığı gerektirir."),
    "qa-test-muhendisi": (8.0, "Test otomasyonu ve hata tespiti YZ'nin en güçlü olduğu alanlardan biridir. Manuel test süreçleri büyük ölçüde otomatikleştirilecektir."),
    "urun-yoneticisi": (6.0, "Pazar analizi ve kullanıcı araştırması YZ ile desteklenebilir ancak vizyon belirleme, paydaş yönetimi ve stratejik kararlar insan yargısı gerektirir."),
    "proje-yoneticisi": (6.0, "Planlama, raporlama ve kaynak yönetimi otomatikleştirilebilir. Ekip yönetimi ve paydaş iletişimi insan becerileri gerektirir."),
    "yazilim-mimari": (7.0, "Mimari kalıplar ve tasarım kararları YZ tarafından önerilse de, karmaşık sistem tasarımı ve teknik liderlik insan deneyimi gerektirir."),
    "is-analisti": (7.5, "İş gereksinimlerinin analizi ve dokümantasyonu YZ ile büyük ölçüde otomatikleştirilebilir. Paydaş görüşmeleri ve müzakere insan gerektirir."),
    "gomulu-yazilim-gelistiricisi": (6.0, "Donanım-yazılım etkileşimi ve fiziksel test gereksinimleri nedeniyle saf yazılıma göre daha düşük maruziyet. Ancak kod yazma kısmı YZ'den etkilenir."),
    "sap-erp-danismani": (7.0, "ERP yapılandırma ve raporlama otomatikleştirilebilir. İş süreçleri analizi ve müşteri danışmanlığı insan etkileşimi gerektirir."),
    "veritabani-yoneticisi": (7.0, "Veritabanı optimizasyonu, yedekleme ve rutin yönetim görevleri otomasyona açıktır. Karmaşık mimari kararlar hâlâ insan gerektirir."),
    "ui-ux-tasarimcisi": (7.5, "YZ tasarım araçları hızla gelişiyor. Görsel tasarım ve prototipleme otomatikleştirilebilir ancak kullanıcı araştırması ve empati insan gerektirir."),
    # finans
    "muhasebeci": (8.0, "Muhasebe tamamen dijital bir meslektir. Defter tutma, vergi hesaplama ve raporlama YZ tarafından büyük ölçüde otomatikleştirilecektir."),
    "mali-musavir": (7.0, "Mali danışmanlık ve vergi planlaması YZ ile desteklenebilir. Müşteri ilişkileri ve karmaşık mevzuat yorumu hâlâ insan gerektirir."),
    "banka-veznedari": (9.0, "Dijital bankacılık ve ATM'ler bu mesleği zaten daraltmıştır. YZ ile birlikte kalan işlemler de otomatikleşecektir."),
    "sigorta-uzmani": (7.5, "Risk değerlendirme ve poliçe işlemleri YZ ile otomatikleştirilebilir. Müşteri ilişkileri ve karmaşık hasar değerlendirmesi insan gerektirir."),
    "finansal-analist": (8.0, "Finansal modelleme, piyasa analizi ve raporlama YZ'nin en güçlü olduğu alanlardan biridir."),
    # hukuk
    "avukat": (6.5, "Hukuki araştırma ve belge hazırlama YZ ile otomatikleştirilebilir. Mahkemede savunma, müzakere ve müvekkil ilişkileri insan gerektirir."),
    "hakim": (4.0, "Yargılama süreci insan yargısı, empati ve toplumsal değerlendirme gerektirir. Hukuki araştırma YZ ile desteklenebilir."),
    "noter": (7.5, "Noter işlemleri büyük ölçüde dijital ve standart prosedürlerden oluşur. Dijitalleşme ile birçok noter işlevi otomatikleşebilir."),
    # saglik
    "pratisyen-hekim": (4.0, "Hasta muayenesi ve fiziksel değerlendirme insan etkileşimi gerektirir. Teşhis desteği YZ ile güçlendirilebilir."),
    "uzman-hekim": (3.5, "Cerrahi müdahale ve karmaşık teşhis süreçleri insan uzmanlığı gerektirir. YZ görüntüleme ve analiz alanlarında yardımcı olabilir."),
    "dis-hekimi": (3.0, "Diş tedavisi tamamen fiziksel beceri ve hasta etkileşimi gerektirir. Teşhis aşamasında YZ yardımcı olabilir."),
    "eczaci": (6.0, "İlaç etkileşim kontrolü ve reçete doğrulama otomatikleştirilebilir. Hasta danışmanlığı insan etkileşimi gerektirir."),
    "hemsire": (3.0, "Hemşirelik bakımı fiziksel temas, empati ve hasta etkileşimi gerektirir. Dokümantasyon ve izleme YZ ile desteklenebilir."),
    "veteriner": (3.0, "Hayvan muayenesi ve tedavisi fiziksel beceri gerektirir. Teşhis aşamasında YZ yardımcı olabilir."),
    "psikolog": (4.5, "Terapi ve danışmanlık derin insan etkileşimi gerektirir. Değerlendirme araçları ve ilk tarama YZ ile desteklenebilir."),
    "fizyoterapist": (2.5, "Fizik tedavi doğrudan fiziksel temas ve müdahale gerektirir. Egzersiz planlaması YZ ile desteklenebilir."),
    "ebe": (1.5, "Doğum süreci yoğun fiziksel ve duygusal destek gerektirir. YZ maruziyeti çok düşüktür."),
    # egitim
    "ilkogretim-ogretmeni": (4.5, "Çocuk gelişimi ve sınıf yönetimi insan etkileşimi gerektirir. Ders materyali hazırlama ve değerlendirme YZ ile desteklenebilir."),
    "ortaogretim-ogretmeni": (5.0, "Konu anlatımı ve ödev değerlendirmesi YZ ile desteklenebilir. Öğrenci motivasyonu ve mentorluk insan gerektirir."),
    "universite-ogretim-uyesi": (5.5, "Araştırma ve makale yazımı YZ'den etkilenir. Ancak bilimsel yenilik, öğrenci danışmanlığı ve laboratuvar çalışması insan gerektirir."),
    "okul-oncesi-ogretmeni": (2.0, "Küçük çocuklarla etkileşim, oyun yoluyla öğrenme ve duygusal destek tamamen insan etkileşimi gerektirir."),
    # muhendislik
    "insaat-muhendisi": (5.0, "Yapısal analiz ve proje planlaması YZ ile desteklenebilir. Saha denetimi ve fiziksel değerlendirme insan gerektirir."),
    "makine-muhendisi": (5.0, "Tasarım ve simülasyon YZ ile desteklenebilir. Prototipleme ve üretim denetimi fiziksel mevcudiyet gerektirir."),
    "elektrik-muhendisi": (5.0, "Devre tasarımı ve analizi YZ ile desteklenebilir. Saha çalışması ve kurulum denetimi fiziksel mevcudiyet gerektirir."),
    "endustri-muhendisi": (6.5, "Süreç optimizasyonu ve veri analizi YZ'nin güçlü olduğu alanlardır. Ancak fabrika ziyaretleri ve uygulama denetimi insan gerektirir."),
    "mimar": (5.5, "Tasarım ve çizim araçları YZ ile güçleniyor. Yaratıcı vizyon, müşteri iletişimi ve saha denetimi insan gerektirir."),
    "cevre-muhendisi": (5.0, "Çevresel etki değerlendirmesi ve veri analizi YZ ile desteklenebilir. Saha çalışması ve denetim fiziksel mevcudiyet gerektirir."),
    "gida-muhendisi": (4.5, "Gıda analizi ve kalite kontrol testleri kısmen otomatikleştirilebilir. Üretim hattı denetimi fiziksel mevcudiyet gerektirir."),
    # medya
    "grafik-tasarimci": (8.0, "YZ görsel üretim araçları (Midjourney, DALL-E) grafik tasarımı köklü şekilde değiştiriyor. Yaratıcı yönetmenlik hâlâ insan gerektirir."),
    "gazeteci": (7.0, "Haber yazımı ve araştırma YZ tarafından desteklenebilir. Saha gazetecilik, röportaj ve editoryal yargı insan gerektirir."),
    "yazar": (7.5, "YZ metin üretimi hızla gelişiyor. Yaratıcı yazarlık ve özgün ses hâlâ insan yaratıcılığı gerektirir ancak içerik üretimi otomatikleşiyor."),
    "cevirmen": (9.0, "Makine çevirisi çok ileri seviyeye ulaşmıştır. Edebi çeviri ve kültürel uyarlama hâlâ insan gerektirir ancak rutin çeviri işleri YZ'ye geçiyor."),
    "fotografci": (5.0, "YZ görsel üretim ve düzenleme araçları gelişiyor. Ancak etkinlik fotoğrafçılığı ve stüdyo çekimi fiziksel mevcudiyet gerektirir."),
    "film-video-yapimcisi": (5.5, "Video düzenleme ve efekt üretimi YZ ile desteklenebilir. Yönetmenlik ve çekim fiziksel mevcudiyet gerektirir."),
    "sosyal-medya-uzmani": (7.5, "İçerik üretimi, analiz ve planlama YZ ile büyük ölçüde otomatikleştirilebilir. Marka stratejisi ve topluluk yönetimi insan gerektirir."),
    # yonetim
    "satis-muduru": (5.0, "Satış analizi ve raporlama otomatikleştirilebilir. Ekip motivasyonu, müşteri ilişkileri ve müzakere insan gerektirir."),
    "pazarlama-uzmani": (7.0, "Dijital pazarlama, SEO ve içerik üretimi YZ tarafından desteklenebilir. Strateji ve marka yönetimi insan yargısı gerektirir."),
    "insan-kaynaklari-uzmani": (6.5, "CV tarama, işe alım ve performans analizi YZ ile otomatikleştirilebilir. Çalışan ilişkileri ve kültür yönetimi insan gerektirir."),
    "yonetim-danismani": (6.5, "Analiz ve raporlama YZ ile desteklenebilir. Müşteri ilişkileri, sunum ve strateji geliştirme insan becerileri gerektirir."),
    "genel-mudur": (4.0, "Üst düzey liderlik, vizyon belirleme ve paydaş yönetimi insan becerileri gerektirir. Karar destek sistemleri YZ ile güçlenebilir."),
    "imalat-muduru": (4.0, "Üretim yönetimi fiziksel mevcudiyet ve fabrika denetimi gerektirir. Planlama ve optimizasyon YZ ile desteklenebilir."),
    # hizmet
    "tezgahtar-satici": (4.0, "Perakende satış müşteri etkileşimi ve fiziksel mevcudiyet gerektirir. Self-checkout ve e-ticaret bazı işlevleri azaltmıştır."),
    "garson": (2.0, "Garsonluk fiziksel servis, müşteri iletişimi ve hızlı tepki gerektirir. YZ maruziyeti çok düşüktür."),
    "asci": (2.0, "Yemek pişirme tamamen fiziksel bir beceridir. Lezzet, sunum ve yaratıcılık insan gerektirir."),
    "kuafor": (1.0, "Saç kesimi ve bakım tamamen fiziksel beceri ve müşteri etkileşimi gerektirir."),
    "guvenlik-gorevlisi": (3.0, "Fiziksel güvenlik mevcudiyet gerektirir. Kamera izleme ve tehdit tespiti YZ ile desteklenebilir."),
    "temizlik-iscisi": (1.0, "Temizlik tamamen fiziksel bir iştir. Robot süpürgeler bazı görevleri üstlenebilir ancak genel temizlik hâlâ insan gerektirir."),
    "kasiyer": (9.0, "Self-checkout ve dijital ödeme sistemleri kasiyer ihtiyacını büyük ölçüde azaltmıştır."),
    "tur-rehberi": (4.0, "Tur rehberliği fiziksel mevcudiyet, hikaye anlatımı ve kültürel bilgi gerektirir. Sesli rehberler bazı işlevleri üstlenebilir."),
    "otel-resepsiyonisti": (7.0, "Online check-in ve self-servis kiosklar resepsiyon ihtiyacını azaltıyor. Müşteri memnuniyeti hâlâ insan etkileşimi gerektirir."),
    "cagri-merkezi-elemani": (9.0, "Çağrı merkezi işlemleri YZ chatbot ve sesli asistanlar tarafından büyük ölçüde otomatikleştirilmektedir."),
    "kurye-dagitici": (4.5, "Kuryelik fiziksel teslimat gerektirir. Rota optimizasyonu YZ ile yapılır. Otonom araçlar gelecekte etkili olabilir."),
    # buro
    "buro-elemani": (8.5, "Büro işleri tamamen dijitaldir. Dosyalama, yazışma ve veri işleme YZ tarafından otomatikleştirilebilir."),
    "sekreter": (8.5, "Randevu yönetimi, yazışma ve organizasyon görevleri dijital araçlarla otomatikleştirilebilir."),
    "veri-giris-elemani": (10.0, "Veri girişi rutin dijital bilgi işlemedir. YZ bu işlerin neredeyse tamamını bugün bile yapabilir."),
    "muhasebe-elemani": (8.5, "Defter tutma ve fatura işlemleri otomasyona en açık görevlerdendir."),
    # tarim
    "ciftci": (1.0, "Çiftçilik fiziksel emek, doğa koşullarına uyum ve elle hasat gerektirir. Hassas tarım YZ ile desteklenebilir ancak temel iş fizikseldir."),
    "hayvancilik-iscisi": (1.0, "Hayvancılık hayvan bakımı ve fiziksel mevcudiyet gerektirir. YZ maruziyeti çok düşüktür."),
    "balikci": (0.5, "Balıkçılık denizde fiziksel mevcudiyet ve el becerisi gerektirir. YZ maruziyeti en düşük mesleklerdendir."),
    "ormancilik-iscisi": (1.0, "Ormancılık açık havada fiziksel çalışma gerektirir. YZ maruziyeti çok düşüktür."),
    # zanaat
    "insaat-iscisi": (1.0, "İnşaat işçiliği ağır fiziksel emek ve saha çalışması gerektirir. YZ maruziyeti çok düşüktür."),
    "tesisatci": (1.5, "Tesisat işleri fiziksel beceri ve saha çalışması gerektirir. Her iş benzersizdir ve yerinde müdahale gerekir."),
    "elektrikci": (2.0, "Elektrik işleri fiziksel beceri ve güvenlik bilinci gerektirir. Rutin kurulumlar dışında her iş farklıdır."),
    "kaynakci": (1.5, "Kaynak işi yüksek fiziksel beceri ve hassasiyet gerektirir. Robot kaynak fabrikada kullanılır ancak saha kaynağı insan gerektirir."),
    "marangoz": (1.5, "Marangozluk fiziksel beceri ve yaratıcılık gerektirir. CNC makineler bazı görevleri üstlenir ancak özel işler insan gerektirir."),
    "boyaci": (1.0, "Boyacılık fiziksel emek ve yüzey hazırlığı gerektirir. YZ maruziyeti çok düşüktür."),
    "oto-tamirci": (2.0, "Araç tamiri fiziksel beceri, teşhis ve elle müdahale gerektirir. Teşhis sistemleri YZ ile desteklenebilir."),
    "beyaz-esya-tamircisi": (2.0, "Beyaz eşya tamiri fiziksel müdahale ve teşhis gerektirir."),
    "terzi": (2.0, "Terzilik fiziksel beceri ve müşteri ölçüsü gerektirir. Hazır giyim üretimi otomatikleştirilebilir ancak özel dikim insan gerektirir."),
    "firinci-pastaci": (1.5, "Fırıncılık fiziksel beceri, lezzet bilgisi ve el işçiliği gerektirir."),
    "kasap": (1.5, "Kasaplık fiziksel beceri ve hijyen bilgisi gerektirir. Endüstriyel kesim otomatikleştirilebilir ancak perakende kasaplık insan gerektirir."),
    "kuyumcu": (2.5, "Kuyumculuk el işçiliği ve sanatsal beceri gerektirir. CAD tasarımı YZ ile desteklenebilir."),
    # ulasim
    "agir-vasita-soforu": (4.0, "Otonom araç teknolojisi ilerliyor ancak Türkiye'nin altyapısı ve trafik koşulları göz önüne alındığında kısa vadede tam otomasyon zor görünüyor."),
    "otobus-soforu": (4.0, "Toplu taşıma otomasyonu bazı şehirlerde test ediliyor. Türkiye'de kısa vadede yaygınlaşması beklenmemektedir."),
    "taksi-soforu": (4.5, "Otonom taksi teknolojisi gelişiyor. Türkiye'nin trafik koşullarında tam otomasyon orta vadede olası."),
    "is-makinesi-operatoru": (3.0, "İş makineleri zorlu arazi koşullarında çalışır. Otonom sistemler gelişse de, saha koşulları insan operatör gerektirir."),
    "forklift-operatoru": (5.0, "Depo otomasyonu ve otonom forkliftler hızla gelişmektedir. Kapalı ortamlarda otomasyon daha kolaydır."),
    # imalat
    "tekstil-iscisi": (3.0, "Tekstil üretimi kısmen otomatikleştirilebilir. Kalite kontrol ve bakım fiziksel mevcudiyet gerektirir."),
    "paketleme-iscisi": (5.0, "Paketleme ve ambalaj otomasyonu fabrika ortamında yaygınlaşmaktadır."),
    "fabrika-operatoru": (4.0, "Makine operatörlüğü fiziksel mevcudiyet ve müdahale gerektirir. Otomasyon bazı süreçleri etkiler."),
    "gida-isleme-iscisi": (3.5, "Gıda işleme kısmen otomatikleştirilebilir. Hijyen denetimi ve kalite kontrol insan gerektirir."),
    # kamu
    "polis-memuru": (3.0, "Suç soruşturması ve toplum güvenliği fiziksel mevcudiyet ve insan yargısı gerektirir. Veri analizi YZ ile desteklenebilir."),
    "itfaiyeci": (1.0, "İtfaiyecilik fiziksel güç, cesaret ve acil müdahale gerektirir. YZ maruziyeti çok düşüktür."),
    "devlet-memuru": (6.5, "Bürokrasi ve evrak işlemleri dijitalleştirilebilir. Vatandaş hizmetleri ve karar süreçleri insan gerektirir."),
    "vergi-memuru": (7.0, "Vergi hesaplama ve denetim dijital süreçlerdir. YZ ile otomatikleştirilebilir ancak karmaşık vakalar insan gerektirir."),
    # arastirma
    "ekonomist": (7.0, "Ekonomik analiz ve modelleme YZ tarafından desteklenebilir. Politika yorumu ve strateji önerisi insan yargısı gerektirir."),
    "sosyolog": (5.5, "Sosyal araştırma ve veri analizi YZ ile desteklenebilir. Saha çalışması ve kültürel yorumlama insan gerektirir."),
    "biyolog": (4.5, "Laboratuvar çalışması ve saha araştırması fiziksel mevcudiyet gerektirir. Veri analizi ve genom çalışmaları YZ ile desteklenebilir."),
    "kimyager": (4.5, "Laboratuvar deneyleri fiziksel mevcudiyet gerektirir. Moleküler modelleme ve veri analizi YZ ile desteklenebilir."),
    # kultur
    "muzisyen": (4.0, "Canlı performans ve yaratıcı beste insan yeteneği gerektirir. YZ müzik üretimi gelişse de, canlı performans ikame edilemez."),
    "sporcu": (0.5, "Atletik performans tamamen fiziksel yetenek ve antrenman gerektirir. Analiz araçları YZ ile desteklenebilir."),
    "ic-mimar": (6.0, "YZ tasarım araçları iç mekan görselleştirmede hızla gelişiyor. Müşteri ilişkileri ve saha denetimi insan gerektirir."),
    # ticaret
    "esnaf-dukkan-sahibi": (3.0, "Esnaf fiziksel mevcudiyet ve müşteri ilişkileri gerektirir. E-ticaret bazı işlevleri dijitalleştirmiştir."),
    "arac-yedek-parca": (3.5, "Yedek parça satışı ürün bilgisi ve müşteri etkileşimi gerektirir. Online satış kanalları büyüyor."),
    "emlakci": (5.5, "Emlak arama ve değerleme YZ ile desteklenebilir. Müşteri ilişkileri ve saha gezileri insan gerektirir."),
    "gumruk-musaviri": (7.0, "Gümrük beyanname işlemleri dijitaldir ve büyük ölçüde otomatikleştirilebilir."),
    "dis-ticaret-uzmani": (6.5, "Belge hazırlama ve lojistik koordinasyonu otomatikleştirilebilir. Müşteri müzakeresi ve ilişki yönetimi insan gerektirir."),
}

def main():
    with open("occupations.json") as f:
        occupations = json.load(f)

    scores = []
    for occ in occupations:
        slug = occ["slug"]
        if slug in HEURISTIC_SCORES:
            exposure, rationale = HEURISTIC_SCORES[slug]
        else:
            exposure, rationale = 5.0, "Bu meslek için tahmini YZ maruziyet skoru atanmıştır."
        scores.append({
            "slug": slug,
            "title": occ["title"],
            "exposure": exposure,
            "rationale": rationale,
        })

    with open("scores.json", "w") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

    vals = [s["exposure"] for s in scores]
    avg = sum(vals) / len(vals)
    print(f"Generated {len(scores)} heuristic scores")
    print(f"Average exposure: {avg:.1f}")
    by_tier = {"0-3": 0, "4-5": 0, "6-7": 0, "8-10": 0}
    for v in vals:
        if v <= 3: by_tier["0-3"] += 1
        elif v <= 5: by_tier["4-5"] += 1
        elif v <= 7: by_tier["6-7"] += 1
        else: by_tier["8-10"] += 1
    for k, v in by_tier.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
