from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=200)),
                ('account_number', models.CharField(blank=True, max_length=50)),
                ('type', models.CharField(choices=[('deposit', 'Para Girişi'), ('withdrawal', 'Para Çıkışı')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateField()),
                ('description', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Banka Hareketi',
                'verbose_name_plural': 'Banka Hareketleri',
                'db_table': 'bank_transactions',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='CashTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('in', 'Kasa Girişi'), ('out', 'Kasa Çıkışı')], max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateField()),
                ('description', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Kasa İşlemi',
                'verbose_name_plural': 'Kasa İşlemleri',
                'db_table': 'cash_transactions',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='POSTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_type', models.CharField(choices=[('credit', 'Kredi Kartı'), ('debit', 'Banka Kartı')], default='credit', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('commission_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('date', models.DateField()),
                ('description', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pos_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'POS İşlemi',
                'verbose_name_plural': 'POS İşlemleri',
                'db_table': 'pos_transactions',
                'ordering': ['-date'],
            },
        ),
    ]
