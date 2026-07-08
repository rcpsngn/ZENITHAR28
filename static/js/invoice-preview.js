// static/js/invoice-preview.js
// Tüm fatura sayfalarında (taslak, gönderilen, gelen) ortak kullanılan
// resmi belge önizleme, yazdırma ve toplu seçim fonksiyonları.

function toggleAllInvoices(source) {
    document.querySelectorAll(".invoice-row-checkbox").forEach(cb => cb.checked = source.checked);
}

function openInvoicePreview(invoiceId) {
    fetch(`/invoices/view/${invoiceId}/?format=json`)
        .then(res => res.json())
        .then(data => {
            const target = document.getElementById("invoiceEmbedTarget");
            let watermarkHTML = "";
            if (data.status === 'draft') {
                watermarkHTML = `<div class="mali-degeri-yoktur-watermark">Mali Değeri Yoktur</div>`;
            } else if (data.status === 'cancelled') {
                watermarkHTML = `<div class="mali-degeri-yoktur-watermark">İptal Edildi</div>`;
            }

            let itemsRows = "";
            (data.items || []).forEach((item, index) => {
                itemsRows += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${item.desc}</td>
                        <td>${item.qty} ${item.unit}</td>
                        <td>${item.price.toFixed(2)} ${data.currency}</td>
                        <td>%${item.vat_rate}</td>
                        <td>${item.vat_amount.toFixed(2)} ${data.currency}</td>
                        <td>${item.total.toFixed(2)} ${data.currency}</td>
                    </tr>
                `;
            });

            target.innerHTML = `
                <div class="gib-invoice-template">
                    ${watermarkHTML}
                    <div class="gib-header">
                        <div>
                            <strong>ZENITHAR TEKNOLOJİ ERP SİSTEMİ</strong><br>
                            Merkez Mah. İstiklal Cad. No:44 Beyoğlu / İstanbul<br>
                            VKN: 9999999999 | Telefon: 0212 555 00 00
                        </div>
                        <div style="text-align: right; font-size: 16px; font-weight: bold; color: #ef4444;">e-FATURA</div>
                    </div>
                    <div class="gib-grid-info">
                        <div class="gib-box-border">
                            <div class="gib-title-sub">SAYIN / ALICI</div>
                            <strong>${data.customer_name}</strong><br>
                            ${data.customer_street} ${data.customer_district} / ${data.customer_city}<br>
                            <strong>VKN/TCKN:</strong> ${data.customer_tax_id}<br>
                            <strong>Vergi Dairesi:</strong> ${data.customer_tax_office}
                        </div>
                        <div class="gib-box-border">
                            <div class="gib-title-sub">Belge Künyesi</div>
                            <strong>ETTN:</strong> ${data.ettn}<br>
                            <strong>Fatura No:</strong> ${data.invoice_number}<br>
                            <strong>Fatura Tarihi:</strong> ${data.issue_date}<br>
                            <strong>Para Birimi / Kur:</strong> ${data.currency} (${data.exchange_rate})
                        </div>
                    </div>
                    <table class="gib-table">
                        <thead>
                            <tr>
                                <th>Sıra No</th>
                                <th>Mal / Hizmet Açıklaması</th>
                                <th>Miktar</th>
                                <th>Birim Fiyat</th>
                                <th>KDV %</th>
                                <th>KDV Tutarı</th>
                                <th>Mal Hizmet Tutarı</th>
                            </tr>
                        </thead>
                        <tbody>${itemsRows}</tbody>
                    </table>
                    <div class="gib-flex-end-totals">
                        <div class="gib-total-row"><span>Mal Hizmet Toplam Tutarı:</span><span>${data.amount.toFixed(2)} ${data.currency}</span></div>
                        <div class="gib-total-row"><span>Hesaplanan KDV:</span><span>${data.vat_amount.toFixed(2)} ${data.currency}</span></div>
                        <div class="gib-total-row gib-grand-total"><span>Ödenecek Toplam Tutar:</span><span>${data.total_amount.toFixed(2)} ${data.currency}</span></div>
                    </div>
                </div>
            `;
            document.getElementById("invoicePreviewModal").style.display = "flex";
        });
}

function closeInvoicePreview() {
    document.getElementById("invoicePreviewModal").style.display = "none";
}

function printModalInvoice() {
    const content = document.getElementById("invoiceEmbedTarget").innerHTML;
    const win = window.open('', '_blank');
    win.document.write(`<html><head><title>Baskı</title><style>
        body{margin:20px;font-family:sans-serif;}
        .gib-invoice-template{position:relative;}
        .mali-degeri-yoktur-watermark{position:absolute;top:35%;left:5%;width:90%;background:none !important;background-color:transparent !important;box-shadow:none !important;border:none !important;color:rgba(220,38,38,0.5) !important;font-size:64px;font-weight:900;text-transform:uppercase;text-align:center;transform:rotate(-25deg);pointer-events:none;}
        .gib-header{display:flex;justify-content:space-between;border-bottom:2px solid #000;padding-bottom:12px;margin-bottom:16px;font-size:12px;}
        .gib-grid-info{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;font-size:12px;}
        .gib-box-border{border:1px solid #000;padding:10px;}
        .gib-title-sub{font-size:13px;font-weight:bold;border-bottom:1px solid #000;margin-bottom:6px;}
        .gib-table{width:100%;border-collapse:collapse;font-size:11px;}
        .gib-table th, .gib-table td{border:1px solid #000;padding:6px;}
        .gib-flex-end-totals{display:flex;flex-direction:column;align-items:flex-end;margin-top:15px;}
        .gib-total-row{display:flex;width:260px;justify-content:space-between;font-size:12px;}
        .gib-grand-total{font-weight:bold;border-top:1px solid #000;}
    </style></head><body>${content}</body></html>`);
    win.document.close(); win.focus(); setTimeout(() => { win.print(); win.close(); }, 300);
}
