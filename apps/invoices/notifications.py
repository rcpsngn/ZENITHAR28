"""
apps/invoices/notifications.py

Aşama 11 (E-Arşiv - E-Arşiv Raporlama ve İlgili Alıcıya Mail/SMS Gönderimi)
için yazıldı.

- E-POSTA: Django'nun yerleşik `django.core.mail` altyapısını kullanır.
  Gerçekten çalışır durumdadır — geliştirmede EMAIL_BACKEND=console olduğu için
  e-posta gönderilmez, terminale yazdırılır; üretimde .env'e SMTP bilgileri
  girilince otomatik olarak gerçek gönderime geçer (kod değişikliği gerekmez).

- SMS: Türkiye'de yaygın sağlayıcılar (Netgsm, İletimerkezi, Twilio vb.) her
  biri farklı bir API sözleşimi kullanıyor. SMS_API_URL/SMS_API_KEY tanımlı
  değilse fonksiyon simülasyon moduna düşer (sistem bozulmaz). Tanımlanınca
  _send_sms_via_provider() içindeki gövdeyi sağlayıcının dokümanına göre
  güncellemeniz yeterli.
"""
import logging

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("apps.invoices.notifications")


def send_earchive_email(invoice, request=None) -> dict:
    """
    E-Arşiv faturasının görüntülenebileceği linki müşteriye e-posta ile gönderir.

    Dönen format: {"success": bool, "message": str, "simulated": bool}
    """
    if not invoice.customer_email:
        return {"success": False, "message": "Müşteri e-posta adresi tanımlı değil.", "simulated": False}

    if request is not None:
        link = request.build_absolute_uri(f"/invoices/view/{invoice.id}/")
    else:
        link = f"/invoices/view/{invoice.id}/"

    subject = f"{invoice.invoice_number} numaralı e-Arşiv faturanız"
    body = (
        f"Sayın {invoice.customer_name},\n\n"
        f"{invoice.invoice_number} numaralı, {invoice.total_amount} {invoice.currency} "
        f"tutarındaki e-Arşiv faturanızı aşağıdaki bağlantıdan görüntüleyebilirsiniz:\n\n"
        f"{link}\n\n"
        f"İyi çalışmalar dileriz."
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.customer_email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error("E-Arşiv e-postası gönderilemedi (%s): %s", invoice.invoice_number, exc)
        return {"success": False, "message": f"E-posta gönderilemedi: {exc}", "simulated": False}

    is_simulated = settings.EMAIL_BACKEND.endswith("console.EmailBackend")
    return {
        "success": True,
        "message": "E-posta konsola yazdırıldı (simülasyon)." if is_simulated else "E-posta gönderildi.",
        "simulated": is_simulated,
    }


def send_earchive_sms(invoice) -> dict:
    """
    E-Arşiv faturasının linkini müşteriye SMS ile gönderir.
    SMS_API_URL/SMS_API_KEY tanımlı değilse simülasyon moduna düşer.
    """
    if not invoice.customer_phone:
        return {"success": False, "message": "Müşteri telefon numarası tanımlı değil.", "simulated": False}

    if not settings.SMS_API_URL or not settings.SMS_API_KEY:
        logger.info("SMS API kimlik bilgisi yok, %s için SMS simülasyon modunda 'gönderildi' sayıldı.", invoice.invoice_number)
        return {
            "success": True,
            "message": "Simülasyon modu: SMS sağlayıcısı bağlanmadığı için gönderim test amaçlı işaretlendi.",
            "simulated": True,
        }

    message = f"{invoice.invoice_number} nolu e-Arşiv faturanız düzenlendi. Tutar: {invoice.total_amount} {invoice.currency}."

    try:
        response = requests.post(
            settings.SMS_API_URL,
            json={"to": invoice.customer_phone, "message": message},
            headers={"Authorization": f"Bearer {settings.SMS_API_KEY}"},
            timeout=8,
        )
    except requests.RequestException as exc:
        logger.error("SMS gönderilemedi (%s): %s", invoice.invoice_number, exc)
        return {"success": False, "message": f"SMS sağlayıcısına ulaşılamadı: {exc}", "simulated": False}

    if response.status_code != 200:
        return {"success": False, "message": f"SMS sağlayıcısı hata döndürdü: {response.status_code}", "simulated": False}

    return {"success": True, "message": "SMS gönderildi.", "simulated": False}


def notify_customer(invoice, request=None) -> dict:
    """E-posta VE SMS'i birlikte dener; ikisinin de sonucunu tek bir mesajda özetler."""
    email_result = send_earchive_email(invoice, request=request)
    sms_result = send_earchive_sms(invoice)

    parts = []
    if email_result["success"]:
        parts.append(f"E-posta: {email_result['message']}")
    else:
        parts.append(f"E-posta BAŞARISIZ: {email_result['message']}")

    if sms_result["success"]:
        parts.append(f"SMS: {sms_result['message']}")
    else:
        parts.append(f"SMS BAŞARISIZ: {sms_result['message']}")

    return {
        "success": email_result["success"] or sms_result["success"],
        "message": " | ".join(parts),
        "simulated": email_result.get("simulated", False) or sms_result.get("simulated", False),
    }
