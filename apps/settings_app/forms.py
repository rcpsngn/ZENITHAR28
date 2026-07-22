from django import forms
from .models import PortalSettings, DocumentDesignSettings, NotificationPreferences, SystemPreferences, DocumentTemplate


class PortalSettingsForm(forms.ModelForm):
    # Şifre modelde encrypted_password olarak tutulur; formda ayrı, düz-metin
    # bir alan olarak alınır ve view içinde set_password() ile şifrelenir.
    api_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "search-input", "placeholder": "Değiştirmek için doldurun"}),
        label="API Bağlantı Şifresi",
    )

    class Meta:
        model = PortalSettings
        fields = ["provider", "api_url", "api_username"]
        widgets = {
            "provider": forms.Select(attrs={"class": "search-input"}),
            "api_url": forms.URLInput(attrs={"class": "search-input", "placeholder": "https://api.saglayici.com"}),
            "api_username": forms.TextInput(attrs={"class": "search-input"}),
        }


class DocumentDesignSettingsForm(forms.ModelForm):
    class Meta:
        model = DocumentDesignSettings
        fields = ["invoice_number_prefix", "footer_note"]
        widgets = {
            "invoice_number_prefix": forms.TextInput(attrs={"class": "search-input", "maxlength": "10"}),
            "footer_note": forms.Textarea(attrs={"class": "search-input", "style": "height:70px; padding:6px;"}),
        }

    def clean_invoice_number_prefix(self):
        value = self.cleaned_data["invoice_number_prefix"].strip().upper()
        if not value.isalnum():
            raise forms.ValidationError("Seri no öneki yalnızca harf ve rakam içerebilir.")
        return value


class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = ["email_on_new_invoice", "notify_overdue_checks"]


class SystemPreferencesForm(forms.ModelForm):
    class Meta:
        model = SystemPreferences
        fields = ["language"]
        widgets = {"language": forms.Select(attrs={"class": "search-input"})}


class DocumentTemplateCustomizeForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = [
            "document_type", "name", "is_active", "is_default",
            "sender_title", "discount_replaces", "unit_price_format",
            "logo", "signature", "bank_info_html", "note", "sender_note", "recipient_note",
        ]
        widgets = {
            "document_type": forms.Select(attrs={"class": "search-input"}),
            "name": forms.TextInput(attrs={"class": "search-input"}),
            "sender_title": forms.TextInput(attrs={"class": "search-input"}),
            "unit_price_format": forms.Select(attrs={"class": "search-input"}),
            "bank_info_html": forms.Textarea(attrs={"class": "search-input", "rows": 4}),
            "note": forms.Textarea(attrs={"class": "search-input", "rows": 2}),
            "sender_note": forms.Textarea(attrs={"class": "search-input", "rows": 2}),
            "recipient_note": forms.Textarea(attrs={"class": "search-input", "rows": 2}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.creation_type = "customized"
        if commit:
            instance.save()
        return instance


class DocumentTemplateUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = ["document_type", "name", "is_active", "is_default", "uploaded_file"]
        widgets = {
            "document_type": forms.Select(attrs={"class": "search-input"}),
            "name": forms.TextInput(attrs={"class": "search-input"}),
        }

    def clean_uploaded_file(self):
        f = self.cleaned_data.get("uploaded_file")
        if f and not f.name.lower().endswith(".xslt"):
            raise forms.ValidationError("Yalnızca '.xslt' uzantılı dosyalar yüklenebilir.")
        return f

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.creation_type = "uploaded"
        if commit:
            instance.save()
        return instance
