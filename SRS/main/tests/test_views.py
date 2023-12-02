from django.test import TestCase, Client
from django.urls import reverse
from main import models
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError 
from django.conf import settings
from django.contrib.auth.models import User
from main import validators
from django.contrib.messages import get_messages
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

class Test_view_home(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('main:Home')


    def test_get_homepage(self):
        response = self.client.get(self.home_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/home.html')


    @patch('main.views.send_mail')
    def test_post_homepage(self,  mocked_send_mail):
        data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'email': 'test@email.com'
        }

        response = self.client.post(self.home_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        self.assertEqual(mocked_send_mail.call_count, 1)
        mocked_send_mail.assert_called_once_with(
            'Test Subject', 'Test Message', 'test@email.com', [settings.EMAIL_HOST_USER]
        )


    @patch('main.views.send_mail')
    def test_post_emptyData_homepage(self,  mocked_send_mail):
        data = {
            'subject': '',
            'message': '',
            'email': ''
        }

        response = self.client.post(self.home_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        mocked_send_mail.assert_called()
    

    @patch('main.views.send_mail')
    def test_post_invalidEmail_homepage(self,  mocked_send_mail):
        data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'email': 'test@email'
        }

        response = self.client.post(self.home_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        mocked_send_mail.assert_called()



class Test_view_register(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('main:Register')
    

    def test_get_registerPage(self):
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/register.html')


    def test_user_registration(self):
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword@123',
            'confirm-signup-password': 'TestPassword@123'
        }
        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'OTP has been sent to your email address!!')
        self.assertTemplateUsed(response, 'main/otp.html')
    

    def test_validOTP_registration(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = otp
        session['email'] = 'test@example.com'
        session['password'] = 'TestPassword@123'
        session.save()

        response = self.client.post(self.register_url, {'otp':otp})

        self.assertRedirects(response, expected_url=reverse('main:FillApplication'))
        self.assertTrue(User.objects.filter(username='test@example.com').exists())
        self.assertEqual(User.objects.count(),1)


    def test_InvalidOTP_registration(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = 65431
        session['email'] = 'test@example.com'
        session['password'] = 'TestPassword@123'
        session.save()

        response = self.client.post(self.register_url, {'otp':otp})

        self.assertTemplateUsed(response, 'main/otp.html')
        self.assertContains(response, 'Invalid OTP!!!')
        self.assertEqual(User.objects.count(),0)


    def test_register_existing_email(self):
        # Create an user
        User.objects.create_user(username='test@example.com', password='Password123')
        # Try creating user with same username
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword@123',
            'confirm-signup-password': 'TestPassword@123'
        }

        response = self.client.post(self.register_url, data=data)

        self.assertContains(response, 'Email already registered!!!')
        self.assertTemplateUsed(response, 'main/register.html')

    
    def test_register_mismatched_password(self):
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword@123',
            'confirm-signup-password': 'TestPassword@122'
        }

        response = self.client.post(self.register_url, data=data)

        self.assertContains(response, 'Password do not match!!!')
        self.assertTemplateUsed(response, 'main/register.html')


    def test_register_weak_password(self):
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'Test',
            'confirm-signup-password': 'Test'
        }

        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        messages = list(response.context['messages'])
        self.assertTrue(messages)  # Check if messages are present
        error_messages = [str(msg) for msg in messages if msg.tags == 'error']
        # print("Error messages:")
        # for error_msg in error_messages:
        #     print(error_msg)
        self.assertTrue(error_messages)
        self.assertTemplateUsed(response, 'main/register.html')


    def test_register_registration_period_over(self):
        models.Deadline.objects.create(name='app_start', time=timezone.now() - timezone.timedelta(days=2))
        models.Deadline.objects.create(name='app_end', time=timezone.now() - timezone.timedelta(days=1))

        response = self.client.get(self.register_url, follow=True)

        self.assertRedirects(response, reverse('main:Login'))
        self.assertContains(response, 'Registration Period is closed!!!')
    


class Test_view_login(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('main:Login')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')


    def test_get_loginPage(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/login.html')

    
    def test_login_successful(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'TestPassword@123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302) # Redirected
    

    def test_login_successful_redirects_fillApplication(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'TestPassword@123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:FillApplication'))


    def test_login_successful_redirects_dashboard(self):
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
        )
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'TestPassword@123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:Dashboard'))


    def test_login_invalid_username(self):
        data = {
            'signin-email': 'testuuer@gmail.com',
            'signin-password': 'TestPassword@123',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'main/login.html')
    

    def test_login_invalid_password(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'Testassword@123',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'main/login.html')
    

    def test_login_empty_data(self):
        data = {
            'signin-email': '',
            'signin-password': '',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'main/login.html')



