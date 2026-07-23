let tempItemsList = [];

function fetchExchangeRate() {
    const code = document.getElementById("invoice_currency").value;
    fetch(`/invoices/api/get-tcmb-rate/?code=${code}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("exchange_rate_input").value = data.rate;
        });
}

function triggerGibQuery() {
    const vkn = document.getElementById("vkn_input").value;
    fetch(`/invoices/api/vkn-sorgula/?vkn=${vkn}`)
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                document.getElementById("customer_name_input").value = data.title;
                document.getElementById("customer_tax_office_input").value = data.office;
                document.getElementById("customer_city_input").value = data.city;
                document.getElementById("customer_district_input").value = data.district;
                document.getElementById("customer_street_input").value = data.street;
                document.getElementById("customer_postal_code_input").value = data.zip;
            } else {
                alert(data.message);
            }
        });
}

function openItemModal() {
    document.getElementById("itemModal").style.display = "flex";
    document.getElementById("m_desc").focus();
    // Aşama 46/54: her açılışta "Diğer Seçenekler" alanlarını temizle, ilk sekmeye dön.
    ["m_seller_code", "m_buyer_code", "m_barcode", "m_brand", "m_model_name",
     "m_origin_country", "m_additional_description", "m_item_note",
     "m_classification_value", "m_classification_version", "m_classification_code",
     "m_related_waybill_number", "m_related_waybill_date", "m_order_number",
     "m_order_date", "m_additional_info_id"].forEach(function (id) {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    switchItemTab("general");
}

function switchItemTab(tab) {
    const general = document.getElementById("panel_general");
    const other = document.getElementById("panel_other");
    const tabGeneral = document.getElementById("tab_general");
    const tabOther = document.getElementById("tab_other");
    if (!general || !other) return;
    general.style.display = (tab === "general") ? "grid" : "none";
    other.style.display = (tab === "other") ? "grid" : "none";
    if (tabGeneral) tabGeneral.classList.toggle("active", tab === "general");
    if (tabOther) tabOther.classList.toggle("active", tab === "other");
}

function closeItemModal() {
    document.getElementById("itemModal").style.display = "none";
}

function runModalMath() {
    const qty = parseFloat(document.getElementById("m_qty").value) || 0;
    const price = parseFloat(document.getElementById("m_price").value) || 0;
    const vat = parseFloat(document.getElementById("m_vat").value) || 0;
    const base = qty * price;
    const vatCalc = (base * vat) / 100;
    document.getElementById("m_vat_calc").value = vatCalc.toFixed(2);
    document.getElementById("m_total_calc").value = (base + vatCalc).toFixed(2);
}

function _fieldValue(id) {
    const el = document.getElementById(id);
    return el ? el.value : "";
}

function pushItemToGrid() {
    const desc = document.getElementById("m_desc").value || "Malzeme/Hizmet";
    const qty = parseFloat(document.getElementById("m_qty").value) || 1;
    const unit = document.getElementById("m_unit").value;
    const price = parseFloat(document.getElementById("m_price").value) || 0;
    const vat = parseFloat(document.getElementById("m_vat").value) || 20;

    // Aşama 46/47/54: "Diğer Seçenekler" ve KDV muafiyet sebebi — tamamı
    // opsiyonel, alan sayfada yoksa (waybill'de vat_exemption olmayabilir) boş geçilir.
    tempItemsList.push({
        desc, qty, unit, price, vat,
        vat_exemption_reason: _fieldValue("m_vat_exemption_reason"),
        seller_code: _fieldValue("m_seller_code"),
        buyer_code: _fieldValue("m_buyer_code"),
        barcode: _fieldValue("m_barcode"),
        brand: _fieldValue("m_brand"),
        model_name: _fieldValue("m_model_name"),
        origin_country: _fieldValue("m_origin_country"),
        additional_description: _fieldValue("m_additional_description"),
        item_note: _fieldValue("m_item_note"),
        classification_value: _fieldValue("m_classification_value"),
        classification_version: _fieldValue("m_classification_version"),
        classification_code: _fieldValue("m_classification_code"),
        related_waybill_number: _fieldValue("m_related_waybill_number"),
        related_waybill_date: _fieldValue("m_related_waybill_date"),
        order_number: _fieldValue("m_order_number"),
        order_date: _fieldValue("m_order_date"),
        additional_info_id: _fieldValue("m_additional_info_id"),
    });
    renderTableGrid();

    document.getElementById("m_desc").value = "";
    document.getElementById("m_qty").value = "1.00";
    document.getElementById("m_price").value = "0.00";
    document.getElementById("m_vat_calc").value = "0.00";
    document.getElementById("m_total_calc").value = "0.00";

    closeItemModal();
}

function removeGridItem(index) {
    tempItemsList.splice(index, 1);
    renderTableGrid();
}

function renderTableGrid() {
    const tbody = document.querySelector("#itemGridDisplayTable tbody");
    tbody.innerHTML = "";
    let totalBase = 0, totalVat = 0;

    tempItemsList.forEach((item, index) => {
        const base = item.qty * item.price;
        const vatAmt = (base * item.vat) / 100;
        const taxedAmt = base + vatAmt;
        totalBase += base; totalVat += vatAmt;

        tbody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${item.desc}</td>
                <td>${item.qty}</td>
                <td>${item.unit}</td>
                <td>${item.price.toFixed(2)}</td>
                <td>${item.vat}</td>
                <td>${vatAmt.toFixed(2)}</td>
                <td>${taxedAmt.toFixed(2)}</td>
                <td style="text-align:center;"><button type="button" class="mini-del-btn" onclick="removeGridItem(${index})">🗑️</button></td>
            </tr>
        `;
    });

    document.getElementById("lbl_base").innerText = totalBase.toFixed(2);
    document.getElementById("lbl_vat").innerText = totalVat.toFixed(2);
    document.getElementById("lbl_final").innerText = (totalBase + totalVat).toFixed(2);
    document.getElementById("items_json_data").value = JSON.stringify(tempItemsList);
}

