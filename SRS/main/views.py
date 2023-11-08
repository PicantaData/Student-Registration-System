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
    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']
        from_email = request.POST['email']
        to_list = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, to_list)
        return render(request, 'home.html')
    
    return render(request, 'home.html')


def Login(request):
    if request.method == 'POST':
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
            return redirect(reverse('FillApplication', args=(email,)))

        elif('signin-email' in request.POST):
            email = request.POST['signin-email']
            password = request.POST['signin-password']

            user = authenticate(username=email, password=password)

            if user is not None:
                login(request, user)
                try:
                    app = Application.objects.get(student=user)
                except Application.DoesNotExist:
                    return redirect(reverse('FillApplication', args=(email,)))
   
                return redirect(reverse('Dashboard', args=(email,)))
            
            else:
                messages.error(request, 'Bad Credentials!!!')
                return redirect('main/login.html')

    return render(request, 'main/login.html')


@login_required
def FillApplication(request, email):
    user = User.objects.get(email=email)
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        address = request.POST['address']
        phone = request.POST['phone']
        photo = request.POST['photo']
        marks_10 = request.POST['marks_10']
        marks_12 = request.POST['marks_12']

        Application.objects.create(name=name, dob=dob, address=address, phone=phone, student=user, photo=photo, marks_10=marks_10, marks_12=marks_12)
        return redirect(reverse('Dashboard', args=(email,)))

    return render(request, 'fill_application.html', {'email': email})


@login_required
def Dashboard(request, email):
    user = User.objects.get(username=email)
    app = Application.objects.get(student=user)
    context = {'user': user, 'application': app}

    return render(request, 'dashboard.html', context=context)
    

def Logout(request):
    logout(request)
    return redirect('Home')