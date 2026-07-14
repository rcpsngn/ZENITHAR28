from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('current_accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('unit', models.CharField(choices=[('Adet', 'Adet'), ('Kg', 'Kilogram'), ('Metre', 'Metre'), ('Litre', 'Litre'), ('Kutu', 'Kutu'), ('Paket', 'Paket')], default='Adet', max_length=20)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('vat_rate', models.DecimalField(decimal_places=2, default=20, max_digits=5)),
                ('min_stock_level', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ürün / Stok',
                'verbose_name_plural': 'Ürünler / Stoklar',
                'db_table': 'products',
                'ordering': ['name'],
            },
        ),
    ]
