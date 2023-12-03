from django.contrib import admin, messages
from .models import *

# Register your models here.
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dob', 'app_status')
    search_fields = ['name', 'dob', 'app_no', 'app_status', 'phone']
    ordering = ['name', 'app_status']

class NotificationAdmin(admin.ModelAdmin):
    list_filter = ['filter_flag']
    list_display = ['filter_flag', 'content']
    def save_model(self, request, obj, form, change):
        if obj.filter_flag == 'S' and obj.recipient is None:
        # Example of raising an error message
            self.message_user(request, "Please select application for specific notification.", level=messages.ERROR)
        else:
        # Call the original save_model method to save the model
            super().save_model(request, obj, form, change)

class DeadlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'time')  

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['ques', 'qid']
    list_display = ['qid', 'ques', 'ans']

class TestAdmin(admin.ModelAdmin):
    search_fields = ['app_no', 'score']
    ordering = ['score']

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ApplicantResponse)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Deadline, DeadlineAdmin)
