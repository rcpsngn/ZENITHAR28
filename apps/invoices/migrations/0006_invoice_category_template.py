from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_invoice_is_read_invoice_is_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_type',
            field=models.CharField(
                choices=[
                    ('temel', 'Temel'),
                    ('ticari', 'Ticari'),
                    ('yolcu_beraber', 'Yolcu Beraber'),
                    ('ihracat', 'İhracat'),
                    ('hal', 'Hal'),
                    ('kamu', 'Kamu'),
                    ('enerji', 'Enerji'),
                    ('ilac_tibbi_cihaz', 'İlaç ve Tıbbi Cihaz'),
                    ('yatirim_tesvik', 'Yatırım Teşvik'),
                    ('insaat_demiri_izleme_sistemi', 'İnşaat Demiri İzleme Sistemi'),
                ],
                default='temel',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_category',
            field=models.CharField(
                choices=[
                    ('satis', 'Satış'), ('iade', 'İade'), ('tevkifat', 'Tevkifat'),
                    ('istisna', 'İstisna'), ('ozel_matrah', 'Özel Matrah'), ('ihrac_kayitli', 'İhraç Kayıtlı'),
                    ('sgk', 'SGK'), ('komisyoncu', 'Komisyoncu'), ('hks_satis', 'HKS Satış'),
                    ('hks_komisyoncu', 'HKS Komisyoncu'), ('tevkifat_iade', 'Tevkifat İade'),
                    ('konaklama_vergisi', 'Konaklama Vergisi'), ('sarj', 'Şarj'), ('sarj_anlik', 'Şarj Anlık'),
                    ('teknoloji_destek', 'Teknoloji Destek'), ('ytb_satis', 'YTB Satış'),
                    ('ytb_istisna', 'YTB İstisna'), ('ytb_iade', 'YTB İade'), ('ytb_tevkifat', 'YTB Tevkifat'),
                    ('ytb_tevkifat_iade', 'YTB Tevkifat İade'),
                ],
                default='satis',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_template',
            field=models.CharField(default='varsayilan', max_length=30),
        ),
    ]
