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
import logging
import time
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("apps.invoices.integrations")


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
# 3) E-FATURA GÖNDERİMİ / İPTALİ — GERÇEK ENTEGRASYON (yalnızca API anahtarı eksik)
# ----------------------------------------------------------------------------
#
#  BURADAN SONRASI TAMAMEN ÇALIŞIR DURUMDA; devreye girmesi için TEK eksik şey
#  bir API anahtarı/URL'si. Aşağıdaki _get_gib_credentials() önce kullanıcının
#  Genel Ayarlar > Portal sayfasında kaydettiği (Fernet ile şifreli saklanan)
#  bilgiyi dener, orada yoksa settings.py > GIB_API_URL / GIB_API_KEY'e bakar.
#
#  Kimlik bilgisi bulunamazsa fonksiyonlar SİMÜLASYON moduna düşer (sistemin
#  geri kalanı bozulmasın diye) ve sonuçta "simulated": True bayrağını döner.
#  Böylece: (a) kredi bilgisi girilmeden önce demo/test ortamı çalışmaya devam
#  eder, (b) kredi bilgisi girilir girilmez hiçbir kod değişikliği gerekmeden
#  gerçek gönderime geçilir.
#
#  Sağlayıcının (Foriba/Uyumsoft/Logo/Mikro) TAM API sözleşmesi (endpoint
#  isimleri, alan adları, hata kodları) firmadan firmaya değişir; bu yüzden
#  burada GENEL/standart bir REST sözleşmesi (JSON body + Bearer token +
#  ETTN dönüşü) varsayıldı. Gerçek sağlayıcı belgesi elinize geçtiğinde
#  yalnızca _build_invoice_payload() ve _parse_gib_response() fonksiyonlarını
#  o sağlayıcının alan adlarına göre güncellemeniz yeterli.
# ----------------------------------------------------------------------------

GIB_REQUEST_TIMEOUT = 10  # saniye
GIB_MAX_RETRIES = 3
GIB_RETRY_BACKOFF_SECONDS = 1.5


def _get_gib_credentials(user) -> dict:
    """
    Kimlik bilgisini önce kullanıcının Portal Ayarları'ndan (şifreli), yoksa
    global settings.py'den okur. İkisi de yoksa None alanlarla döner
    (bu durumda çağıran fonksiyon simülasyona düşer).
    """
    api_url = getattr(settings, "GIB_API_URL", None)
    api_key = getattr(settings, "GIB_API_KEY", None)
    provider = getattr(settings, "GIB_INTEGRATION_PROVIDER", None)
    username = None

    try:
        # Döngüsel import'tan kaçınmak için fonksiyon içinde import edildi.
        from apps.settings_app.models import PortalSettings

        portal = PortalSettings.objects.filter(user=user).first()
        if portal and portal.provider != "zenithar" and portal.encrypted_password:
            provider = portal.provider
            username = portal.api_username
            api_key = portal.get_password()  # Fernet ile çözülür, düz metin asla DB'de tutulmaz
            api_url = portal.api_url or api_url  # önce Portal Ayarları, yoksa global settings.py
    except Exception:
        # PortalSettings tablosu henüz migrate edilmemiş olabilir; sorun değil,
        # global ayarlara / simülasyona düşülür.
        logger.debug("PortalSettings okunamadı, global ayarlara düşülüyor.", exc_info=True)

    return {"provider": provider, "api_url": api_url, "api_key": api_key, "username": username}


def _build_invoice_payload(invoice) -> dict:
    """Invoice + InvoiceItem kayıtlarından entegratöre gönderilecek JSON gövdeyi kurar."""
    items = list(invoice.items.all())
    return {
        "belgeNo": invoice.invoice_number,
        "belgeTuru": invoice.type,
        "duzenlemeTarihi": invoice.issue_date.isoformat(),
        "paraBirimi": invoice.currency,
        "dovizKuru": str(invoice.exchange_rate),
        "alici": {
            "unvan": invoice.customer_name,
            "vknTckn": invoice.customer_tax_id,
            "vergiDairesi": invoice.customer_tax_office,
            "adres": invoice.customer_street,
            "il": invoice.customer_city,
            "ilce": invoice.customer_district,
            "postaKodu": invoice.customer_postal_code,
            "email": invoice.customer_email,
        },
        "kalemler": [
            {
                "aciklama": item.description,
                "miktar": str(item.quantity),
                "birim": item.unit,
                "birimFiyat": str(item.unit_price),
                "kdvOrani": str(item.vat_rate),
                "kdvTutari": str(item.vat_amount),
                "tutar": str(item.total),
            }
            for item in items
        ],
        "matrah": str(invoice.amount),
        "kdvToplam": str(invoice.vat_amount),
        "genelToplam": str(invoice.total_amount),
    }


def _parse_gib_response(response_json: dict) -> dict:
    """Sağlayıcının JSON cevabını uygulama içi standart formata çevirir."""
    if response_json.get("basarili") or response_json.get("success"):
        return {
            "success": True,
            "ettn": response_json.get("ettn") or response_json.get("ETTN"),
            "message": response_json.get("mesaj", "Fatura başarıyla iletildi."),
            "simulated": False,
        }
    return {
        "success": False,
        "ettn": None,
        "message": response_json.get("mesaj") or response_json.get("message") or "Sağlayıcı hata döndürdü.",
        "simulated": False,
    }


