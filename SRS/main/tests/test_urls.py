from django.test import SimpleTestCase, Client
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from main import views

class TestUrls(SimpleTestCase):

    def test_home_url(self):
        url = reverse('Home')
        self.assertEqual(url,'/')   # Check if the URL resolves correctly

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Home)    # Check if the view is associated correctly


    def test_login_url(self):
        url = reverse('Login')
        self.assertEqual(url, '/login/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Login)  


    def test_register_url(self):
        url = reverse('Register')
        self.assertEqual(url, '/register/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Register)  


    def test_logout_url(self):
        url = reverse('Logout')
        self.assertEqual(url, '/logout/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Logout)  


    def test_fill_application_url(self):
        url = reverse('FillApplication')
        self.assertEqual(url, '/fill_application/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.FillApplication)  


    def test_dashboard_url(self):
        url = reverse('Dashboard')
        self.assertEqual(url, '/dashboard/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Dashboard)  


    def test_forget_url(self):
        url = reverse('Forget')
        self.assertEqual(url, '/forget/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Forget) 


    def test_startTest_url(self):
        url = reverse('StartTest')
        self.assertEqual(url, '/test/start')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.startTest)
    

    def test_nextQuestion_url(self):
        url = reverse('Next_Question', args=[1])
        self.assertEqual(url, '/test/1')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.nextQuestion)
    

    def test_endTest_url(self):
        url = reverse('EndTest')
        self.assertEqual(url, '/test/endtest/')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.EndTest)  


    def test_Result_url(self):
        url = reverse('Result')
        self.assertEqual(url, '/test/result')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.Result)  


    def test_populateTest_url(self):
        url = reverse('populateTest')
        self.assertEqual(url, '/staff/define-test-window')  

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.populateTest)  



class Test_Unauthenticated_URLs(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated_access(self):
        unauthenticated_urls = ['/dashboard/', '/fill_application/', '/test/start']
        for url in unauthenticated_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirects to login when not authenticated
            if url == '/dashboard/':
                self.assertRedirects(response, '/login/?next=/dashboard/')
            elif url == '/fill_application/':
                self.assertRedirects(response, '/login/?next=/fill_application/')
            elif url == '/test/start':
                self.assertRedirects(response, '/login/?next=/test/start')



class Test_NonExistent_Urls(SimpleTestCase):

    def test_nonexistent_urls(self):
        nonexistent_urls = ['/nonexistent/', '/random_url/', '/invalid/url/']
        
        for url in nonexistent_urls:
            # Test if the URL resolves to a 404 view (Not found)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
