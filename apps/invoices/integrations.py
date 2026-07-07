# apps/invoices/integrations.py
#
# ============================================================================
#  DIŞ ENTEGRASYON KATMANI (VKN/GİB sorgulama, döviz kuru vb.)
# ============================================================================
#
#  Bu dosyanın amacı: dış servislere (GİB, e-Fatura entegratörü, TCMB vb.)
#  yapılan tüm çağrıları TEK BİR YERDE toplamak. views.py bu fonksiyonları
#  çağırır, dış servisin nasıl çalıştığıyla hiç ilgilenmez.
#
#  Böylece ileride gerçek bir GİB/entegratör API'sine geçerken sadece BU
#  DOSYAYI değiştirmen yeterli olacak — views.py, models.py, HTML, JS
#  dosyalarının HİÇBİRİNE dokunmana gerek kalmayacak.
#
#  Şu an "lookup_vkn" fonksiyonu SİMÜLASYON modunda çalışıyor (sabit test
#  verisi döndürüyor). Gerçek bir sağlayıcıyla (Foriba, Uyumsoft, Logo,
#  Mikro vb.) anlaştığında aşağıdaki adımları izle:
#
#    1) settings.py'ye şunları ekle:
#         GIB_INTEGRATION_PROVIDER = "gerçek_saglayici_adi"
#         GIB_API_URL = "https://saglayicinin-verdigi-url"
#         GIB_API_KEY = "saglayicinin-verdigi-anahtar"
#         (Bu bilgileri asla koda gömme, .env dosyasından oku!)
#
#    2) Aşağıdaki lookup_vkn() fonksiyonunun içindeki SİMÜLASYON bloğunu
#       silip, yerine sağlayıcının verdiği örnek koda göre gerçek bir
#       `requests.get(...)` / `requests.post(...)` çağrısı yaz.
#
#    3) Dönen cevabı, fonksiyonun en altındaki sözlük (dict) formatına
#       çevirip return et. Format hep aynı kalmalı ki views.py bozulmasın:
#         {
#           "success": True/False,
#           "title": "...", "office": "...", "city": "...",
#           "district": "...", "street": "...", "zip": "...",
#           "message": "..."   (sadece success=False ise)
#         }
#
# ============================================================================

from decimal import Decimal
import urllib.request
import xml.etree.ElementTree as ET

from django.conf import settings


# ----------------------------------------------------------------------------
# 1) VKN / GİB VERGİ DAİRESİ SORGULAMA
# ----------------------------------------------------------------------------

def lookup_vkn(vkn: str) -> dict:
    """
    Bir VKN/TCKN'ye karşılık firma/şahıs bilgilerini döndürür.

    ŞU AN: Simülasyon modunda. Gerçek entegrasyon için dosyanın en üstündeki
    açıklamayı oku.
    """

    provider = getattr(settings, "GIB_INTEGRATION_PROVIDER", None)

    if provider:
        # ------------------------------------------------------------------
        # GERÇEK ENTEGRASYON BURAYA YAZILACAK
        # ------------------------------------------------------------------
        # Örnek iskelet (sağlayıcının API dokümantasyonuna göre düzenle):
        #
        # import requests
        # try:
        #     response = requests.get(
        #         f"{settings.GIB_API_URL}/vkn-sorgula",
        #         params={"vkn": vkn},
        #         headers={"Authorization": f"Bearer {settings.GIB_API_KEY}"},
        #         timeout=5,
        #     )
        #     data = response.json()
        #     return {
        #         "success": True,
        #         "title": data["unvan"],
        #         "office": data["vergi_dairesi"],
        #         "city": data["il"],
        #         "district": data["ilce"],
        #         "street": data["adres"],
        #         "zip": data["posta_kodu"],
        #     }
        # except Exception:
        #     return {"success": False, "message": "GİB servisine ulaşılamadı."}
        raise NotImplementedError(
            "GIB_INTEGRATION_PROVIDER ayarlandı ama gerçek entegrasyon kodu "
            "henüz yazılmadı. apps/invoices/integrations.py dosyasındaki "
            "yorum satırlarına bak."
        )

    # ------------------------------------------------------------------
    # SİMÜLASYON MODU (varsayılan) — gerçek servis bağlanana kadar aktif
    # ------------------------------------------------------------------
    if vkn == "1234567890":
        return {
            "success": True,
            "title": "ZENITHAR YAZILIM VE TEKNOLOJİ ANONİM ŞİRKETİ",
            "office": "BEYOĞLU VERGİ DAİRESİ",
            "city": "İSTANBUL",
            "district": "BEYOĞLU",
            "street": "İSTİKLAL CADDESİ NO:100 KAT:3",
            "zip": "34430",
        }

    return {
        "success": False,
        "message": "Mükellef bulunamadı. Lütfen bilgileri elle doldurunuz.",
    }


# ----------------------------------------------------------------------------
# 2) TCMB DÖVİZ KURU (bu kısım zaten gerçek ve ücretsiz bir devlet servisi)
# ----------------------------------------------------------------------------

FALLBACK_RATES = {"USD": "34.2500", "EUR": "37.1200", "GBP": "44.5000"}


def get_exchange_rate(currency_code: str) -> str:
    """TCMB günlük kur listesinden verilen döviz kodunun alış kurunu döndürür."""
    currency_code = (currency_code or "TL").upper()

    if currency_code in ("TL", "TRY"):
        return "1.0000"

    try:
        req = urllib.request.Request(
            "https://www.tcmb.gov.tr/kurlar/today.xml",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        for currency in root.findall("Currency"):
            if currency.get("CurrencyCode") == currency_code:
                rate_str = currency.find("ForexBuying").text
                return str(round(float(rate_str), 4))
    except Exception:
        return FALLBACK_RATES.get(currency_code, "1.0000")

    return "1.0000"


# ----------------------------------------------------------------------------
# 3) E-FATURA GÖNDERİMİ (henüz kullanılmıyor, ileride buraya eklenecek)
# ----------------------------------------------------------------------------

def send_efatura(invoice) -> dict:
    """
    İleride gerçek bir e-Fatura entegratörüne (GİB e-Arşiv Portalı veya özel
    entegratör API'si) fatura gönderimi burada yapılacak.

    Şu an sadece durumu 'sent' yapan basit bir yer tutucu (placeholder).
    Gerçek entegrasyonda: XML/UBL-TR formatında fatura oluşturup entegratöre
    POST edip, dönen ETTN/durum bilgisini invoice modeline kaydet.
    """
    return {"success": True, "message": "Simülasyon: fatura 'gönderildi' olarak işaretlendi."}
