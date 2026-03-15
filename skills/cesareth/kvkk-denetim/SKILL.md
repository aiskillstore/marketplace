---
name: kvkk-denetim
description: Türkiye Kişisel Verilerin Korunması Kanunu (KVKK / 6698 sayılı Kanun) uyum denetimi. Gizlilik politikası, aydınlatma metni, açık rıza formu oluşturma ve mevcut metinleri KVKK'ya uygunluk açısından analiz etme. Türk şirketleri için GDPR muadili uyum desteği.
license: MIT
metadata:
  author: hermes-turkce-skills
  version: "1.0"
  language: Turkish
  region: TR
  legal-disclaimer: "Bu araç hukuki danışmanlık değildir. Nihai kararlar için avukat görüşü alınmalıdır."
compatibility: Türk hukuku kapsamında faaliyet gösteren şirketler için
---

# KVKK Denetim Aracı

⚠️ **Yasal Uyarı**: Bu araç bilgilendirme amaçlıdır. Bağlayıcı hukuki tavsiye değildir. Nihai kararlar için bir hukuk danışmanına başvurun.

## KVKK Nedir?

6698 sayılı Kişisel Verilerin Korunması Kanunu, Türkiye'de kişisel verilerin işlenmesini düzenleyen temel kanundur. AB'nin GDPR'ına benzer şekilde çalışır.

**Yürürlük:** 7 Nisan 2016
**Denetim Kurumu:** Kişisel Verileri Koruma Kurumu (KVKK)
**Web:** kvkk.gov.tr

## Denetim Süreci

Bir metin veya uygulama KVKK denetimi yapılırken şu adımları izle:

### 1. Veri Envanteri Kontrolü
- [ ] Hangi kişisel veriler toplanıyor? (ad, e-posta, TC kimlik, konum vb.)
- [ ] Özel nitelikli veri var mı? (sağlık, din, biyometrik, ceza kaydı)
- [ ] Veriler nerede saklanıyor? (Türkiye içi mi, yurt dışı mı?)
- [ ] Ne kadar süre saklanıyor?
- [ ] Kimlerle paylaşılıyor?

### 2. Hukuki Dayanak Kontrolü
Her veri işleme faaliyeti için mutlaka bir hukuki dayanak olmalı:
- **Açık rıza** (en yaygın ama en kırılgan)
- **Kanunlarda açıkça öngörülmesi**
- **Sözleşmenin kurulması veya ifası**
- **Hukuki yükümlülüğün yerine getirilmesi**
- **İlgili kişinin hayati menfaatlerinin korunması**
- **Bir hakkın tesisi, kullanılması veya korunması**
- **Veri sorumlusunun meşru menfaati**

### 3. Aydınlatma Metni Kontrolü
Aydınlatma metni şunları içermeli:
- [ ] Veri sorumlusunun kimliği ve iletişim bilgileri
- [ ] İşlenen kişisel verilerin neler olduğu
- [ ] Kişisel verilerin işlenme amacı
- [ ] Kişisel verilerin kimlere aktarılabileceği
- [ ] Kişisel verilerin toplanma yöntemi ve hukuki sebebi
- [ ] İlgili kişinin hakları (KVKK Madde 11)
- [ ] Başvuru yöntemi

### 4. İlgili Kişi Hakları Kontrolü (Madde 11)
Şirketin aşağıdaki haklara cevap verebilme kapasitesi var mı?
- [ ] Kişisel verilerin işlenip işlenmediğini öğrenme
- [ ] Kişisel verileri işlenmişse buna ilişkin bilgi talep etme
- [ ] İşlenme amacını öğrenme
- [ ] Aktarılan üçüncü kişileri bilme
- [ ] Eksik/yanlış verilerin düzeltilmesini isteme
- [ ] Silinmesini veya yok edilmesini isteme
- [ ] Otomatik işleme sonuçlarına itiraz
- [ ] Zararın giderilmesini talep etme

