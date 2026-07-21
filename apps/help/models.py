from django.db import models


class Announcement(models.Model):
    """
    Ana sayfadaki 'GİB Duyuruları' ve 'Genel Duyurular' panelleri için
    (Uyumsoft portalı referans alınarak istenen ana sayfa tasarımının bir parçası).

    NOT — kapsam sınırı: Gerçek GİB duyuruları GİB'in kendi sisteminden (RSS/API)
    çekilmiyor; bunun için resmi bir GİB veri kaynağına/anlaşmaya ihtiyaç var.
    Bunun yerine bu model Django Admin üzerinden ELLE yönetilebilir bir duyuru
    panosu sağlıyor — firma sahibi/admin kendi duyurularını (bakım bildirimi,
    mevzuat hatırlatması vb.) buradan yayınlayabilir. Kayıt yokken şablon,
    referans ekran görüntüsündeki gibi zarif bir "Kayıt Yok" boş durumu gösterir.
    """
    CATEGORY_CHOICES = [
        ("gib", "GİB Duyurusu"),
        ("general", "Genel Duyuru"),
    ]

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="general")
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=500, blank=True)
    published_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "announcements"
        verbose_name = "Duyuru"
        verbose_name_plural = "Duyurular"
        ordering = ["-published_date"]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class HelpVideo(models.Model):
    """Aşama 32 (Yardım - Videolar): admin tarafından yönetilebilir eğitim videoları."""
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo embed linki (opsiyonel).")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "help_videos"
        verbose_name = "Yardım Videosu"
        verbose_name_plural = "Yardım Videoları"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class UsageTip(models.Model):
    """Aşama 33 (Yardım - Kılavuz): admin tarafından yönetilebilir kullanım ipuçları."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    icon = models.CharField(max_length=50, default="bi-lightning", help_text="Bootstrap Icons sınıf adı.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "usage_tips"
        verbose_name = "Kullanım İpucu"
        verbose_name_plural = "Kullanım İpuçları"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
