from django.apps import AppConfig


class CurrentAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.current_accounts"

    def ready(self):
        from . import signals  # noqa: F401 — post_save alıcısını kaydeder
