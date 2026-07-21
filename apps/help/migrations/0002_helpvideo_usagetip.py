from django.db import migrations, models


def seed_initial_data(apps, schema_editor):
    HelpVideo = apps.get_model("help", "HelpVideo")
    UsageTip = apps.get_model("help", "UsageTip")

    HelpVideo.objects.create(
        title="Zenithar E-Fatura Nasıl Oluşturulur?",
        description="Temel faturalama, cari seçimi ve e-fatura gönderme adımları eğitimi.",
        order=1,
    )
    HelpVideo.objects.create(
        title="E-İrsaliye ve Sevkiyat Yönetimi",
        description="Şoför, araç bilgileri ekleme ve irsaliye düzenleme rehberi.",
        order=2,
    )
    UsageTip.objects.create(
        title="Klavyeden Hızlı Arama Kullanımı",
        content="Topbar üzerinde yer alan arama çubuğuna tıklayarak rehber paneli açabilir, "
                "doğrudan \"fatura\" veya \"cari\" yazarak ilgili hızlı işlem ekranlarına ışınlanabilirsiniz.",
        icon="bi-lightning",
        order=1,
    )
    UsageTip.objects.create(
        title="Gece / Gündüz Modu Hafızası",
        content="Üst paneldeki buton yardımıyla geçiş yaptığınız tema tercihiniz tarayıcı "
                "hafızasında saklanır. Sayfayı yenilediğinizde düzeniniz bozulmaz.",
        icon="bi-moon-stars",
        order=2,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("help", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HelpVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.CharField(blank=True, max_length=500)),
                ("video_url", models.URLField(blank=True, help_text="YouTube/Vimeo embed linki (opsiyonel).")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Yardım Videosu",
                "verbose_name_plural": "Yardım Videoları",
                "db_table": "help_videos",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="UsageTip",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("icon", models.CharField(default="bi-lightning", max_length=50, help_text="Bootstrap Icons sınıf adı.")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Kullanım İpucu",
                "verbose_name_plural": "Kullanım İpuçları",
                "db_table": "usage_tips",
                "ordering": ["order", "id"],
            },
        ),
        migrations.RunPython(seed_initial_data, noop_reverse),
    ]
