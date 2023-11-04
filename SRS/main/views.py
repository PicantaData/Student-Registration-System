from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from random import randint
from SRS import settings
from .models import Application

def send_otp(email):
    subject = 'OTP'
    otp = randint(100000, 999999)
    message = f"Your OTP is {otp}"
    from_email = settings.EMAIL_HOST_USER
    to_list = [email]
    send_mail(subject, message, from_email, to_list)
    return otp

def Home(request):
    return render(request, 'home.html')

def Login(request):
    if request.method == 'POST':
        print(request.POST)
        if('signup-email' in request.POST):
            email = request.POST['signup-email']
            password = request.POST['signup-password'] 
            confirm_password = request.POST['confirm-signup-password']

            # if User.objects.filter(username=email).exists():
            #     messages.error(request, "Email already registered.")
            #     return redirect('main/login.html')

            otp = send_otp(email)
            context = {'email':email, 'password':password, 'otp':otp}
            return render(request, 'verify.html', context)
        
        elif('verified-email' in request.POST):
            email = request.POST['verified-email']
            password = request.POST['password']
            User.objects.create_user(username=email, email=email, password=password)
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect(reverse('Dashboard', args=(email,)))

        elif('signin-email' in request.POST):
            email = request.POST['signin-email']
            password = request.POST['signin-password']

            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse('Dashboard', args=(email,)))
            else:
                messages.error(request, 'Bad Credentials!!!')
                return redirect('main/login.html')

    return render(request, 'main/login.html')

@login_required
def Dashboard(request, email):
    user = User.objects.get(username=email)
    try:
        app = Application.objects.get(student=user)
    except Application.DoesNotExist:
        context = {'user': user}
        return render(request, 'fill_app.html', context)
    
    context = {'user': user, 'application': app}
    return render(request, 'dashboard.html', context)
    
def Logout(request):
    logout(request)
    return redirect('Home')