class Test_view_forget(TestCase):

    def setUp(self):
        self.client = Client()
        self.forget_url = reverse('main:Forget')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')


    def test_get_forgetPage(self):
        response = self.client.get(self.forget_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/forget.html')

    
    def test_forget_existingEmail(self):
        data = {
            'forget-email' : 'testuser@gmail.com'
        }

        response = self.client.post(self.forget_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'OTP has been sent to your email address!!')
        self.assertTemplateUsed(response, 'main/otp.html')

    
    def test_forget_NonExistingEmail(self):
        data = {
            'forget-email' : 'testuuer@gmail.com'
        }

        response = self.client.post(self.forget_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Email Does Not Exist')
        self.assertTemplateUsed(response, 'main/forget.html')


    def test_forget_valid_otp(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = otp
        session['email'] = 'testuser@gmail.com'
        session.save()

        response = self.client.post(self.forget_url, {'otp':otp})

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'OTP matched successfully!!!')
        self.assertTemplateUsed(response, 'main/change_password.html')

    
    def test_forget_Invalid_otp(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = 654321
        session['email'] = 'testuser@gmail.com'
        session.save()

        response = self.client.post(self.forget_url, {'otp':otp})

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Invalid OTP!!!')
        self.assertTemplateUsed(response, 'main/otp.html')

    
    def test_forget_password_change_successfull(self):
        # Data stored in session:-
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'PasswordNew@123',
            'confirm-change-password': 'PasswordNew@123'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Your password has been successfully changed !!!')
        self.assertRedirects(response, reverse('main:Login'))


    def test_forget_password_Mismatch(self):
        # Data stored in session:-
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'PasswordNew@123',
            'confirm-change-password': 'PassworNew@123'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Password do not match!!!')
        self.assertTemplateUsed(response, 'main/change_password.html')

    
    def test_forget_password_weakPassword(self):
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'Passwo',
            'confirm-change-password': 'Passwo'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        messages = list(response.context['messages'])
        self.assertTrue(messages)  # Check if messages are present
        error_messages = [str(msg) for msg in messages if msg.tags == 'error']
        # print("Error messages:")
        # for error_msg in error_messages:
        #     print(error_msg)
        self.assertTrue(error_messages)
        self.assertTemplateUsed(response, 'main/change_password.html')

    

class Test_view_FillApplication(TestCase):

    def setUp(self):
        self.client = Client()
        self.application_url = reverse('main:FillApplication')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')


    def test_get_applicationPage_unauthorized(self):
        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/fill_application/')


    def test_get_applicationPage_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/fill_application.html')

    
    def test_application_creation(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')

        # Prepare file data
        id_file = SimpleUploadedFile("Aadhar.pdf", b"file_content", content_type="application/pdf")
        photo_file = SimpleUploadedFile("photo.jpg", b"file_content", content_type="image/jpeg")
        marks_10_file = SimpleUploadedFile("10marks.pdf", b"file_content", content_type="application/pdf")
        marks_12_file = SimpleUploadedFile("12marks.pdf", b"file_content", content_type="application/pdf")

        data = {
            'fname': 'Test',
            'mname': 'A',
            'lname': 'Applicant',
            'gender':'M',
            'dob':date(2000, 1, 1),
            'father':'Test Person1',
            'mother':'Test Person2',
            'phone':'9988776655',
            'alt_phone':'9876543210',
            'line-1':'Address Line1',
            'line-2':'Address Line2',
            'city':'TestCity',
            'state':'TestState',
            'country':'TestCountry',
            'postal-code':'354765',
            'app_status':'P',
            'ssc':'School1',
            'ssc_per':'90',
            'hsc':'School2',
            'hsc_per':'85',
            'gujcet':'GujCET Details',
            'jee':'JEE Details',
            'id_proof':id_file,
            'photo':photo_file,
            'marks_10':marks_10_file, 
            'marks_12':marks_12_file,
        }

        response = self.client.post(self.application_url, data=data)

        self.assertEqual(models.Application.objects.count(), 1) 
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:PayFees'))


    def test_application_filled_withPayment(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
        )

        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:Dashboard'))

    
    def test_application_filled_withoutPayment(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
        )

        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main:PayFees'))



class Test_view_PayFees(TestCase):

    def setUp(self):
        self.client = Client()
        self.payFees_url = reverse('main:PayFees')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
        )


    def test_get_payFeesPage_unauthorized(self):
        response = self.client.get(self.payFees_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/pay_fees/')


    def test_get_payFeesPage_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.payFees_url)

        self.assertEqual(response.status_code,302)
        expected_razorpay_url = "https://razorpay.com/payment-button/pl_MgAaDNUDkk2msX"
        self.assertIn(expected_razorpay_url, response.url)

    
    def test_payFees_fees_already_paid(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        applicant = models.Application.objects.get(student=self.user)
        applicant.order_id = 'dfkjvvjl32'
        applicant.payment_id = '12yuvvvy2'
        applicant.payment_receipt = 'payment.pdf'
        applicant.save()

        response = self.client.get(self.payFees_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse('main:Dashboard'))



class Test_view_Dashboard(TestCase):

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('main:Dashboard')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
            payment_receipt = 'payment.pdf'
        )


    def test_get_Dashboard_unauthorized(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/dashboard/')


    def test_get_Dashboard_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/dashboard.html')

    
    def test_get_Dashboard_when_application_notFilled(self):
        self.application.delete()
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('main:FillApplication'))



class Test_view_startTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.startTest_url = reverse('main:StartTest')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='A',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
            payment_receipt = 'payment.pdf',
        )
        self.question1 = models.Question.objects.create(
            qid=1,
            ques='What is 1 + 1?', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='2'
        )
        self.question2 = models.Question.objects.create(
            qid=2,
            ques='What is the capital of France?', 
            op1='Paris', op2='Rome', op3='Berlin', op4='Madrid', 
            ans='Paris'
        )


    def test_get_startTest_unauthorized(self):
        response = self.client.get(self.startTest_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/test/start')


    def test_get_startTest_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() - timezone.timedelta(days=1))
        models.Deadline.objects.create(name='test_end', time=timezone.now() + timezone.timedelta(days=1))

        response = self.client.get(self.startTest_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/instructions.html')


    def test_startTest_afterInstructions(self): # Going from instructions to 1st question
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() - timezone.timedelta(days=1))
        models.Deadline.objects.create(name='test_end', time=timezone.now() + timezone.timedelta(days=1))

        response = self.client.get(self.startTest_url + '?start=')
        
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('main:Next_Question', args=(1,)))


    def test_startTest_registration_period_over(self):
        # Delete the application to simulate the registration period being over
        self.application.delete()
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() - timezone.timedelta(days=1))
        models.Deadline.objects.create(name='test_end', time=timezone.now() + timezone.timedelta(days=1))

        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('main:Login'))
        self.assertContains(response, 'The registration period is over! You are not eligible to give test.')
        

    def test_startTest_test_already_completed(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() - timezone.timedelta(days=1))
        models.Deadline.objects.create(name='test_end', time=timezone.now() + timezone.timedelta(days=1))
        past_time1 = timezone.now() - timedelta(hours=2)
        past_time2 = timezone.now() - timedelta(hours=1)  # Assuming test ended 1 hour ago
        self.test = models.Test.objects.create(
            app_no = self.application,
            test_start = past_time1,
            test_end = past_time2,
            score = 20
        )

        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('main:Dashboard'))
        self.assertContains(response, 'Your test has already ended! You can now view your result')


    def test_startTest_before_testWindow(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() + timezone.timedelta(days=1))
        models.Deadline.objects.create(name='test_end', time=timezone.now() + timezone.timedelta(days=2))

        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('main:Dashboard'))
        self.assertContains(response, 'The test will start from')


    def test_startTest_testWindow_ended(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        models.Deadline.objects.create(name='test_start', time=timezone.now() - timezone.timedelta(days=2))
        models.Deadline.objects.create(name='test_end', time=timezone.now() - timezone.timedelta(days=1))

        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('main:Dashboard'))
        self.assertContains(response, 'The test window has ended!')


    def test_startTest_test_not_available(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')

        response = self.client.get(self.startTest_url,follow=True)

        self.assertRedirects(response, reverse('main:Home'))
        # self.assertContains(response, 'Test is not available. Please contact Admin.')


    def test_startTest_application_notApproved(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        applicant = models.Application.objects.get(student=self.user)
        applicant.app_status = 'P'
        applicant.save()
        
        response = self.client.get(self.startTest_url)

        self.assertEqual(models.Test.objects.count(),0)


    def test_startTest_fees_unpaid(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        applicant = models.Application.objects.get(student=self.user)
        applicant.payment_id = None
        applicant.save()
        
        response = self.client.get(self.startTest_url)

        self.assertEqual(models.Test.objects.count(),0)




class Test_view_nextQuestion(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='A',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
            payment_receipt = 'payment.pdf',
        )
        self.question1 = models.Question.objects.create(
            qid=1,
            ques='Ques1', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='2'
        )
        self.question2 = models.Question.objects.create(
            qid=2,
            ques='Ques2', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='1'
        )
        self.question3 = models.Question.objects.create(
            qid=3,
            ques='Ques3', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='4'
        )
        self.test = models.Test.objects.create(app_no=self.application, test_start=timezone.now())
    

    def test_get_nextQuestion_unauthorized(self):
        response = self.client.get(reverse('main:Next_Question', args=(self.question1.qid,)))

        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url, reverse('main:StartTest'))


    def test_get_nextQuestion_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(reverse('main:Next_Question', args=(self.question1.qid,)))

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'main/questions.html')
        self.assertTrue('question' in response.context)
        self.assertTrue('options' in response.context)
        self.assertEqual(models.ApplicantResponse.objects.count(), 1)

    
    def test_nextQuestion_invalid_question_id(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        invalid_question_id = 490

        response = self.client.get(reverse('main:Next_Question', args=(invalid_question_id,)))

        self.assertEqual(response.url, reverse('main:StartTest'))

    
    def test_nextQuestion_test_already_ended(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        self.test.delete()
        past_time1 = timezone.now() - timedelta(hours=2)
        past_time2 = timezone.now() - timedelta(hours=1)  # Assuming test ended 1 hour ago
        self.test = models.Test.objects.create(
            app_no = self.application,
            test_start = past_time1,
            test_end = past_time2,
        )

        response = self.client.get(reverse('main:Next_Question', args=(self.question1.qid,)), follow=True)

        self.assertRedirects(response, reverse('main:Dashboard'))
        self.assertContains(response, 'Your test has already ended! You can now view your result')

    
    def test_nextQuestion_clearResponse(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.post(reverse('main:Next_Question', args=(self.question2.qid,)), {'clear':''})

        user_response = models.ApplicantResponse.objects.get(app_no=self.application,ques=self.question2)
        self.assertEqual(user_response.response, '')
        self.assertEqual(response.status_code, 302)

    
    def test_nextQuestion_noResponse(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.post(reverse('main:Next_Question', args=(self.question1.qid,)), {'submit':''})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:Next_Question', args=(self.question2.qid,)))

    
    def test_nextQuestion_withResponse(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.post(reverse('main:Next_Question', args=(self.question1.qid,)), {'answer':'2','submit':''})

        user_response = models.ApplicantResponse.objects.get(app_no=self.application,ques=self.question1)
        self.assertEqual(user_response.response, '2')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:Next_Question', args=(self.question2.qid,)))


    def test_nextQuestion_lastQuestion(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.post(reverse('main:Next_Question', args=(self.question3.qid,)), {'answer':'3','submit':''}, follow=True)

        self.assertRedirects(response, reverse('main:Next_Question', args=(self.question1.qid,)))
        self.assertContains(response, 'You have reached the end of test. Please review your answers and submit')

    
    def test_nextQuestion_EndingTest(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.post(reverse('main:Next_Question', args=(self.question3.qid,)), {'end':''})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:EndTest'))


    def test_nextQuestion_before_accepting_termsAndConditions(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        self.test.delete()

        response = self.client.get(reverse('main:Next_Question', args=(self.question1.qid,)))

        self.assertEqual(response.url, reverse('main:StartTest'))



class Test_view_EndTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
            payment_receipt = 'payment.pdf',
        )
        self.question1 = models.Question.objects.create(
            qid=1,
            ques='Ques1', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='2'
        )
        self.question2 = models.Question.objects.create(
            qid=2,
            ques='Ques2', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='1'
        )
        self.question3 = models.Question.objects.create(
            qid=3,
            ques='Ques3', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='4'
        )
        self.question4 = models.Question.objects.create(
            qid=4,
            ques='Ques4', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='1'
        )
        self.test = models.Test.objects.create(app_no=self.application, test_start=timezone.now())
        self.response1 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question1, response='2')
        self.response2 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question2, response='3')
        self.response3 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question3, response='4')
        self.response4 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question4, response='')
        self.EndTest_url = reverse('main:EndTest')
    

    def test_get_EndTest_unauthorized(self):
        response = self.client.get(self.EndTest_url)

        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url, reverse('main:StartTest'))


    def test_get_EndTest_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.EndTest_url)

        user_application = models.Application.objects.get(student=self.user)
        responses = models.ApplicantResponse.objects.filter(app_no=user_application)
        total = models.Question.objects.count()*4
        correct = 0
        incorrect = 0
        for i in responses:
            if i.response == '':
                continue
            question = i.ques
            if question.ans==i.response:
                correct+=1
            else:
                incorrect+=1

        unanswered = models.Question.objects.count()-incorrect-correct
        score = correct*4-incorrect

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/result.html')
        self.assertEqual(response.context['score'], score)



class Test_view_Result(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')
        self.application = models.Application.objects.create(
            student=self.user,
            name='Test Applicant',
            gender='M',
            dob=date(2000, 1, 1),
            father='Test Person1',
            mother='Test Person2',
            phone='9988776655',
            alt_phone='9876543210',
            address='Test Address',
            app_status='P',
            ssc='School1',
            ssc_per='90',
            hsc='School2',
            hsc_per='85',
            gujcet='GujCET Details',
            jee='JEE Details',
            id_proof='Aadhar.pdf',
            photo = 'photo.jpg',
            marks_10='test_10.pdf', 
            marks_12='test_12.pdf',
            order_id = 'sdyt7867t897u4c3c',
            payment_id = 'value',
            payment_receipt = 'payment.pdf',
        )
        self.question1 = models.Question.objects.create(
            qid=1,
            ques='Ques1', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='2'
        )
        self.question2 = models.Question.objects.create(
            qid=2,
            ques='Ques2', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='1'
        )
        self.question3 = models.Question.objects.create(
            qid=3,
            ques='Ques3', 
            op1='1', op2='2', op3='3', op4='4', 
            ans='4'
        )
        self.response1 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question1, response='2')
        self.response2 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question2, response='3')
        self.response3 = models.ApplicantResponse.objects.create(app_no=self.application, ques=self.question3, response='4')
        self.test = models.Test.objects.create(app_no=self.application, test_start='2023-11-25T12:00:00Z', test_end='2023-11-25T12:05:00Z')
        self.Result_url = reverse('main:Result')


    def test_get_Result_unauthorized(self):
        response = self.client.get(self.Result_url)

        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url, '/login/?next=/test/result')


    def test_get_Result_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.Result_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/result.html')
        self.assertEqual(response.context['total'], 12)
        self.assertEqual(response.context['score'], 7)



class Test_view_logout(TestCase):

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('main:Logout')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword@123')

    
    def test_logout(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword@123')
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('main:Home'))

    
    def test_logout_already_loggedOut(self):
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('main:Home'))

