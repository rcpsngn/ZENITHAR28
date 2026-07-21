# DÜZELTME MİGRASYONU
#
# Neden gerekti: api_url alanı, PortalSettings modelini ilk oluşturan
# 0002_portalsettings.py migration dosyası İÇİNE sonradan eklenmişti (ayrı bir
# migration olarak değil). Eğer siz `migrate` komutunu api_url eklenmeden ÖNCEKİ
# bir sürümle çalıştırdıysanız, Django o migration'ı "uygulandı" olarak
# işaretlemiş olur ve dosya sonradan değişse bile TEKRAR ÇALIŞTIRMAZ — bu yüzden
# sizin veritabanınızda api_url sütunu hiç oluşmadı.
#
# Bu migration, sütunu var olan tabloya sonradan ekler (mevcut satırlarınız
# silinmez, api_url alanları boş/"" olarak başlar).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("settings_app", "0004_notification_system_preferences"),
    ]

    operations = [
        migrations.AddField(
            model_name="portalsettings",
            name="api_url",
            field=models.URLField(
                blank=True, default="",
                help_text="Entegratörün verdiği API adresi (ör. https://api.saglayici.com)",
            ),
            preserve_default=False,
        ),
    ]
