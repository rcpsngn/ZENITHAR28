from django.db import models
from accounts.models import User

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employees')
    full_name = models.CharField(max_length=200)
    identity_number = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Personel'
        verbose_name_plural = 'Personeller'
        ordering = ['full_name']

class Attendance(models.Model):
    TYPE_CHOICES = [
        ('entry', 'Giriş'),
        ('exit', 'Çıkış'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendances'
        verbose_name = 'Giriş-Çıkış'
        verbose_name_plural = 'Giriş-Çıkışlar'
        ordering = ['-date', '-time']

class Salary(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('paid', 'Ödendi'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    month = models.IntegerField()
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'salaries'
        verbose_name = 'Maaş'
        verbose_name_plural = 'Maaşlar'
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']

class Leave(models.Model):
    TYPE_CHOICES = [
        ('annual', 'Yıllık İzin'),
        ('sick', 'Hastalık İzni'),
        ('unpaid', 'Ücretsiz İzin'),
        ('maternity', 'Doğum İzni'),
        ('other', 'Diğer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaves'
        verbose_name = 'İzin'
        verbose_name_plural = 'İzinler'
        ordering = ['-start_date']
