# apps/waybill/models.py
#
# E-İrsaliye modülünün kendi modeli YOKTUR — apps.invoices.models.Invoice
# modelini (type="e-irsaliye" filtresiyle) yeniden kullanır. Bu sayede
# fatura ve irsaliye aynı alt yapıyı (kalemler, müşteri bilgisi, toplamlar,
# ETTN vb.) paylaşır, kod tekrarı olmaz.
#
# Önceden bu dosyaya yanlışlıkla view fonksiyonları kopyalanmıştı, kaldırıldı.
# Gerçek view'lar için apps/waybill/views.py dosyasına bakın.
