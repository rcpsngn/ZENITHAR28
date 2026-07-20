"""
apps/current_accounts/signals.py

Aşama 20 notu: "Stok hareket fişi kesildiğinde ... ürün adedini güncelleyen
Django Sinyalleri (Signals) yazılmalı." — bu dosya tam olarak bunu yapar.

Bir StockMovement kaydı oluşturulduğunda (post_save, created=True), ilgili
Product.quantity alanı türe göre otomatik artırılır/azaltılır. update() değil
F() ifadesi kullanılır ki eşzamanlı iki hareket birbirinin üzerine yazmasın
(race condition'a karşı veritabanı seviyesinde atomik artır/azalt).

NOT (kapsam sınırı): "fatura onaylandığında ürün adedini güncelleyen sinyal"
kısmı bu pakete DAHİL EDİLMEDİ — çünkü InvoiceItem modelinde bir Product'a
işaret eden foreign key yok (kalemler serbest metin `description` alanı ile
tutuluyor). Bu, invoices ve current_accounts modüllerini birbirine bağlayan
ayrı bir şema değişikliği gerektiriyor; burada kapsam dışı bırakıldı ki
yanlışlıkla var olmayan bir InvoiceItem.product alanına referans verip
sistemi bozmayalım. Bu bağlantı ayrı bir görev olarak ele alınmalı.
"""
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StockMovement, Product


@receiver(post_save, sender=StockMovement)
def update_product_quantity_on_movement(sender, instance: StockMovement, created: bool, **kwargs):
    if not created:
        # Bir stok hareketi kaydı GÜNCELLENEMEZ olmalı (muhasebe fişi mantığı:
        # hatalı bir hareket düzeltilecekse yeni bir ters hareket girilir, eskisi
        # değiştirilmez). Bu yüzden yalnızca created=True durumunda işlem yapılır.
        return

    if instance.type == "in":
        Product.objects.filter(id=instance.product_id).update(quantity=F("quantity") + instance.quantity)
    elif instance.type == "out":
        Product.objects.filter(id=instance.product_id).update(quantity=F("quantity") - instance.quantity)
