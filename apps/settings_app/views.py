from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CompanyProfile, PortalSettings, DocumentDesignSettings, NotificationPreferences, SystemPreferences
from .forms import PortalSettingsForm, DocumentDesignSettingsForm, NotificationPreferencesForm, SystemPreferencesForm
from django.http import FileResponse, Http404
from django.conf import settings as django_settings
import os

@login_required
def company_info(request):
    profile, created = CompanyProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.company_name = request.POST.get("company_name", profile.company_name)
        profile.tax_id = request.POST.get("tax_id", "")
        profile.tax_office = request.POST.get("tax_office", "")
        profile.address = request.POST.get("address", "")
        profile.phone = request.POST.get("phone", "")
        profile.email = request.POST.get("email", "")
        profile.website = request.POST.get("website", "")
        if request.FILES.get("logo"):
            profile.logo = request.FILES["logo"]
        profile.save()
        return redirect("company_info")

    return render(request, 'settings_app/company-info.html', {"profile": profile})

@login_required
def definitions(request):
    return render(request, 'settings_app/definitions.html')

@login_required
def accountant(request):
    return render(request, 'settings_app/accountant.html')

@login_required
def document_design(request):
    design, created = DocumentDesignSettings.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = DocumentDesignSettingsForm(request.POST, instance=design)
        if form.is_valid():
            form.save()
            messages.success(request, "Belge tasarım ayarları kaydedildi. Yeni faturalar bu ayarlarla numaralandırılacak.")
            return redirect("document_design")
    else:
        form = DocumentDesignSettingsForm(instance=design)
    return render(request, 'settings_app/document-design.html', {"form": form})

@login_required
def portal_settings(request):
    portal, created = PortalSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = PortalSettingsForm(request.POST, instance=portal)
        if form.is_valid():
            portal = form.save(commit=False)
            new_password = form.cleaned_data.get("api_password")
            if new_password:
                # Şifre yalnızca kullanıcı YENİ bir değer girdiyse güncellenir;
                # boş bırakılırsa mevcut şifrelenmiş şifre olduğu gibi korunur.
                portal.set_password(new_password)
            portal.is_verified = False  # bilgiler değiştiyse yeniden test edilmesi gerekir
            portal.save()
            messages.success(request, "Portal ayarları kaydedildi. Devam etmeden önce 'Bağlantıyı Test Et' butonunu kullanın.")
            return redirect("portal_settings")
    else:
        form = PortalSettingsForm(instance=portal)

    return render(request, 'settings_app/portal.html', {
        "form": form,
        "portal": portal,
        "masked_password": portal.get_masked_password() if portal.encrypted_password else None,
    })

@login_required
def notification_settings(request):
    prefs, _ = NotificationPreferences.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = NotificationPreferencesForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Bildirim tercihleri kaydedildi.")
            return redirect("notification_settings")
    else:
        form = NotificationPreferencesForm(instance=prefs)
    return render(request, 'settings_app/notifications.html', {"form": form})

@login_required
def system_settings(request):
    prefs, _ = SystemPreferences.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = SystemPreferencesForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Sistem tercihleri kaydedildi.")
            return redirect("system_settings")
    else:
        form = SystemPreferencesForm(instance=prefs)
    return render(request, 'settings_app/system.html', {"form": form})

@login_required
def system_backup_download(request):
    """
    Aşama 39: 'SQL Veritabanı Yedeği İndir' butonunu gerçek bir dosya indirmeye bağlar.
    Yalnızca SQLite kullanılıyorken çalışır (Postgres'e geçilirse pg_dump ile
    değiştirilmesi gerekir — bilinçli küçük kapsamlı bir uygulama).
    """
    db_config = django_settings.DATABASES.get("default", {})
    if "sqlite3" not in db_config.get("ENGINE", ""):
        raise Http404("Yedek indirme yalnızca SQLite veritabanında desteklenir.")
    db_path = db_config.get("NAME")
    if not db_path or not os.path.exists(db_path):
        raise Http404("Veritabanı dosyası bulunamadı.")
    return FileResponse(open(db_path, "rb"), as_attachment=True, filename="zenithar_yedek.sqlite3")