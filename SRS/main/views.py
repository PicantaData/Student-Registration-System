from django.shortcuts import render, redirect

def landing(request):
    return render(request, 'landing.html')

def Login(request):
    return render(request, 'login.html')

def Logout(request):
    return redirect('landing.html')