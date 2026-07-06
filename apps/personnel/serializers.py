from rest_framework import serializers
from .models import Employee, Attendance, Salary, Leave
from datetime import datetime

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'identity_number', 'phone', 'email', 'address', 
                  'position', 'department', 'hire_date', 'salary', 'is_active', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'type', 'date', 'time', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    month_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Salary
        fields = ['id', 'employee', 'employee_name', 'month', 'year', 'month_name',
                  'base_salary', 'bonus', 'deductions', 'net_salary', 'status', 
                  'payment_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_month_name(self, obj):
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        return months[obj.month - 1] if 1 <= obj.month <= 12 else str(obj.month)

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Leave
        fields = ['id', 'employee', 'employee_name', 'type', 'start_date', 'end_date', 
                  'days', 'status', 'reason', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Başlangıç tarihi bitiş tarihinden sonra olamaz.")
        return data
