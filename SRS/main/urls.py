from django.urls import path
from django.contrib import admin
from main import views
from SRS import settings
from django.conf.urls.static import static

app_name = 'main'
urlpatterns = [
    path('', views.Home, name='Home'),
    path('register/', views.Register, name='Register'),
    path('login/', views.Login, name='Login'),
    path('logout/', views.Logout, name='Logout'),
    path('forget/', views.Forget, name='Forget'),
    path('fill_application/', views.FillApplication, name='FillApplication'),
    path('pay_fees/', views.PayFees, name='PayFees'),
    path('dashboard/', views.Dashboard, name='Dashboard'),
    path('test/start', views.startTest, name='StartTest'),
    path('test/<int:question_id>', views.nextQuestion, name='Next_Question'),
    path('test/endtest/', views.EndTest, name='EndTest'),
    path('test/result', views.Result, name='Result'),
    path('process-payment/<int:amount>', views.success, name='success'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)