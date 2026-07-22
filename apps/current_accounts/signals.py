"""
apps/current_accounts/signals.py

Aşama 20 notu: "Stok hareket fişi kesildiğinde ... ürün adedini güncelleyen
Django Sinyalleri (Signals) yazılmalı." — bu dosya tam olarak bunu yapar.

Bir StockMovement kaydı oluşturulduğunda (post_save, created=True), ilgili
Product.quantity alanı türe göre otomatik artırılır/azaltılır. update() değil
F() ifadesi kullanılır ki eşzamanlı iki hareket birbirinin üzerine yazmasın
(race condition'a karşı veritabanı seviyesinde atomik artır/azalt).

Aşama 55 (Depo-Stok Entegrasyonu) ile: hareket bir depoya bağlıysa
ProductWarehouseStock kaydı da eş zamanlı güncellenir — "ürün şu depoda
olduğu belirli olsun, stoktan düştükçe depodan düşsün" isteği budur.
'transfer' tipinde Product.quantity toplamda DEĞİŞMEZ (mal firma içinde
kalıyor), yalnızca kaynak depodan düşer, hedef depoya eklenir.

NOT (kapsam sınırı): "fatura onaylandığında ürün adedini güncelleyen sinyal"
kısmı bu pakete DAHİL EDİLMEDİ — çünkü InvoiceItem modelinde bir Product'a
işaret eden foreign key yok (kalemler serbest metin `description` alanı ile
tutuluyor). Bu, invoices ve current_accounts modüllerini birbirine bağlayan
ayrı bir şema değişikliği gerektiriyor (bkz. Aşama 56 notu); burada kapsam
dışı bırakıldı.
"""
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StockMovement, Product, ProductWarehouseStock


def _adjust_warehouse_stock(product_id, warehouse_id, delta):
    """ProductWarehouseStock kaydını get_or_create edip F() ile atomik artır/azalt."""
    if not warehouse_id:
        return
    stock, _ = ProductWarehouseStock.objects.get_or_create(
        product_id=product_id, warehouse_id=warehouse_id, defaults={"quantity": 0}
    )
    ProductWarehouseStock.objects.filter(pk=stock.pk).update(quantity=F("quantity") + delta)


@receiver(post_save, sender=StockMovement)
def update_product_quantity_on_movement(sender, instance: StockMovement, created: bool, **kwargs):
    if not created:
        # Bir stok hareketi kaydı GÜNCELLENEMEZ olmalı (muhasebe fişi mantığı:
        # hatalı bir hareket düzeltilecekse yeni bir ters hareket girilir, eskisi
        # değiştirilmez). Bu yüzden yalnızca created=True durumunda işlem yapılır.
        return

    if instance.type == "in":
        Product.objects.filter(id=instance.product_id).update(quantity=F("quantity") + instance.quantity)
        _adjust_warehouse_stock(instance.product_id, instance.warehouse_id, instance.quantity)

    elif instance.type == "out":
        Product.objects.filter(id=instance.product_id).update(quantity=F("quantity") - instance.quantity)
        _adjust_warehouse_stock(instance.product_id, instance.warehouse_id, -instance.quantity)

    elif instance.type == "transfer":
        # Toplam Product.quantity değişmez; yalnızca depolar arasında hareket eder.
        _adjust_warehouse_stock(instance.product_id, instance.warehouse_id, -instance.quantity)
        _adjust_warehouse_stock(instance.product_id, instance.target_warehouse_id, instance.quantity)