function submitMainForm() {
    document.getElementById("mainInvoiceForm").submit();
}

// Sayfa genelinde TCMB menüsünü yöneten ve kurları işleyen fonksiyonlar
function toggleTCMBMenu(event) {
    event.stopPropagation();
    const menu = document.getElementById('tcmb-menu');
    if (menu) {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    }
}

// Menü dışına tıklandığında otomatik kapatma
document.addEventListener('click', function() {
    const menu = document.getElementById('tcmb-menu');
    if (menu) menu.style.display = 'none';
});

// Kur tipi seçildiğinde tetiklenen fonksiyon
function selectRateType(event, type) {
    event.preventDefault();
    const menu = document.getElementById('tcmb-menu');
    if (menu) menu.style.display = 'none';

    // Sayfadaki döviz türü select elementini buluyoruz (Örn: USD, EUR, TRY)
    // Eğer şablondaki select id'si farklıysa 'currency_select' kısmını ona göre güncelle
    const currencySelect = document.getElementById('currency_select') || document.getElementsByName('currency')[0];
    const currency = currencySelect ? currencySelect.value : 'USD';

    const inputField = document.getElementById('exchange_rate_input');

    if (currency === 'TRY' || currency === 'TL') {
        if (inputField) inputField.value = '1.0000';
        return;
    }

    if (inputField) inputField.value = "Yükleniyor...";

    // Senin views.py içinde güncellediğimiz URL ve parametre yapısı:
    fetch(`/invoices/api/tcmb-rate/?code=${currency}&type=${type}`)
        .then(response => {
            if (!response.ok) throw new Error('Kur çekilemedi.');
            return response.json();
        })
        .then(data => {
            if (data.success && inputField) {
                // TCMB'den gelen değeri alıp 4 basamaklı güvenli formata çeviriyoruz
                const rateFloat = parseFloat(data.rate.replace(',', '.'));
                inputField.value = rateFloat.toFixed(4);

                // Eğer fatura hesaplayıcında kurlar değiştiğinde tüm sayfayı yeniden
                // hesaplayan bir fonksiyon varsa (örneğin calculateTotals() gibi), onu burada tetikleyebilirsin:
                if (typeof calculateTotals === "function") {
                    calculateTotals();
                }
                console.log(`TCMB Kur Tarihi: ${data.date} - Seçilen: ${type}`);
            } else {
                alert(data.error || "Kur alınamadı.");
                if (inputField) inputField.value = "1.0000";
            }
        })
        .catch(error => {
            alert("Merkez Bankası kurları alınırken bir hata oluştu.");
            if (inputField) inputField.value = "1.0000";
            console.error(error);
        });
}