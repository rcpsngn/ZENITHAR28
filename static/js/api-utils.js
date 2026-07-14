// static/js/api-utils.js
// Django REST Framework API'lerine (personel, cari hesap, çek/senet vb.)
// istek atarken CSRF token'ı otomatik ekleyen ortak yardımcı fonksiyon.

function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
}

// apiFetch: fetch()'in CSRF + JSON header'larını otomatik ekleyen sürümü.
async function apiFetch(url, options = {}) {
    const headers = Object.assign(
        {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        options.headers || {}
    );
    const response = await fetch(url, Object.assign({}, options, { headers }));
    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok) {
        const message = (data && (data.detail || JSON.stringify(data))) || `Hata (${response.status})`;
        throw new Error(message);
    }
    return data;
}
