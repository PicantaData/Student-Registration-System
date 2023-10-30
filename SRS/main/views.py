from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from random import randint
from SRS import settings

def landing(request):
    return render(request, 'landing.html')

def Login(request):
    if request.method == 'POST':
        if('signup-email' in request.POST):
            email = request.POST['signup-email']

            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('main/login.html')

            subject = 'OTP'
            otp = randint(100000, 999999)
            message = f"Your OTP is {otp}"
            from_email = settings.EMAIL_HOST_USER
            to_list = [email]
            send_mail(subject, message, from_email, to_list)
            return

        if('signin-password' in request.POST):
            email = request.POST['signin-email']
            password = request.POST['signin-password']

            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)
                return render(request, 'main/index.html')
            else:
                messages.error(request, 'Bad Credentials!!!')
                return redirect('main/login.html')
            
    return render(request, 'main/login.html')

def Logout(request):
    logout(request)
    return redirect('landing.html')