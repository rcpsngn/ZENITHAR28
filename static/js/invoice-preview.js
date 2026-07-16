// static/js/invoice-preview.js
// Tüm fatura sayfalarında (taslak, gönderilen, gelen) ortak kullanılan
// resmi belge önizleme, yazdırma ve toplu seçim fonksiyonları.

function toggleAllInvoices(source) {
    document.querySelectorAll(".invoice-row-checkbox").forEach(cb => cb.checked = source.checked);
}

// "Detay Göster" acilir menu kontrolu
function toggleDetailMenu(btn) {
    const menu = btn.nextElementSibling;
    const isOpen = menu.classList.contains("open");
    document.querySelectorAll(".detail-menu.open").forEach(m => m.classList.remove("open"));
    if (!isOpen) menu.classList.add("open");
}
document.addEventListener("click", function (e) {
    if (!e.target.closest(".detail-menu-wrapper")) {
        document.querySelectorAll(".detail-menu.open").forEach(m => m.classList.remove("open"));
    }
});

// Henuz gercek bir GIB/e-posta/WhatsApp entegrasyonu bagli olmayan
// ozellikler icin durust bir bilgilendirme (sahte "basarili" mesaji GOSTERMEZ).
function notReadyYet(featureName) {
    alert(
        featureName + " özelliği arayüzde hazır, ancak gerçek bir e-Fatura " +
        "entegratörü (GİB/Uyumsoft/Foriba vb.) bağlanmadan çalışmaz.\n\n" +
        "apps/invoices/integrations.py dosyasına gerçek API bilgilerini ekleyince aktifleşecek."
    );
}

// ÖNEMLİ: Kullanıcının yazdığı serbest metinler (açıklama, not, ünvan vb.)
// doğrudan şablon string'ine gömülüyordu. İçinde tırnak/HTML özel karakteri
// olan bir açıklama girilince önizleme hiç render olmuyordu (JS hata veriyordu).
// Bu fonksiyon her metni önce güvenli hale getiriyor.
function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
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

            const isWaybill = data.type === 'e-irsaliye';
            const docLabel = isWaybill ? 'e-İRSALİYE' : 'e-FATURA';
            const numberLabel = isWaybill ? 'İrsaliye No' : 'Fatura No';
            const dateLabel = isWaybill ? 'İrsaliye Tarihi' : 'Fatura Tarihi';

            let itemsRows = "";
            (data.items || []).forEach((item, index) => {
                itemsRows += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${escapeHtml(item.desc)}</td>
                        <td>${item.qty} ${escapeHtml(item.unit)}</td>
                        <td>${item.price.toFixed(2)} ${data.currency}</td>
                        <td>%${item.vat_rate}</td>
                        <td>${item.vat_amount.toFixed(2)} ${data.currency}</td>
                        <td>${item.total.toFixed(2)} ${data.currency}</td>
                    </tr>
                `;
            });

            // Alıcı iletişim satırları (sadece doluysa gösterilir)
            let contactLines = "";
            if (data.customer_phone) contactLines += `<strong>Tel:</strong> ${escapeHtml(data.customer_phone)}<br>`;
            if (data.customer_email) contactLines += `<strong>E-Posta:</strong> ${escapeHtml(data.customer_email)}<br>`;
            if (data.customer_website) contactLines += `<strong>Web:</strong> ${escapeHtml(data.customer_website)}<br>`;

            // Sevk adresi, alıcı adresinden farklıysa ayrıca gösterilir
            let deliveryBoxHTML = "";
            const hasDeliveryAddress = data.delivery_street || data.delivery_district;
            if (hasDeliveryAddress) {
                deliveryBoxHTML = `
                    <div class="gib-box-border" style="margin-top:10px;">
                        <div class="gib-title-sub">SEVK ADRESİ</div>
                        ${escapeHtml(data.delivery_street)} ${escapeHtml(data.delivery_district)}<br>
                        ${escapeHtml(data.delivery_country || "")} ${escapeHtml(data.delivery_postal_code || "")}
                    </div>
                `;
            }

            // Notlar / açıklamalar (varsa)
            let notesHTML = "";
            if (data.notes) {
                notesHTML = `
                    <div class="gib-box-border" style="margin-top:14px;">
                        <div class="gib-title-sub">AÇIKLAMALAR / NOTLAR</div>
                        ${escapeHtml(data.notes).replaceAll("\n", "<br>")}
                    </div>
                `;
            }

            // Firma bilgileri (Ayarlar > Firma Bilgileri'nden gelir)
            const company = data.company || {};
            const logoHTML = company.logo_url
                ? `<img src="${company.logo_url}" alt="Logo" style="height:48px; object-fit:contain; margin-bottom:6px;"><br>`
                : "";
            let companyContactLine = "";
            if (company.phone) companyContactLine += `Tel: ${escapeHtml(company.phone)} `;
            if (company.email) companyContactLine += `| E-Posta: ${escapeHtml(company.email)} `;
            if (company.website) companyContactLine += `| ${escapeHtml(company.website)}`;

            target.innerHTML = `
                <div class="gib-invoice-template">
                    ${watermarkHTML}
                    <div class="gib-header">
                        <div>
                            ${logoHTML}
                            <strong>${escapeHtml(company.name)}</strong><br>
                            ${escapeHtml(company.address)}<br>
                            ${company.tax_id ? `VKN: ${escapeHtml(company.tax_id)}` : ""}${company.tax_office ? ` | ${escapeHtml(company.tax_office)}` : ""}
                            ${companyContactLine ? `<br>${companyContactLine}` : ""}
                        </div>
                        <div style="text-align: right; font-size: 16px; font-weight: bold; color: #ef4444;">${docLabel}</div>
                    </div>
                    <div class="gib-grid-info">
                        <div>
                            <div class="gib-box-border">
                                <div class="gib-title-sub">SAYIN / ALICI</div>
                                <strong>${escapeHtml(data.customer_name)}</strong><br>
                                ${escapeHtml(data.customer_street)} ${escapeHtml(data.customer_district)} / ${escapeHtml(data.customer_city)}<br>
                                <strong>VKN/TCKN:</strong> ${escapeHtml(data.customer_tax_id)}<br>
                                <strong>Vergi Dairesi:</strong> ${escapeHtml(data.customer_tax_office)}<br>
                                ${contactLines}
                            </div>
                            ${deliveryBoxHTML}
                        </div>
                        <div class="gib-box-border">
                            <div class="gib-title-sub">Belge Künyesi</div>
                            <strong>ETTN:</strong> ${escapeHtml(data.ettn)}<br>
                            <strong>Özelleştirme No:</strong> ${escapeHtml(data.custom_no)}<br>
                            <strong>${numberLabel}:</strong> ${escapeHtml(data.invoice_number)}<br>
                            <strong>${dateLabel}:</strong> ${data.issue_date}<br>
                            <strong>Senaryo:</strong> ${escapeHtml(data.invoice_type)}<br>
                            <strong>Fatura Tipi:</strong> ${escapeHtml(data.invoice_category)}<br>
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
                    ${notesHTML}
                </div>
            `;
            document.getElementById("invoicePreviewModal").style.display = "flex";
        })
        .catch(err => {
            alert("Önizleme yüklenirken bir hata oluştu: " + err.message);
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