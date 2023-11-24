from django.urls import path, include
from main import views
from SRS import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home, name='Home'),
    path('login/', views.Login, name='Login'),
    path('register/', views.Register, name='Register'),
    path('logout/', views.Logout, name='Logout'),
    path('forget/', views.Forget, name='Forget'),
    path('fill_application/', views.FillApplication, name='FillApplication'),
    path('dashboard/', views.Dashboard, name='Dashboard'),
    path('test/start', views.startTest, name='StartTest'),
    path('test/<int:qid>', views.nextQuestion, name='Next_Question'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)