### 5. Veri Güvenliği Kontrolü
- [ ] Teknik önlemler alınmış mı? (şifreleme, erişim kontrolü)
- [ ] İdari önlemler var mı? (gizlilik sözleşmeleri, eğitim)
- [ ] İhlal bildirim prosedürü var mı? (72 saat kurul bildirimi)

## Aydınlatma Metni Şablonu

```
[ŞİRKET ADI] KİŞİSEL VERİLERİN KORUNMASI AYDINLATMA METNİ

Veri Sorumlusu: [Şirket Adı], [Adres]
İletişim: [E-posta], [Telefon]

1. İŞLENEN KİŞİSEL VERİLER
[hangi veriler - örn: ad soyad, e-posta, telefon]

2. VERİLERİN İŞLENME AMACI
[neden işleniyor - örn: sipariş yönetimi, müşteri hizmetleri]

3. VERİLERİN KİMLERE AKTARILABİLECEĞİ
[kimlerle paylaşılıyor - örn: kargo firmaları, ödeme sistemleri]

4. VERİLERİN TOPLANMA YÖNTEMİ VE HUKUKİ SEBEBİ
[nasıl ve hangi yasal dayanakla - örn: web formu, sözleşme ifası]

5. HAKLARINIZ (KVKK Madde 11)
Aşağıdaki haklarınızı [iletişim@sirket.com] adresine yazılı başvuru ile kullanabilirsiniz:
- Kişisel verilerinizin işlenip işlenmediğini öğrenme
- İşlenmişse bilgi talep etme
- Düzeltme, silme veya yok etme talep etme
- Otomatik işleme sonuçlarına itiraz
- Zararın giderilmesini talep etme

Son güncelleme: [Tarih]
```

## Açık Rıza Metni Şablonu

```
AÇIK RIZA BEYANI

[Şirket Adı] tarafından [veri türü] kişisel verilerimin [amaç] amacıyla
işlenmesine özgür irademle, bilgilendirilerek ve açıkça rıza gösteriyorum.

Bu rızamı dilediğim zaman geri alabileceğimi biliyorum.

Tarih: ___/___/______
Ad Soyad: _______________
İmza: _______________
```

## Sık Yapılan KVKK İhlalleri

| İhlal | Risk |
|-------|------|
| Aydınlatma metni eksik veya anlaşılmaz | İdari para cezası |
| Açık rıza önceden işaretli kutu | Geçersiz rıza |
| Veri yurt dışına aktarım bildirimi yok | Ceza + dava |
| Veri ihlali bildirilmemiş (72 saat) | Ağır ceza |
| Silme talebi yerine getirilmemiş | İdari işlem |
| Gizlilik politikası eski GDPR şablonu (Türkçe değil) | Uyumsuzluk |

## KVKK Ceza Tablosu (2024)

- Aydınlatma yükümlülüğünü yerine getirmeme: 13.112 TL - 262.238 TL
- Veri güvenliği önlemleri almama: 26.233 TL - 2.621.152 TL
- Kurul kararlarını yerine getirmeme: 52.465 TL - 2.621.152 TL
- Veri ihlali bildirimi yapmama: 26.233 TL - 2.621.152 TL

*Not: Tutarlar her yıl yeniden değerleme oranında artırılmaktadır.*

## Denetim Raporu Çıktısı

Denetim tamamlandığında şu formatta rapor üret:

```
KVKK UYUM DENETİM RAPORU
Tarih: [tarih]
Denetlenen: [uygulama/metin/şirket]

UYUM PUANI: [X/100]

KRİTİK BULGULAR (Acil Düzeltme Gerekli):
- [bulgu 1]
- [bulgu 2]

ÖNEMLİ BULGULAR (30 Gün İçinde Düzeltilmeli):
- [bulgu 1]

ÖNERİLER:
- [öneri 1]

SONUÇ: [Uyumlu / Kısmen Uyumlu / Uyumsuz]
```

Detaylı KVKK maddeleri için [kvkk-maddeler.md](references/kvkk-maddeler.md) dosyasına bakın.
