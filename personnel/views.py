from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Attendance, Salary, Leave
from .serializers import EmployeeSerializer, AttendanceSerializer, SalarySerializer, LeaveSerializer
from datetime import datetime, date

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'department', 'position']
    search_fields = ['full_name', 'identity_number', 'phone', 'email']
    ordering_fields = ['full_name', 'hire_date', 'salary']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Employee.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        employee = self.get_object()
        employee.is_active = not employee.is_active
        employee.save()
        return Response({'status': 'success', 'is_active': employee.is_active})

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'type', 'date']
    ordering_fields = ['date', 'time']
    ordering = ['-date', '-time']
    
    def get_queryset(self):
        return Attendance.objects.filter(employee__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def quick_entry(self, request):
        employee_id = request.data.get('employee')
        attendance_type = request.data.get('type', 'entry')
        
        try:
            employee = Employee.objects.get(id=employee_id, user=request.user)
            attendance = Attendance.objects.create(
                employee=employee,
                type=attendance_type,
                date=date.today(),
                time=datetime.now().time()
            )
            serializer = self.get_serializer(attendance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Employee.DoesNotExist:
            return Response({'error': 'Personel bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

class SalaryViewSet(viewsets.ModelViewSet):
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'year', 'month']
    ordering_fields = ['year', 'month', 'payment_date']
    ordering = ['-year', '-month']
    
    def get_queryset(self):
        return Salary.objects.filter(employee__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        salary = self.get_object()
        salary.status = 'paid'
        salary.payment_date = date.today()
        salary.save()
        return Response({'status': 'success', 'message': 'Maaş ödendi olarak işaretlendi'})

class LeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'type', 'status']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        return Leave.objects.filter(employee__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.save()
        return Response({'status': 'success', 'message': 'İzin onaylandı'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.notes = request.data.get('notes', '')
        leave.save()
        return Response({'status': 'success', 'message': 'İzin reddedildi'})
