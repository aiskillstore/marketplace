#!/usr/bin/env python3
"""
KVKK Uyum Hızlı Kontrol Aracı
Bir metin veya URL'yi analiz ederek temel KVKK uyum noktalarını kontrol eder.

Kullanım:
  python kvkk_check.py --text "gizlilik politikası metni"
  python kvkk_check.py --file gizlilik.txt
"""

import sys
import re
import argparse
from dataclasses import dataclass, field
from typing import List

@dataclass
class KVKKBulgu:
    kategori: str  # "kritik", "önemli", "öneri"
    mesaj: str
    madde: str = ""

ZORUNLU_IFADELER = {
    "veri_sorumlusu": [
        r"veri sorumlusu",
        r"data controller",
    ],
    "aydinlatma": [
        r"aydınlatma",
        r"bilgilendirme",
    ],
    "haklar": [
        r"madde 11",
        r"haklarınız",
        r"başvuru hakkı",
        r"silme.*talep",
        r"düzeltme.*talep",
    ],
    "iletisim": [
        r"@",
        r"iletişim",
        r"başvuru",
    ],
    "amac": [
        r"amaç",
        r"işlenme amacı",
        r"neden işliyoruz",
    ],
    "saklama": [
        r"saklama süresi",
        r"imha",
        r"ne kadar süre",
        r"silineceğini",
    ],
}

RISK_IFADELERI = [
    (r"üçüncü taraflarla paylaşabiliriz", "Belirsiz aktarım ifadesi", "Madde 8"),
    (r"iş ortaklarımızla paylaşabiliriz", "Belirsiz aktarım ifadesi", "Madde 8"),
    (r"önceden işaretli", "Önceden işaretli onay kutusu geçersizdir", "Madde 3"),
    (r"hizmetlerimizi kullanarak kabul etmiş", "Kullanımla rıza geçersizdir", "Madde 3"),
    (r"gdpr", "GDPR şablonu kullanılmış, KVKK'ya uyarlanmalı", "Genel"),
    (r"privacy policy", "İngilizce bölüm var, Türkçe olmalı", "Genel"),
]

def metni_analiz_et(metin: str) -> List[KVKKBulgu]:
    bulgular = []
    metin_kucuk = metin.lower()

    # Zorunlu ifade kontrolü
    for kategori, ifadeler in ZORUNLU_IFADELER.items():
        bulundu = any(re.search(ifade, metin_kucuk) for ifade in ifadeler)
        if not bulundu:
            kategori_adi = {
                "veri_sorumlusu": "Veri sorumlusu kimliği",
                "aydinlatma": "Aydınlatma yükümlülüğü başlığı",
                "haklar": "İlgili kişi hakları (Madde 11)",
                "iletisim": "İletişim/başvuru bilgileri",
                "amac": "Veri işleme amacı",
                "saklama": "Saklama süresi bilgisi",
            }.get(kategori, kategori)

            oncelik = "kritik" if kategori in ["veri_sorumlusu", "haklar", "aydinlatma"] else "önemli"
            bulgular.append(KVKKBulgu(
                kategori=oncelik,
                mesaj=f"{kategori_adi} bulunamadı",
                madde="Madde 10" if kategori != "haklar" else "Madde 11"
            ))

    # Risk ifadesi kontrolü
    for ifade, mesaj, madde in RISK_IFADELERI:
        if re.search(ifade, metin_kucuk):
            bulgular.append(KVKKBulgu(
                kategori="önemli",
                mesaj=mesaj,
                madde=madde
            ))

    # Özel nitelikli veri kontrolü
    ozel_veri_ifadeleri = ["sağlık", "hastalık", "engellilik", "din", "mezhep",
                           "siyasi", "etnik", "biyometrik", "genetik", "cinsel"]
    for ifade in ozel_veri_ifadeleri:
        if ifade in metin_kucuk:
            bulgular.append(KVKKBulgu(
                kategori="kritik",
                mesaj=f"Özel nitelikli veri ({ifade}) işleniyor - güçlendirilmiş önlem gerekli",
                madde="Madde 6"
            ))

    # Yurt dışı aktarım kontrolü
    yurtdisi = ["yurt dışı", "yurtdışı", "abroad", "overseas", "aws", "google cloud",
                "azure", "firebase", "stripe", "paypal"]
    for ifade in yurtdisi:
        if ifade in metin_kucuk:
            bulgular.append(KVKKBulgu(
                kategori="önemli",
                mesaj=f"Yurt dışı aktarım tespit edildi ({ifade}) - Madde 9 gereklilikleri kontrol edilmeli",
                madde="Madde 9"
            ))
            break

    return bulgular

