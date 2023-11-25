from django.test import TestCase, Client
from django.urls import reverse
from main import models
from unittest.mock import patch, Mock
from django.core.exceptions import ValidationError 
from django.conf import settings
from django.contrib.auth.models import User
from main import validator
from django.contrib.messages import get_messages
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

class Test_view_home(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('Home')


    def test_get_homepage(self):
        response = self.client.get(self.home_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'home.html')


    @patch('main.views.send_mail')
    def test_post_homepage(self,  mocked_send_mail):
        data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'email': 'test@email.com'
        }

        response = self.client.post(self.home_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
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
        self.assertTemplateUsed(response, 'home.html')
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
        self.assertTemplateUsed(response, 'home.html')
        mocked_send_mail.assert_called()



class Test_view_register(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('Register')
    

    def test_get_registerPage(self):
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'register.html')


    def test_user_registration(self):
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword123',
            'confirm-signup-password': 'TestPassword123'
        }
        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'OTP has been sent to your email address!!')
        self.assertTemplateUsed(response, 'otp.html')
    

    def test_validOTP_registration(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = otp
        session['email'] = 'test@example.com'
        session['password'] = 'ValidPassword123'
        session.save()

        response = self.client.post(self.register_url, {'otp':otp})

        self.assertRedirects(response, expected_url=reverse('FillApplication'))
        self.assertTrue(User.objects.filter(username='test@example.com').exists())
        self.assertEqual(User.objects.count(),1)


    def test_InvalidOTP_registration(self):
        otp = 123456 #otp entered by user
        # Data stored in session:-
        session = self.client.session
        session['otp'] = 65431
        session['email'] = 'test@example.com'
        session['password'] = 'ValidPassword123'
        session.save()

        response = self.client.post(self.register_url, {'otp':otp})

        self.assertTemplateUsed(response, 'otp.html')
        self.assertContains(response, 'Invalid OTP!!!')
        self.assertEqual(User.objects.count(),0)


    def test_register_existing_email(self):
        # Create an user
        User.objects.create_user(username='test@example.com', password='Password123')
        # Try creating user with same username
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword123',
            'confirm-signup-password': 'TestPassword123'
        }

        response = self.client.post(self.register_url, data=data)

        self.assertContains(response, 'Email already registered!!!')
        self.assertTemplateUsed(response, 'register.html')

    
    def test_register_mismatched_password(self):
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword123',
            'confirm-signup-password': 'TestPassword223'
        }

        response = self.client.post(self.register_url, data=data)

        self.assertContains(response, 'Password do not match!!!')
        self.assertTemplateUsed(response, 'register.html')


    @patch('main.validator.MinimumLengthValidator.validate')  # Mocking the validator
    def test_register_password_minLength(self, mock_validate):
        mock_validate.side_effect = ValidationError("Your password must contain at least 8 characters")
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'Test',
            'confirm-signup-password': 'Test'
        }
        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Your password must contain at least 8 characters')
        self.assertTemplateUsed(response, 'register.html')
    

    @patch('main.validator.NumberValidator.validate')
    def test_register_password_noNumber(self, mock_validate):
        mock_validate.side_effect = ValidationError("The password must contain at least 1 digit(s), 0-9")
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'TestPassword',
            'confirm-signup-password': 'TestPassword'
        }
        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'The password must contain at least 1 digit(s), 0-9')
        self.assertTemplateUsed(response, 'register.html')

    
    @patch('main.validator.UppercaseValidator.validate')
    def test_register_password_upperCase(self, mock_validate  ):
        mock_validate.side_effect = ValidationError("Your password must contain at least 1 uppercase letter, A-Z.")
        data = {
            'signup-email': 'test@example.com',
            'signup-password': 'testpassword123',
            'confirm-signup-password': 'testpassword123'
        }
        response = self.client.post(self.register_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Your password must contain at least 1 uppercase letter, A-Z.')
        self.assertTemplateUsed(response, 'register.html')



class Test_view_login(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('Login')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')


    def test_get_loginPage(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'login.html')

    
    def test_login_successful(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'TestPassword123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302) # Redirected
    

    def test_login_successful_redirects_fillApplication(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'TestPassword123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('FillApplication'))


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
            'signin-password': 'TestPassword123',
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('Dashboard'))


    def test_login_invalid_username(self):
        data = {
            'signin-email': 'testuuer@gmail.com',
            'signin-password': 'TestPassword123',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'login.html')
    

    def test_login_invalid_password(self):
        data = {
            'signin-email': 'testuser@gmail.com',
            'signin-password': 'Testassword123',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'login.html')
    

    def test_login_empty_data(self):
        data = {
            'signin-email': '',
            'signin-password': '',
        }

        response = self.client.post(self.login_url, data)

        self.assertContains(response, 'Incorrect Email or Password!!!')
        self.assertTemplateUsed(response, 'login.html')



class Test_view_forget(TestCase):

    def setUp(self):
        self.client = Client()
        self.forget_url = reverse('Forget')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')


    def test_get_forgetPage(self):
        response = self.client.get(self.forget_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'forget.html')

    
    def test_forget_existingEmail(self):
        data = {
            'forget-email' : 'testuser@gmail.com'
        }

        response = self.client.post(self.forget_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'OTP has been sent to your email address!!')
        self.assertTemplateUsed(response, 'otp.html')

    
    def test_forget_NonExistingEmail(self):
        data = {
            'forget-email' : 'testuuer@gmail.com'
        }

        response = self.client.post(self.forget_url, data=data)

        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Email Does Not Exist')
        self.assertTemplateUsed(response, 'forget.html')


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
        self.assertTemplateUsed(response, 'change_password.html')

    
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
        self.assertTemplateUsed(response, 'otp.html')

    
    def test_forget_password_change_successfull(self):
        # Data stored in session:-
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'PasswordNew123',
            'confirm-change-password': 'PasswordNew123'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Your password has been successfully changed !!!')
        self.assertRedirects(response, reverse('Login'))


    def test_forget_password_Mismatch(self):
        # Data stored in session:-
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'PasswordNew123',
            'confirm-change-password': 'PassworNew123'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Password do not match!!!')
        self.assertTemplateUsed(response, 'change_password.html')

    
    @patch('main.validator.MinimumLengthValidator.validate')  
    def test_forget_password_minLength(self, mock_validate):
        mock_validate.side_effect = ValidationError("Your password must contain at least 8 characters")
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'Passwo',
            'confirm-change-password': 'Passwo'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Your password must contain at least 8 characters')
        self.assertTemplateUsed(response, 'change_password.html')
    

    @patch('main.validator.NumberValidator.validate')
    def test_forget_password_noNumber(self, mock_validate):
        mock_validate.side_effect = ValidationError("The password must contain at least 1 digit(s), 0-9")
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'PasswordNew',
            'confirm-change-password': 'PasswordNew'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'The password must contain at least 1 digit(s), 0-9')
        self.assertTemplateUsed(response, 'change_password.html')

    
    @patch('main.validator.UppercaseValidator.validate')
    def test_forget_password_upperCase(self, mock_validate  ):
        mock_validate.side_effect = ValidationError("Your password must contain at least 1 uppercase letter, A-Z.")
        session = self.client.session
        session['email'] = 'testuser@gmail.com'
        session.save()

        data = {
            'change-password': 'passwordnew123',
            'confirm-change-password': 'passwordnew123'
        }
        response = self.client.post(self.forget_url, data=data, follow=True)

        self.assertContains(response, 'Your password must contain at least 1 uppercase letter, A-Z.')
        self.assertTemplateUsed(response, 'change_password.html')

    

class Test_view_FillApplication(TestCase):

    def setUp(self):
        self.client = Client()
        self.application_url = reverse('FillApplication')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')


    def test_get_applicationPage_unauthorized(self):
        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/fill_application/')


    def test_get_applicationPage_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.application_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'fill_application.html')

    
    def test_application_creation(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword123')

        # Prepare file data
        id_file = SimpleUploadedFile("Aadhar.pdf", b"file_content", content_type="application/pdf")
        photo_file = SimpleUploadedFile("photo.jpg", b"file_content", content_type="image/jpeg")
        marks_10_file = SimpleUploadedFile("10marks.pdf", b"file_content", content_type="application/pdf")
        marks_12_file = SimpleUploadedFile("12marks.pdf", b"file_content", content_type="application/pdf")

        data = {
            'fname': 'Test',
            'mname': '-',
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
        self.assertRedirects(response, reverse('Dashboard'))



class Test_view_Dashboard(TestCase):

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('Dashboard')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')
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


    def test_get_Dashboard_unauthorized(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, '/login/?next=/dashboard/')


    def test_get_Dashboard_authorized(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'dashboard.html')



class Test_view_startTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.startTest_url = reverse('StartTest')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')
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
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.startTest_url)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'instructions.html')


    def test_startTest_afterInstructions(self): # Going from instructions to 1st question
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.startTest_url + '?start=')
        
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('Next_Question', args=(1,)))


    def test_startTest_registration_period_over(self):
        # Delete the application to simulate the registration period being over
        self.application.delete()
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('Login'))
        self.assertContains(response, 'The registration period is over! You are not eligible to give test.')
        

    def test_startTest_test_already_ended(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        past_time1 = timezone.now() - timedelta(hours=2)
        past_time2 = timezone.now() - timedelta(hours=1)  # Assuming test ended 1 hour ago
        self.test = models.Test.objects.create(
            app_no = self.application,
            test_start = past_time1,
            test_end = past_time2,
            score = 20
        )

        response = self.client.get(self.startTest_url, follow=True)

        self.assertRedirects(response, reverse('Dashboard'))
        self.assertContains(response, 'Your test has already ended! You can now view your result')



class Test_view_logout(TestCase):

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('Logout')
        self.user = User.objects.create_user(username='testuser@gmail.com', password='TestPassword123')

    
    def test_logout(self):
        self.client.login(username='testuser@gmail.com', password='TestPassword123')
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('Home'))

    
    def test_logout_already_loggedOut(self):
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('Home'))

