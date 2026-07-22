from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CompanyProfile, PortalSettings, DocumentDesignSettings, NotificationPreferences, SystemPreferences, DocumentTemplate
from .forms import PortalSettingsForm, DocumentDesignSettingsForm, NotificationPreferencesForm, SystemPreferencesForm, DocumentTemplateCustomizeForm, DocumentTemplateUploadForm
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
def document_numbering_settings(request):
    """Eskiden 'document_design' idi; seri no öneki/alt not ayarları burada kaldı."""
    design, created = DocumentDesignSettings.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = DocumentDesignSettingsForm(request.POST, instance=design)
        if form.is_valid():
            form.save()
            messages.success(request, "Belge tasarım ayarları kaydedildi. Yeni faturalar bu ayarlarla numaralandırılacak.")
            return redirect("document_numbering_settings")
    else:
        form = DocumentDesignSettingsForm(instance=design)
    return render(request, 'settings_app/document-numbering.html', {"form": form})


# ============================================================
# BELGE TASARIMLARI (liste + özelleştirme + hazır .xslt yükleme)
# ============================================================

def _sample_invoice_for(user, document_type):
    """Önizleme için kullanıcının o türdeki en güncel faturasını, yoksa None döner."""
    from apps.invoices.models import Invoice
    return Invoice.objects.filter(user=user, type=document_type).order_by("-issue_date").first()


@login_required
def document_design(request):
    templates = DocumentTemplate.objects.filter(user=request.user)
    return render(request, 'settings_app/document-design-list.html', {"templates": templates})


@login_required
def document_design_customize(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(DocumentTemplate, id=id, user=request.user)

    if request.method == "POST":
        form = DocumentTemplateCustomizeForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, f"'{template.name}' belge tasarımı kaydedildi.")
            return redirect("document_design")
    else:
        form = DocumentTemplateCustomizeForm(instance=instance)

    doc_type = (instance.document_type if instance else request.GET.get("type", "e-fatura"))
    sample_invoice = _sample_invoice_for(request.user, doc_type)

    return render(request, 'settings_app/document-design-customize.html', {
        "form": form,
        "instance": instance,
        "sample_invoice": sample_invoice,
    })


@login_required
def document_design_upload(request):
    if request.method == "POST":
        form = DocumentTemplateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, f"'{template.name}' belge tasarımı yüklendi.")
            return redirect("document_design")
        else:
            messages.error(request, "Yükleme başarısız: " + " ".join(
                e for errs in form.errors.values() for e in errs
            ))
    return redirect("document_design")


@login_required
def document_design_preview(request, id):
    template = get_object_or_404(DocumentTemplate, id=id, user=request.user)
    sample_invoice = _sample_invoice_for(request.user, template.document_type)

    xslt_result = None
    if template.creation_type == "uploaded" and template.uploaded_file:
        xslt_result = _try_render_xslt(template, sample_invoice)

    return render(request, 'settings_app/document-design-preview.html', {
        "template": template,
        "sample_invoice": sample_invoice,
        "xslt_result": xslt_result,
    })


def _try_render_xslt(template, invoice):
    """
    Yüklenen .xslt dosyasını gerçekten çalıştırmayı DENER. Sağlayıcıya özel
    XML şeması bilinmediği için (her entegratörün beklediği XML alan adları
    farklı olabilir), başarısız olursa sistemi ÇÖKERTMEZ; kullanıcıya anlaşılır
    bir mesaj döner. Başarılı olursa dönüştürülmüş HTML/metin çıktısını verir.
    """
    try:
        from lxml import etree
    except ImportError:
        return {"success": False, "message": "Sunucuda lxml kurulu değil; .xslt önizlemesi için 'pip install lxml' gerekiyor."}

    if not invoice:
        return {"success": False, "message": "Bu belge türü için örnek bir fatura bulunamadı; önizleme yapılamıyor."}

    try:
        xml_bytes = _invoice_to_simple_xml(invoice)
        xslt_doc = etree.parse(template.uploaded_file.path)
        transform = etree.XSLT(xslt_doc)
        xml_doc = etree.fromstring(xml_bytes)
        result = transform(xml_doc)
        return {"success": True, "output": str(result)}
    except Exception as exc:
        return {
            "success": False,
            "message": (
                "Bu .xslt dosyası örnek fatura verisiyle çalıştırılamadı. "
                "Sağlayıcınızın XML şeması farklı olabilir (hata: "
                f"{exc.__class__.__name__}). Kod tarafı (lxml XSLT motoru) çalışıyor; "
                "gerçek bir fatura göndermeden önce sağlayıcının XML örneğiyle test edin."
            ),
        }


def _invoice_to_simple_xml(invoice) -> bytes:
    """Faturadan BASİT bir XML üretir (gerçek UBL-TR şeması değildir, genel bir yaklaşımdır)."""
    from xml.sax.saxutils import escape
    items_xml = "".join(
        f"<Item><Description>{escape(i.description)}</Description>"
        f"<Quantity>{i.quantity}</Quantity><UnitPrice>{i.unit_price}</UnitPrice>"
        f"<Total>{i.total}</Total></Item>"
        for i in invoice.items.all()
    )
    xml = (
        f"<Invoice>"
        f"<InvoiceNumber>{escape(invoice.invoice_number)}</InvoiceNumber>"
        f"<IssueDate>{invoice.issue_date}</IssueDate>"
        f"<CustomerName>{escape(invoice.customer_name)}</CustomerName>"
        f"<TotalAmount>{invoice.total_amount}</TotalAmount>"
        f"<Items>{items_xml}</Items>"
        f"</Invoice>"
    )
    return xml.encode("utf-8")


@login_required
def document_design_delete(request, id):
    get_object_or_404(DocumentTemplate, id=id, user=request.user).delete()
    messages.success(request, "Belge tasarımı silindi.")
    return redirect("document_design")


@login_required
def document_design_set_default(request, id):
    template = get_object_or_404(DocumentTemplate, id=id, user=request.user)
    template.is_default = True
    template.save()  # model.save() aynı türdeki diğer varsayılanları otomatik kaldırır
    messages.success(request, f"'{template.name}' bu belge türü için varsayılan yapıldı.")
    return redirect("document_design")


@login_required
def document_design_toggle_active(request, id):
    template = get_object_or_404(DocumentTemplate, id=id, user=request.user)
    template.is_active = not template.is_active
    template.save(update_fields=["is_active"])
    return redirect("document_design")


@login_required
def document_design_download(request, id):
    template = get_object_or_404(DocumentTemplate, id=id, user=request.user)
    if template.creation_type != "uploaded" or not template.uploaded_file:
        raise Http404("Bu tasarımın indirilebilir bir dosyası yok (özelleştirilmiş tasarımlar dosya olarak indirilemez).")
    return FileResponse(template.uploaded_file.open("rb"), as_attachment=True, filename=template.uploaded_file.name.split("/")[-1])

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