def puan_hesapla(bulgular: List[KVKKBulgu]) -> int:
    kritik_sayi = sum(1 for b in bulgular if b.kategori == "kritik")
    onemli_sayi = sum(1 for b in bulgular if b.kategori == "önemli")

    puan = 100
    puan -= kritik_sayi * 20
    puan -= onemli_sayi * 10
    return max(0, puan)

def rapor_olustur(metin: str, kaynak: str = "girdi") -> str:
    from datetime import datetime

    bulgular = metni_analiz_et(metin)
    puan = puan_hesapla(bulgular)

    kritik = [b for b in bulgular if b.kategori == "kritik"]
    onemli = [b for b in bulgular if b.kategori == "önemli"]

    durum = "Uyumlu ✅" if puan >= 80 else "Kısmen Uyumlu ⚠️" if puan >= 50 else "Uyumsuz ❌"

    rapor = f"""
╔══════════════════════════════════════════════════════════╗
║           KVKK UYUM DENETİM RAPORU                       ║
╚══════════════════════════════════════════════════════════╝

Tarih      : {datetime.now().strftime('%d/%m/%Y %H:%M')}
Kaynak     : {kaynak}
Uyum Puanı : {puan}/100
Durum      : {durum}
"""

    if kritik:
        rapor += "\n🔴 KRİTİK BULGULAR (Acil Düzeltme Gerekli):\n"
        for b in kritik:
            madde_str = f" [{b.madde}]" if b.madde else ""
            rapor += f"  • {b.mesaj}{madde_str}\n"

    if onemli:
        rapor += "\n🟡 ÖNEMLİ BULGULAR (30 Gün İçinde Düzeltilmeli):\n"
        for b in onemli:
            madde_str = f" [{b.madde}]" if b.madde else ""
            rapor += f"  • {b.mesaj}{madde_str}\n"

    if not bulgular:
        rapor += "\n✅ Temel KVKK gereklilikleri karşılanıyor.\n"

    rapor += f"""
📋 TAVSİYELER:
  • Bir avukat tarafından hukuki inceleme yaptırın
  • VERBİS kaydınızı güncel tutun
  • Çalışanlarınıza yılda en az bir KVKK eğitimi verin
  • Veri ihlali müdahale planı hazırlayın

⚠️  Bu rapor bilgilendirme amaçlıdır, hukuki tavsiye değildir.
"""
    return rapor

def main():
    parser = argparse.ArgumentParser(
        description="KVKK Uyum Hızlı Kontrol Aracı"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Analiz edilecek metin")
    group.add_argument("--file", help="Analiz edilecek dosya yolu")

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                metin = f.read()
            kaynak = args.file
        except FileNotFoundError:
            print(f"Hata: '{args.file}' dosyası bulunamadı.", file=sys.stderr)
            sys.exit(1)
    else:
        metin = args.text
        kaynak = "komut satırı"

    if len(metin.strip()) < 50:
        print("Uyarı: Metin çok kısa, analiz sınırlı olabilir.", file=sys.stderr)

    print(rapor_olustur(metin, kaynak))

if __name__ == "__main__":
    main()