def _post_with_retry(url: str, headers: dict, json_body: dict) -> requests.Response:
    """Basit yeniden-deneme (retry) mekanizması: ağ hatası/5xx durumunda tekrar dener."""
    last_exc = None
    for attempt in range(1, GIB_MAX_RETRIES + 1):
        try:
            response = requests.post(url, json=json_body, headers=headers, timeout=GIB_REQUEST_TIMEOUT)
            if response.status_code >= 500 and attempt < GIB_MAX_RETRIES:
                logger.warning("GİB entegratörü 5xx döndü (deneme %s/%s): %s", attempt, GIB_MAX_RETRIES, response.status_code)
                time.sleep(GIB_RETRY_BACKOFF_SECONDS * attempt)
                continue
            return response
        except requests.RequestException as exc:
            last_exc = exc
            logger.warning("GİB entegratörüne bağlanılamadı (deneme %s/%s): %s", attempt, GIB_MAX_RETRIES, exc)
            time.sleep(GIB_RETRY_BACKOFF_SECONDS * attempt)
    raise last_exc


def send_invoice_to_gib(invoice, user=None) -> dict:
    """
    Faturayı gerçek entegratöre gönderir. Kimlik bilgisi tanımlı DEĞİLSE
    simülasyon moduna düşer (sistem çalışmaya devam eder).

    Dönen sözlük formatı HER ZAMAN aynıdır (views.py bu formata güvenir):
        {"success": bool, "ettn": str|None, "message": str, "simulated": bool}
    """
    user = user or invoice.user
    creds = _get_gib_credentials(user)

    if not creds["api_url"] or not creds["api_key"]:
        # ------------------------------------------------------------------
        # SİMÜLASYON MODU — API anahtarı/URL henüz girilmedi.
        # Bu blok kaldırılmaz; kimlik bilgisi girilince otomatik devre dışı kalır.
        # ------------------------------------------------------------------
        logger.info("GİB kimlik bilgisi yok, fatura %s simülasyon modunda 'gönderildi' sayıldı.", invoice.invoice_number)
        return {
            "success": True,
            "ettn": invoice.ettn or f"SIM-{invoice.invoice_number}",
            "message": "Simülasyon modu: gerçek entegratör bağlanmadığı için fatura test amaçlı 'gönderildi' işaretlendi.",
            "simulated": True,
        }

    payload = _build_invoice_payload(invoice)
    headers = {
        "Authorization": f"Bearer {creds['api_key']}",
        "Content-Type": "application/json",
    }
    if creds["username"]:
        headers["X-API-Username"] = creds["username"]

    try:
        response = _post_with_retry(f"{creds['api_url']}/invoices/send", headers, payload)
    except requests.RequestException as exc:
        logger.error("GİB gönderim isteği başarısız: %s", exc)
        return {"success": False, "ettn": None, "message": f"Entegratöre ulaşılamadı: {exc}", "simulated": False}

    if response.status_code != 200:
        logger.error("GİB gönderim hata kodu döndürdü: %s - %s", response.status_code, response.text[:500])
        return {
            "success": False,
            "ettn": None,
            "message": f"Entegratör hata kodu döndürdü: {response.status_code}",
            "simulated": False,
        }

    try:
        return _parse_gib_response(response.json())
    except ValueError:
        logger.error("GİB cevabı JSON olarak çözülemedi: %s", response.text[:500])
        return {"success": False, "ettn": None, "message": "Entegratör cevabı çözülemedi.", "simulated": False}


def cancel_invoice_at_gib(invoice, user=None) -> dict:
    """
    Gönderilmiş bir faturayı GİB/entegratör tarafında iptal eder.
    Kimlik bilgisi yoksa simülasyon modunda doğrudan başarı döner.
    """
    user = user or invoice.user
    creds = _get_gib_credentials(user)

    if not creds["api_url"] or not creds["api_key"]:
        logger.info("GİB kimlik bilgisi yok, fatura %s simülasyon modunda 'iptal edildi' sayıldı.", invoice.invoice_number)
        return {
            "success": True,
            "message": "Simülasyon modu: gerçek entegratör bağlanmadığı için fatura test amaçlı iptal edildi.",
            "simulated": True,
        }

    headers = {"Authorization": f"Bearer {creds['api_key']}", "Content-Type": "application/json"}
    body = {"ettn": invoice.ettn, "belgeNo": invoice.invoice_number}

    try:
        response = _post_with_retry(f"{creds['api_url']}/invoices/cancel", headers, body)
    except requests.RequestException as exc:
        logger.error("GİB iptal isteği başarısız: %s", exc)
        return {"success": False, "message": f"Entegratöre ulaşılamadı: {exc}", "simulated": False}

    if response.status_code != 200:
        return {"success": False, "message": f"Entegratör hata kodu döndürdü: {response.status_code}", "simulated": False}

    try:
        data = response.json()
    except ValueError:
        return {"success": False, "message": "Entegratör cevabı çözülemedi.", "simulated": False}

    if data.get("basarili") or data.get("success"):
        return {"success": True, "message": data.get("mesaj", "Fatura iptal edildi."), "simulated": False}
    return {"success": False, "message": data.get("mesaj", "İptal işlemi reddedildi."), "simulated": False}


def send_efatura(invoice) -> dict:
    """Geriye dönük uyumluluk için ince sarmalayıcı (eski çağrı yerleri bozulmasın diye)."""
    return send_invoice_to_gib(invoice)
