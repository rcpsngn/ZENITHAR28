from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def company_info(request):
    return render(request, 'settings_app/company-info.html')

@login_required
def definitions(request):
    return render(request, 'settings_app/definitions.html')

@login_required
def accountant(request):
    return render(request, 'settings_app/accountant.html')

@login_required
def document_design(request):
    return render(request, 'settings_app/document-design.html')

@login_required
def portal_settings(request):
    return render(request, 'settings_app/portal.html')

@login_required
def notification_settings(request):
    return render(request, 'settings_app/notifications.html')

@login_required
def system_settings(request):
    return render(request, 'settings_app/system.html')