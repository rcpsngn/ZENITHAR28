from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, AttendanceViewSet, SalaryViewSet, LeaveViewSet
from . import views  # Şablon fonksiyonları için views import edildi

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'salaries', SalaryViewSet, basename='salary')
router.register(r'leaves', LeaveViewSet, basename='leave')

urlpatterns = [
    # Senin mevcut DRF API rotaların (Aynen korundu)
    path('api/', include(router.urls)),  # API yollarını 'api/' altına alarak çakışmayı önledik

    # Bizim HTML Şablon (Template) rotalarımız
    path('calisanlar/', views.calisanlar, name='calisanlar'),
    path('giris-cikis/', views.giris_cikis, name='giris_cikis'),
    path('yillik-izin/', views.yillik_izin, name='yillik_izin'),
]