from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from random import randint
from SRS import settings

def landing(request):
    return render(request, 'landing.html')

@csrf_exempt
def VerifyOtp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        try:
            User.objects.create_user(email=email, username=email, password=password)
            user = authenticate(username=email,password=password)
            login(request,user)
            return render(request,'landing.html')
        except:
            return JsonResponse({'response':'Email Not Verified'}, status=400)
        
    return JsonResponse({'response': 'Email Verified!'}, status=200)

def Signup(request):
    if request.method=='POST':
        email = request.POST['email']
        password = request.POST['password']
        confPassword = request.POST['confPassword']

        if password!=confPassword:
            messages.error(request, "Passwords do not match!")
            return redirect('Signup')
        
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already exists, you may log in!")
            return redirect("Login")
        
        subject = 'OTP for Login'
        otp = randint(100000, 999999)
        message = f"Your OTP is {otp}"
        from_email = settings.EMAIL_HOST_USER
        to_list = [email]
        # send_mail(subject, message, from_email, to_list)
        print(otp)
        # print(request.POST)
        return render(request, 'verify.html', {'otp':otp, 'email':email, 'pass1':password})

    return render(request,'signup.html')


def Login(request):
    if request.method=='POST':

        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(email=email).exists():
            #try except for wrong password
            # messages.error(request,"Username or Password is Incorrect")
            user = authenticate(username=email, password=password)
            login(request,user)
            return redirect('Home')
        else:
            messages.error(request,"Email ID does not exist.")
            return redirect('Login')
    return render(request,'login.html')
# def Login(request):
#     if request.method == 'POST':
#         if('signup-email' in request.POST):
#             email = request.POST['signup-email']

#             if User.objects.filter(username=email).exists():
#                 messages.error(request, "Email already registered.")
#                 return redirect('main/login.html')

#             subject = 'OTP'
#             otp = randint(100000, 999999)
#             message = f"Your OTP is {otp}"
#             from_email = settings.EMAIL_HOST_USER
#             to_list = [email]
#             send_mail(subject, message, from_email, to_list)
#             return

#         if('signin-password' in request.POST):
#             email = request.POST['signin-email']
#             password = request.POST['signin-password']

#             user = authenticate(username=email, password=password)

#             if user is not None:
#                 login(request, user)
#                 return render(request, 'main/index.html')
#             else:
#                 messages.error(request, 'Bad Credentials!!!')
#                 return redirect('main/login.html')
            
#     return render(request, 'main/login.html')

def Logout(request):
    logout(request)
    return redirect('Home')