from django.urls import path, include
from main import views
from SRS import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home, name='Home'),
    path('login/', views.Login, name='Login'),
    path('logout/', views.Logout, name='Logout'),
    path('fill_application/', views.FillApplication, name='FillApplication'),
    path('dashboard/', views.Dashboard, name='Dashboard'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)