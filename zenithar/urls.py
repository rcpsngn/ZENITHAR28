from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect


def home(request):
    # Arama kutusundan gelen kelimeyi yakalıyoruz
    query = request.GET.get('q', '').strip().lower()

    if query:
        # 1. AKILLI KOMUT: Kullanıcı 'fatura' yazıp arattıysa doğrudan e-fatura oluşturmaya gider
        if query == 'fatura':
            return redirect('invoices_create')

        # 2. AKILLI KOMUT: Kullanıcı 'cari' yazıp arattıysa cari sayfasına gider
        # (İleride current-accounts içindeki url ismine göre burayı güncelleyebiliriz)
        elif query == 'cari':
            return redirect('home')

    # Eğer arama yapılmadıysa veya komut eşleşmediyse mevcut ana sayfa düzeni aynen devam eder
    return render(request, "home.html")


def reports_view(request):
    return render(request, "reports/general-reports.html")


urlpatterns = [

    path('', home, name="home"),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('waybill/', include('waybill.urls')),
    path('invoices/', include('invoices.urls')),
    path('checks/', include('checks.urls')),
    path('current-accounts/', include('current_accounts.urls')),
    path('personnel/', include('personnel.urls')),
    path('reports/', reports_view, name="reports"),
    path('help/', include('help.urls')),
    path('settings/', include('settings_app.urls')),
]

admin.site.site_header = "ZENITHAR Yönetim Paneli"
admin.site.site_title = "ZENITHAR Admin"
admin.site.index_title = "Yönetim Paneli"
