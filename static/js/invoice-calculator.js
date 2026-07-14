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

function pushItemToGrid() {
    const desc = document.getElementById("m_desc").value || "Malzeme/Hizmet";
    const qty = parseFloat(document.getElementById("m_qty").value) || 1;
    const unit = document.getElementById("m_unit").value;
    const price = parseFloat(document.getElementById("m_price").value) || 0;
    const vat = parseFloat(document.getElementById("m_vat").value) || 20;

    tempItemsList.push({ desc, qty, unit, price, vat });
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