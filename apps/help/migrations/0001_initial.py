from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(choices=[("gib", "GİB Duyurusu"), ("general", "Genel Duyuru")], default="general", max_length=10)),
                ("title", models.CharField(max_length=255)),
                ("summary", models.CharField(blank=True, max_length=500)),
                ("published_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Duyuru",
                "verbose_name_plural": "Duyurular",
                "db_table": "announcements",
                "ordering": ["-published_date"],
            },
        ),
    ]
