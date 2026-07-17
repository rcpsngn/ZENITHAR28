from django import forms
from .models import PortalSettings


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
