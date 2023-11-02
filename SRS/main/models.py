# from django.db import models
# from django.contrib.auth.models import User

# class Profile(models.Model):
#     # app_no = models.UUIDField(max_length=)
#     STATUS = [('P','Pending'), ('A','Accepted'), ('R','Rejected')]
#     name = models.CharField(max_length=100, null=False)
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=13, blank=False, null=False)
#     dob = models.DateField(blank=True, null=False)
#     address = models.TextField(blank=True)
#     app_status = models.CharField(choices=STATUS, default='P', max_length=1)

#     def __str__(self):
#         return self.student.username
        
#     class Meta:
#         ordering = ['app_status']


# class Question(models.Model):
#     qid = models.UUIDField(primary_key=True)
#     ques = models.TextField(null=False)
#     op1 = models.TextField(null=False)
#     op2 = models.TextField(null=False)
#     op3 = models.TextField(null=False)
#     op4 = models.TextField(null=False)
#     OPTIONS = [('1','op1'), ('2','op2'), ('3', 'op3'), ('4','op4')]
#     ans = models.TextField(choices=OPTIONS, null=False)

# '''
# class Test(models.Models):
    
# '''


    