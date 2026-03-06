from django.contrib import admin
from .models import Employee, Attendance, Salary, Leave

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'identity_number', 'position', 'salary', 'is_active', 'hire_date']
    list_filter = ['is_active', 'department', 'hire_date']
    search_fields = ['full_name', 'identity_number', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'type', 'date', 'time']
    list_filter = ['type', 'date']
    search_fields = ['employee__full_name']

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'net_salary', 'status', 'payment_date']
    list_filter = ['status', 'year', 'month']
    search_fields = ['employee__full_name']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'type', 'start_date', 'end_date', 'days', 'status']
    list_filter = ['type', 'status', 'start_date']
    search_fields = ['employee__full_name']
