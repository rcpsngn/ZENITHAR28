"""
Portal / entegratör şifrelerini düz metin olarak DB'ye YAZMAMAK için
basit bir Fernet (AES-128-CBC + HMAC) şifreleme yardımcı modülü.

Kullanım:
    from .crypto import encrypt_value, decrypt_value
    encrypted = encrypt_value("gizli-sifre")
    plain = decrypt_value(encrypted)

Anahtar zenithar/settings.py > PORTAL_ENCRYPTION_KEY üzerinden, o da
.env dosyasındaki PORTAL_ENCRYPTION_KEY ortam değişkeninden okunur.
Anahtar asla kod içine gömülmemeli / repoya commit edilmemelidir.
"""
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _get_cipher() -> Fernet:
    key = getattr(settings, "PORTAL_ENCRYPTION_KEY", None)
    if not key:
        raise RuntimeError(
            "PORTAL_ENCRYPTION_KEY tanımlı değil. .env dosyanıza şu komutla "
            "üretilen bir anahtar ekleyin: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_value(plain_text: str) -> str:
    """Düz metni şifreleyip DB'ye yazılabilir bir string olarak döner."""
    if not plain_text:
        return ""
    cipher = _get_cipher()
    return cipher.encrypt(plain_text.encode()).decode()


def decrypt_value(encrypted_text: str) -> str:
    """Şifreli metni çözer. Bozuk/eksik veri varsa boş string döner (hata fırlatmaz)."""
    if not encrypted_text:
        return ""
    cipher = _get_cipher()
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except (InvalidToken, ValueError):
        return ""


def mask_value(plain_text: str, visible: int = 2) -> str:
    """Ekranda gösterim için: 'ab******yz' gibi maskelenmiş hâl döner."""
    if not plain_text:
        return ""
    if len(plain_text) <= visible * 2:
        return "*" * len(plain_text)
    return plain_text[:visible] + "*" * (len(plain_text) - visible * 2) + plain_text[-visible:]
