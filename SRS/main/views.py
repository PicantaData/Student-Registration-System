from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from random import randint
from SRS import settings
from .models import Application, Notification
from .validator import MinimumLengthValidator, NumberValidator, UppercaseValidator


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

def Register(request):
    if request.method == 'POST':
        if('signup-email' in request.POST):
            email = request.POST['signup-email']
            password = request.POST['signup-password'] 
            confirm_password = request.POST['confirm-signup-password']

            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered!!!")
                return render(request, 'register.html')

            if(password!=confirm_password):
                messages.error(request, 'Password do not match!!!')
                return render(request, 'register.html')
            
            validators = [MinimumLengthValidator, NumberValidator, UppercaseValidator]
            try:
                for validator in validators:
                    validator().validate(password)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'register.html')

            # otp = send_otp(email)
            otp = 0
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['password'] = password
            messages.success(request, "OTP has been sent to your email address!!")
            return render(request, 'otp.html')
        
        if('otp' in request.POST):
            if(int(request.POST['otp'])==int(request.session['otp'])):
                email = request.session['email']
                password = request.session['password']
                User.objects.create_user(username=email, email=email, password=password)
                user = authenticate(username=email, password=password)
                login(request, user)
                return redirect('FillApplication')
            else:
                messages.error(request, "Invalid OTP!!!")
                return render(request, 'otp.html')
        
    return render(request, 'register.html')

def Login(request):
    if request.method == 'POST':
        email = request.POST['signin-email']
        password = request.POST['signin-password']

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            try:
                app = Application.objects.get(student=user)
            except Application.DoesNotExist:
                return redirect('FillApplication')

            return redirect('Dashboard')
        
        else:
            messages.error(request, 'Incorrect Email or Password!!!')
            return render(request, 'login.html')

    return render(request, 'login.html')

def Forget(request):
    if request.method=='POST':
        if 'otp' in request.POST:
            if(int(request.POST['otp'])==int(request.session['otp'])):
                messages.success(request, "OTP matched successfully!!!")
                return render(request, 'change_password.html')
            else:
                messages.error(request, "Invalid OTP!!!")
                return render(request, 'otp.html')
            
        if 'change-password' in request.POST:
            email = request.session['email']
            password = request.POST['change-password']
            confirm_password = request.POST['confirm-change-password']

            if password!=confirm_password : 
                messages.error(request, "Password do not match!!!")
                return render(request, 'change_password.html')
            
            validators = [MinimumLengthValidator, NumberValidator, UppercaseValidator]
            try:
                for validator in validators:
                    validator().validate(password)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'change_password.html')
            
            user = User.objects.get(username=email)
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been successfully changed !!!")
            return redirect('Login')

        if 'forget-email' in request.POST:
            email = request.POST['forget-email']
            if(User.objects.filter(username=email).exists()):
                otp = send_otp(email)
                request.session['otp'] = otp
                request.session['email'] = email
                messages.success(request, "OTP has been sent to your email address!!")
                return render(request, 'otp.html')
            else:
                messages.error(request, 'Email Does Not Exist')
                return render(request, 'forget.html')

    return render(request, 'forget.html')

@login_required
def FillApplication(request):
    user = request.user
    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        name = request.POST['name']
        dob = request.POST['dob']
        address = request.POST['address']
        phone = request.POST['phone']
        photo = request.FILES.get('photo')
        marks_10 = request.FILES.get('marks_10')
        marks_12 = request.FILES.get('marks_12')
        Application.objects.create(name=name, dob=dob, address=address, phone=phone, student=user, photo=photo, marks_10=marks_10, marks_12=marks_12)
        return redirect('Dashboard')

    return render(request, 'fill_application.html')


@login_required
def Dashboard(request):
    user = request.user
    app = Application.objects.get(student=user)
    notification = Notification.objects.filter(recipient=app) | Notification.objects.filter(filter_flag='Q') | Notification.objects.filter(filter_flag=app.app_status)
    
    context = {'user' : user, 'application' : app, 'notifications' : notification}

    return render(request, 'dashboard.html', context=context)
    

def Logout(request):
    logout(request)
    return redirect('Home')