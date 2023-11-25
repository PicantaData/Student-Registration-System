from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from random import randint
from SRS import settings
from .models import Application, Notification, Question, ApplicantResponse, Test
from .validator import MinimumLengthValidator, NumberValidator, UppercaseValidator
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone

@staff_member_required
def populateTest(request):
    if request.method == 'POST':
        startTime = request.POST['start-time']
        endTime = request.POST['end-time']
        applications = Application.objects.all()
        for application in applications:
            application.test_start = startTime
            application.test_end = endTime
            application.save()
    return render(request, 'admin_startTest.html')


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
    
    notifications = Notification.objects.filter(filter_flag='E')
    context = {'notifications': notifications}

    return render(request, 'home.html', context=context)


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

            otp = send_otp(email)
            # otp = 0
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
        # print(request.POST)
        email = request.POST['signin-email']
        password = request.POST['signin-password']

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            next = request.GET.get('next')
            try:
                app = Application.objects.get(student=user)
            except Application.DoesNotExist:
                if next:
                    messages.error(request, "The registration period is over! You are not eligible to give test.")
                    return redirect('Login')
                else:                    
                    return redirect('FillApplication')
            
            if next:
                return redirect(next)
            else:
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
        # print(request.POST)
        # print(request.FILES)
        name = request.POST['fname'] + ' ' + request.POST['mname'] + ' ' + request.POST['lname']
        gender = request.POST.get('gender')
        dob = request.POST['dob']

        
        address = request.POST['line-1'] + ', ' + request.POST.get('line-2') + ', ' + request.POST['city'] + ', ' + request.POST['state'] + ', ' + request.POST['country'] + ', ' + request.POST['postal-code']
        phone = request.POST['phone']
        alt_phone = request.POST['alt_phone']

        father = request.POST['father']
        mother = request.POST['mother']

        ssc = request.POST['ssc']
        ssc_per = request.POST['ssc_per']
        hsc = request.POST['hsc']
        hsc_per = request.POST['hsc_per']
        gujcet = request.POST['gujcet']
        jee = request.POST['jee']

        id_proof = request.FILES.get('id_proof')
        photo = request.FILES.get('photo')
        marks_10 = request.FILES.get('marks_10')
        marks_12 = request.FILES.get('marks_12')
        Application.objects.create(name=name, gender=gender, dob=dob, address=address, phone=phone, alt_phone=alt_phone, father=father, mother=mother, ssc=ssc, ssc_per=ssc_per, hsc=hsc, hsc_per=hsc_per, gujcet=gujcet, jee=jee, student=user, id_proof=id_proof, photo=photo, marks_10=marks_10, marks_12=marks_12)
        return redirect('Dashboard')

    return render(request, 'fill_application.html')


@login_required
def Dashboard(request):
    user = request.user
    app = Application.objects.get(student=user)
    notification = Notification.objects.filter(recipient=app) | Notification.objects.filter(filter_flag='Q') | Notification.objects.filter(filter_flag=app.app_status)
    
    context = {'application' : app, 'notifications' : notification}

    return render(request, 'dashboard.html', context=context)
    

def Logout(request):
    logout(request)
    return redirect('Home')


@login_required
def startTest(request):
    user = request.user
    try:
        user_application = Application.objects.get(student=user)
    except Application.DoesNotExist:
        messages.error(request, "The registration period is over! You are not eligible to give test.")
        return redirect('Login')
    
    try:
        test = Test.objects.get(app_no=user_application)
        if test.test_end is not None:
            messages.success(request, "Your test has already ended! You can now view your result")
            return redirect('Dashboard')
    except Test.DoesNotExist:
        pass
    
    if 'start' in request.GET:
        try:
            test = Test.objects.get(app_no=user_application)
        except Test.DoesNotExist:
            test = Test.objects.create(app_no=user_application, test_start=timezone.now())
        return redirect(reverse('Next_Question', args=(1,)))

    
    return render(request,'instructions.html')


def nextQuestion(request, question_id):
    if request.user.is_authenticated:
        user = request.user
        question = Question.objects.get(qid = question_id)
        qCount = Question.objects.all().count()
        options = [question.op1, question.op2,question.op3,question.op4]
        user_application = Application.objects.get(student=user)
        test = Test.objects.get(app_no=user_application)
        if test.test_end is not None:
            messages.success(request, "Your test has already ended! You can now view your result")
            return redirect('Dashboard')

        time_left = test.test_start + timedelta(minutes=5) - timezone.now()
        hours, remainder = divmod(time_left.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
    else:
        return redirect('StartTest')

    try:
        user_response = ApplicantResponse.objects.get(app_no = user_application, ques = question)
    except ApplicantResponse.DoesNotExist:
        user_response = ApplicantResponse.objects.create(app_no = user_application, ques = question)

    if request.method =='POST':    
        if 'clear' in request.POST:
            user_response.response = ""
            user_response.save()
            return redirect(reverse('Next_Question', args=(question.qid,)))
           
        user_curr_ans = request.POST.get('answer')
        if user_response is not None:
            user_response.response = user_curr_ans
            user_response.save()
        else:
            user_response = ApplicantResponse.objects.create(app_no__user = user, ques__qid = question_id, response = user_curr_ans)

        if 'end' in request.POST:
            return redirect('EndTest')
        
        if 'submit' in request.POST:
            if(question_id==Question.objects.count()):
                messages.success(request,'You have answered all the question. Please review your answers and submit')
                return redirect(reverse('Next_Question', args=(1,)))
            next_question = Question.objects.get(qid=question_id+1)
            options = [next_question.op1, next_question.op2,next_question.op3,next_question.op4]
            return redirect(reverse('Next_Question', args=(next_question.qid,)))
            
    context = {
                'question': question, 
                'options': options,
                'response': user_response.response, 
                'iterateover': range(1,5), 
                'count': qCount,
                'countIterable': range(1,qCount+1),
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,    
            }
    
    return render(request, 'questions.html', context=context)

def EndTest(request):
    if request.user.is_authenticated:
        user = request.user
        user_application = Application.objects.get(student=user)
        responses = ApplicantResponse.objects.filter(app_no=user_application)
        test = Test.objects.get(app_no=user_application)
    else:
        return redirect('StartTest')

    test.test_end=timezone.now()

    total = Question.objects.count()
    score = 0
    for i in responses:
        question = i.ques
        if question.ans==i.response:
            score+=1
    test.score=score
    test.save()

    context = {'score':score, 'total': total}
    return render(request, 'result.html', context=context)

@login_required
def Result(request):
    user = request.user
    app = Application.objects.get(student=user)
    test = Test.objects.get(app_no=app)
    total = Question.objects.count()
    score = test.score
    context = {'total':total, 'score':score}

    return render(request, 'result.html', context=context)


# @login_required
# def Admin(request):
#     return render(request, 'administration.html')

# @login_required
# def ViewApplication(request):
#     apps = Application.objects.filter()
#     context = {'apps': apps}
#     return render(request, 'view_applications.html', context=context)

# @login_required
# def Profile(request, email):
#     user = User.objects.get(username=email)
#     app = Application.objects.get(student=user)
#     notification = Notification.objects.filter(recipient=app) | Notification.objects.filter(filter_flag='Q') | Notification.objects.filter(filter_flag=app.app_status)
    
#     context = {'application' : app, 'notifications' : notification}
#     return render(request, 'profile.html', context=context)