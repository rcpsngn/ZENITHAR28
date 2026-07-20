from django import forms
from .models import PortalSettings, DocumentDesignSettings


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
