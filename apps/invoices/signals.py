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

    Transaction.objects.create(
        current_account=instance.current_account,
        type="debit",
        amount=instance.total_amount,
        description=f"{instance.invoice_number} numaralı fatura (otomatik aktarım)",
        date=instance.issue_date,
        document_number=instance.invoice_number,
    )
    instance.current_account.balance += instance.total_amount
    instance.current_account.save(update_fields=["balance"])

    # update() kullanılır ki bu save() tekrar post_save sinyalini tetiklemesin
    # (instance.save() çağırmak sonsuz döngüye ya da en azından gereksiz bir
    # ikinci sinyal tetiklemesine yol açardı).
    Invoice.objects.filter(pk=instance.pk).update(ledger_posted=True)
