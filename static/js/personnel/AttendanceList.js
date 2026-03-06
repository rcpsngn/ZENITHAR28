from django.db import models
from employees.models import Employee


class Leave(models.Model):

    LEAVE_TYPES = (
        ("annual", "Yıllık"),
        ("sick", "Hastalık"),
        ("unpaid", "Ücretsiz"),
        ("maternity", "Doğum"),
        ("other", "Diğer"),
    )

    STATUS = (
        ("pending", "Bekliyor"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=LEAVE_TYPES)

    start_date = models.DateField()
    end_date = models.DateField()

    days = models.IntegerField()

    reason = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.type}"