"""
apps/accounts/permissions.py

Excel'deki "Kimlik Doğrulama > Yetkilendirme" (Aşama 3) görevinin notu şuydu:
    "@permission_classes veya özel IsOwner, IsFinance yetki sınıfları yazılmalı."

Bu dosya tam olarak o eksikliği kapatır: DRF ViewSet/APIView'lara eklenebilecek,
User.role alanına (admin/accountant/employee/viewer) dayanan yeniden kullanılabilir
izin sınıfları tanımlar.

Kullanım:
    from apps.accounts.permissions import IsOwner, IsAdminOrAccountant, HasRole

    class SalaryViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, IsAdminOrAccountant]
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Nesne düzeyinde ekstra güvenlik katmanı: get_queryset() zaten user=request.user
    ile filtreleme yapıyor olsa da, bu sınıf "defense in depth" olarak nesnenin
    gerçekten istek atan kullanıcıya ait olduğunu bir kez daha doğrular.

    Nesnede doğrudan `user` alanı olabilir (ör. Employee, Invoice) ya da
    `employee.user` üzerinden dolaylı erişilebilir (ör. Attendance, Salary, Leave).
    """

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None)
        if owner is None and hasattr(obj, "employee"):
            owner = getattr(obj.employee, "user", None)
        return owner == request.user


class HasRole(BasePermission):
    """
    Kullanımı: `permission_classes = [IsAuthenticated, HasRole.for_roles("admin", "accountant")]`

    Doğrudan `permission_classes = [HasRole]` şeklinde KULLANILMAMALI; her zaman
    `.for_roles(...)` ile o view'a özel bir alt sınıf üretilmeli.
    """
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Django superuser / admin rolündeki kullanıcı her zaman geçer.
        if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
            return True
        return getattr(request.user, "role", None) in self.allowed_roles

    @classmethod
    def for_roles(cls, *roles):
        return type(f"HasRole_{'_'.join(roles)}", (cls,), {"allowed_roles": tuple(roles)})


class ReadOnlyOrHasRole(BasePermission):
    """
    GET/HEAD/OPTIONS gibi salt-okunur isteklere herkes (giriş yapmış kullanıcı) izinli;
    POST/PUT/PATCH/DELETE gibi değiştirme isteklerine yalnızca belirtilen roller izinli.
    Kullanımı: `ReadOnlyOrHasRole.for_roles("admin", "accountant")`
    """
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
            return True
        return getattr(request.user, "role", None) in self.allowed_roles

    @classmethod
    def for_roles(cls, *roles):
        return type(f"ReadOnlyOrHasRole_{'_'.join(roles)}", (cls,), {"allowed_roles": tuple(roles)})


# Sık kullanılan hazır kombinasyonlar (özel isimlerle, Excel notundaki "IsFinance" gibi):
IsAdminOnly = HasRole.for_roles()  # yalnızca admin/superuser (allowed_roles boş -> sadece admin kısayolu geçer)
IsAdminOrAccountant = HasRole.for_roles("accountant")  # + admin/superuser otomatik dahil
IsFinance = IsAdminOrAccountant  # Excel notundaki isimle birebir eşleşen takma ad
