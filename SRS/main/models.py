from django.db import models
from django.contrib.auth.models import User
import string, secrets
from django.core.exceptions import ValidationError
from django.contrib import messages

def gen_app_no():
    characters = string.ascii_letters + string.digits
    application_number = ''.join(secrets.choice(characters) for _ in range(12))
    return application_number

class Application(models.Model):
    STATUS = [('P','Pending'), ('A','Accepted'), ('R','Rejected')]
    app_no = models.CharField(max_length=12, null=False, default=gen_app_no)
    name = models.CharField(max_length=100, null=False)
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=False, null=False)
    dob = models.DateField(blank=True, null=False)
    address = models.TextField(blank=True)
    app_status = models.CharField(choices=STATUS, default='P', max_length=1)
    photo = models.ImageField(upload_to='photo/', max_length=250, null=False, default=None)
    marks_10 = models.FileField(upload_to='10marks/', max_length=250, null=False, default=None)
    marks_12 = models.FileField(upload_to='12marks/', max_length=250, null=False, default=None)
    # result = models.JSONField(null=True)

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
    qid = models.UUIDField(primary_key=True)
    ques = models.TextField(null=False)
    op1 = models.TextField(null=False)
    op2 = models.TextField(null=False)
    op3 = models.TextField(null=False)
    op4 = models.TextField(null=False)
    OPTIONS = [('1','op1'), ('2','op2'), ('3', 'op3'), ('4','op4')]
    ans = models.TextField(choices=OPTIONS, null=False)

class ApplicantResponse(models.Model):
    OPTIONS = [('1','op1'), ('2','op2'), ('3', 'op3'), ('4','op4')]
    app_no = models.ForeignKey(Application, on_delete=models.CASCADE)
    ques = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    response = models.CharField(choices=OPTIONS, null=True, max_length=1)
    class Meta:
        unique_together = ['app_no', 'ques']

    def __str__(self):
        return str(self.app_no) + ' ' + str(self.ques)