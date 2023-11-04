from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.Home, name='Home'),
    path('login/', views.Login, name='Login'),
    path('logout/', views.Logout, name='Logout'),
    path('dashboard/<str:email>/', views.Dashboard, name='Dashboard'),
]