from django.shortcuts import render

def home(request):
    return render(request, "index.html")

def login_view(request):
    return render(request, "login.html")

def employees(request):
    return render(request, "employees.html")

def personnel(request):
    return render(request, "personnel.html")

def leaves(request):
    return render(request, "leaves.html")