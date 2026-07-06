from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class User(AbstractUser):

    ROLE_CHOICES = [
        ("admin", "Yönetici"),
        ("accountant", "Muhasebeci"),
        ("employee", "Çalışan"),
        ("viewer", "Görüntüleyici"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    company_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return self.username


class Subscription(models.Model):

    PLAN_CHOICES = [
        ("trial", "Deneme (7 Gün)"),
        ("monthly", "Aylık"),
        ("yearly", "Yıllık"),
    ]

    STATUS_CHOICES = [
        ("active", "Aktif"),
        ("expired", "Süresi Dolmuş"),
        ("cancelled", "İptal Edilmiş"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="trial")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    start_date = models.DateTimeField(default=timezone.now)

    end_date = models.DateTimeField(blank=True, null=True)

    auto_renew = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.end_date:

            if self.plan == "trial":
                self.end_date = timezone.now() + timedelta(days=7)

            elif self.plan == "monthly":
                self.end_date = timezone.now() + timedelta(days=30)

            elif self.plan == "yearly":
                self.end_date = timezone.now() + timedelta(days=365)

        super().save(*args, **kwargs)

    def is_active(self):
        return self.status == "active" and self.end_date > timezone.now()

    class Meta:
        db_table = "subscriptions"
        verbose_name = "Abonelik"
        verbose_name_plural = "Abonelikler"


class Notification(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title