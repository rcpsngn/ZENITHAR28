"""
apps/invoices/signals.py

Aşama 56 (Cari & Stok - Cari Ekstre-Fatura Entegrasyonu): "Cari ekstreye
gelen/giden e-faturaları aktarmak için modül lazım" isteği.

Bir fatura, bağlı olduğu cari hesap (current_account) VARSA ve durumu
'approved' ya da 'paid' olduğunda (ve daha önce işlenmemişse), cari ekstreye
otomatik bir BORÇ (debit) hareketi olarak yansıtılır — yani müşteri bu tutarı
firmaya borçlanır. `ledger_posted` bayrağı sayesinde aynı fatura için birden
fazla kayıt oluşmaz (fatura başka bir sebeple tekrar save edilse bile).

NOT (kapsam sınırı): Yalnızca 'debit' (satış/alacak) yönü uygulandı — gelen
(tedarikçi) faturalarının 'credit' olarak işlenmesi, gelen faturaların hangi
cariye ait olduğunu ayırt eden ayrı bir akış gerektiriyor; bu, mevcut
"E-Fatura Gelen" ekranına bir cari eşleştirme adımı eklenmesini gerektirir ve
kapsam dışı bırakıldı.
"""
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Invoice

LEDGER_TRIGGER_STATUSES = ("approved", "paid")


@receiver(post_save, sender=Invoice)
def post_invoice_to_ledger(sender, instance: Invoice, created: bool, **kwargs):
    if not instance.current_account_id:
        return
    if instance.ledger_posted:
        return
    if instance.status not in LEDGER_TRIGGER_STATUSES:
        return

    # Döngüsel import'tan kaçınmak için fonksiyon içinde import edildi.
    from apps.current_accounts.models import Transaction

    # Savunma amaçlı Decimal dönüşümü: total_amount/balance bazen (ör. henüz
    # hiç kalem eklenmemiş bir fatura, ya da DB'den taze çekilmemiş bir
    # nesne) Python int/float olarak gelebilir; Decimal ile karışık aritmetik
    # TypeError fırlatır. str() üzerinden dönüştürmek float hassasiyet
    # sorununu da (ör. 0.1 + 0.2 problemi) önler.
    total_amount = Decimal(str(instance.total_amount or 0))
    if total_amount == 0:
        # Henüz hiç kalemi olmayan bir faturayı (tutar 0) ekstreye işlemenin
        # anlamı yok; kalemler eklenip fatura tekrar save edildiğinde
        # (ledger_posted hâlâ False olduğu için) doğru tutarla işlenecek.
        return

    Transaction.objects.create(
        current_account=instance.current_account,
        type="debit",
        amount=total_amount,
        description=f"{instance.invoice_number} numaralı fatura (otomatik aktarım)",
        date=instance.issue_date,
        document_number=instance.invoice_number,
    )

    current_balance = Decimal(str(instance.current_account.balance or 0))
    instance.current_account.balance = current_balance + total_amount
    instance.current_account.save(update_fields=["balance"])

    # update() kullanılır ki bu save() tekrar post_save sinyalini tetiklemesin
    # (instance.save() çağırmak sonsuz döngüye ya da en azından gereksiz bir
    # ikinci sinyal tetiklemesine yol açardı). Bellekteki instance.ledger_posted
    # de EL İLE True yapılır — aksi halde aynı Python nesnesi üzerinde
    # (ör. aynı test/istek içinde) tekrar .save() çağrılırsa, .update()
    # DB'yi güncellese bile bellekteki eski (False) değer görüleceği için
    # sinyal YANLIŞLIKLA ikinci kez tetiklenip mükerrer kayıt oluşabilirdi.
    Invoice.objects.filter(pk=instance.pk).update(ledger_posted=True)
    instance.ledger_posted = True
