from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CompanyProfile, PortalSettings
from .forms import PortalSettingsForm

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
    return render(request, 'settings_app/document-design.html')

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
    return render(request, 'settings_app/notifications.html')

@login_required
def system_settings(request):
    return render(request, 'settings_app/system.html')