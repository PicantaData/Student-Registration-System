from django.contrib import admin, messages
from .models import *

# Register your models here.
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dob', 'app_status')
    search_fields = ['name', 'dob', 'app_no', 'app_status', 'phone']
    ordering = ['name', 'app_status']

class NotificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if obj.filter_flag == 'S' and obj.recipient is None:
        # Example of raising an error message
            self.message_user(request, "Please select application for specific notification.", level=messages.ERROR)
        else:
        # Call the original save_model method to save the model
            super().save_model(request, obj, form, change)  

admin.site.register(Application)
admin.site.register(Notification)
admin.site.register(Question)
admin.site.register(ApplicantResponse)
