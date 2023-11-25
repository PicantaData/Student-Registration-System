from django.db import models
from django.contrib.auth.models import User
import string, secrets
from django.core.exceptions import ValidationError
from django.contrib import messages
import datetime

def gen_app_no():
    characters = string.ascii_letters + string.digits
    application_number = ''.join(secrets.choice(characters) for _ in range(12))
    return application_number

def file_upload(instance,filename):
    return '{0}/{1}'.format(instance.app_no, filename)

class Application(models.Model):
    STATUS = [('P','Pending'), ('A','Accepted'), ('R','Rejected')]
    app_no = models.CharField(max_length=12, null=False, default=gen_app_no)
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    app_status = models.CharField(choices=STATUS, default='P', max_length=1)
    # verified_by = models.OneToOneField(User, on_delete=models.CASCADE)

    GENDER = [('M','Male'), ('F','Female'), ('P','Prefer Not To Say')]
    name = models.CharField(max_length=100, null=False)
    gender = models.CharField(choices=GENDER, max_length=1)
    dob = models.DateField(blank=True, null=False)

    father = models.CharField(max_length=100, null=False)
    mother = models.CharField(max_length=100, null=False)

    phone = models.CharField(max_length=13, blank=False, null=False)
    alt_phone = models.CharField(max_length=13, blank=False, null=False)
    address = models.TextField(blank=True)

    ssc = models.CharField(max_length=100, null=False)
    ssc_per = models.CharField(max_length=10, null=False)
    hsc = models.CharField(max_length=100, null=False)
    hsc_per = models.CharField(max_length=10, null=False)
    gujcet = models.CharField(max_length=10, null=False)
    jee = models.CharField(max_length=100, null=False)
    
    id_proof = models.FileField(upload_to=file_upload,max_length=250, null=False, default=None)
    photo = models.ImageField(upload_to=file_upload, max_length=250, null=False, default=None)
    marks_10 = models.FileField(upload_to=file_upload, max_length=250, null=False, default=None)
    marks_12 = models.FileField(upload_to=file_upload, max_length=250, null=False, default=None)
    
    test_start = models.DateTimeField(null=True)
    test_end = models.DateTimeField(null=True)

    def __str__(self):
        return self.student.username
        
    class Meta:
        ordering = ['app_status']

    
class Notification(models.Model):
    STATUS = [('E', 'Every-Site-Visitor'),
              ('Q','All-Applicants'),
              ('P','Pending'), 
              ('A','Accepted'),
              ('R','Rejected'),
              ('S', 'Specific-Applicant')]
    filter_flag = models.CharField(choices=STATUS, default='S', max_length=1)
    recipient = models.ForeignKey(Application,default=None,null=True, blank=True, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)

    # def save(self, *args, **kwargs):
        # if self.filter_flag == 'S' and self.recipient is None:
        #     # raise ValidationError('Specific Person needs to be selected!')
        #     messages.error(self.request, "Error Message")
        #     pass
        # else:
        #     super(Notification,self).save(*args, **kwargs)

    def __str__(self):
        return self.filter_flag + ': ' + self.content

class Question(models.Model):
    qid = models.IntegerField(unique=True, primary_key=True)
    ques = models.TextField(null=False)
    op1 = models.TextField(null=False)
    op2 = models.TextField(null=False)
    op3 = models.TextField(null=False)
    op4 = models.TextField(null=False)
    OPTIONS = [('1','op1'), ('2','op2'), ('3', 'op3'), ('4','op4')]
    ans = models.TextField(choices=OPTIONS, null=False)

    def __str__(self):
        return str(self.qid) + ": " + self.ques

class ApplicantResponse(models.Model):
    OPTIONS = [('1','op1'), ('2','op2'), ('3', 'op3'), ('4','op4')]
    app_no = models.ForeignKey(Application, on_delete=models.CASCADE)
    ques = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    response = models.CharField(choices=OPTIONS, null=True, blank=True, max_length=1)
    class Meta:
        unique_together = ['app_no', 'ques']

    def __str__(self):
        return str(self.app_no) + ' ' + str(self.ques)
    
class Test(models.Model):
    app_no = models.ForeignKey(Application, on_delete=models.CASCADE)
    test_start = models.DateTimeField(null=True)
    test_end = models.DateTimeField(null=True)
    score = models.IntegerField(default=0, null=False)

    def __str__(self):
        return str(self.app_no)