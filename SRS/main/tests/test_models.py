from django.test import TestCase
from main import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from django.utils import timezone

class Test_ApplicationModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='Test@1234')
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

    def test_applicantion_creation(self):
        self.assertEqual(self.application.name, 'Test Applicant')
        self.assertEqual(models.Application.objects.count(), 1) 

    def test_delete_applicant(self):
        self.application.delete()
        self.assertFalse(models.Application.objects.filter(name='Test Applicant').exists())


class Test_NotoficationModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='Test@1234')
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
        self.notification = models.Notification.objects.create(
            filter_flag='S',
            recipient=self.application,
            content='Test Notification'
        )

    def test_notification_creation(self):
        self.assertEqual(models.Notification.objects.count(),1)
        self.assertEqual(self.notification.filter_flag, 'S')
        self.assertEqual(self.notification.recipient.name, 'Test Applicant')

     
class Test_QuestionModel(TestCase):
    def setUp(self):
        self.question = models.Question.objects.create(
            qid=1,
            ques='Test Question',
            op1='Option 1',
            op2='Option 2',
            op3='Option 3',
            op4='Option 4',
            ans='1'
        )

    def test_question_creation(self):
        self.assertEqual(models.Question.objects.count(),1)
        self.assertTrue(models.Question.objects.filter(qid=1).exists())



class Test_ApplicantResponseModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='Test@1234')
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
        self.question = models.Question.objects.create(
            qid=3,
            ques='Test Question3',
            op1='Option 1',
            op2='Option 2',
            op3='Option 3',
            op4='Option 4',
            ans='1'
        )

    def test_response_creation(self):
        self.applicant_response = models.ApplicantResponse.objects.create(
            app_no=self.application,
            ques=self.question,
            response='1'
        )
        self.assertEqual(models.ApplicantResponse.objects.count(), 1)
        self.assertEqual(self.applicant_response.response,'1')


class Test_TestModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='Test@1234')
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

    def test_test_creation(self):
        test = models.Test.objects.create(
            app_no=self.application,
            score=30,
        )

        self.assertEqual(models.Test.objects.count(), 1)
        self.assertEqual(test.score,30)


class Test_DeadlineModel(TestCase):
    
    def setUp(self):
        self.ApplicationStart = models.Deadline.objects.create(name='Applicaton Start', time=timezone.now() + timezone.timedelta(days=1))
        self.ApplicationEnd = models.Deadline.objects.create(name='Application End', time=timezone.now() + timezone.timedelta(days=2))
        self.TestStart = models.Deadline.objects.create(name='Test Start', time=timezone.now() + timezone.timedelta(days=3))
        self.TestEnd = models.Deadline.objects.create(name='Test End', time=timezone.now() + timezone.timedelta(days=4))
        
    def test_deadline_creation(self):
        self.assertIsNotNone(self.ApplicationStart.time)
        self.assertIsNotNone(self.ApplicationEnd.time)
        self.assertIsNotNone(self.TestStart.time)
        self.assertIsNotNone(self.TestEnd.time)