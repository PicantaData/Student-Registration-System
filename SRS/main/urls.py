from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.landing, name='Home'),
    path('login/', views.Login, name='Login'),
    path('signup/', views.Signup, name='Signup'),
    path('verifyEmail/', views.VerifyOtp, name='verifyEmail'),
    path('logout/', views.Logout, name='Logout'),

]