# Aşama 38 (Bildirim) ve 39 (Sistem) için gerçek modeller.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("settings_app", "0003_documentdesignsettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationPreferences",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email_on_new_invoice", models.BooleanField(default=True)),
                ("notify_overdue_checks", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="notification_preferences", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Bildirim Tercihi",
                "verbose_name_plural": "Bildirim Tercihleri",
                "db_table": "notification_preferences",
            },
        ),
        migrations.CreateModel(
            name="SystemPreferences",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(choices=[("tr", "Türkçe (TR)"), ("en", "English (EN)")], default="tr", max_length=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="system_preferences", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Sistem Tercihi",
                "verbose_name_plural": "Sistem Tercihleri",
                "db_table": "system_preferences",
            },
        ),
    ]
