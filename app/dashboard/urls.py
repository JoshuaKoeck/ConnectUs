# dashboard/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('', views.dashboard, name='dashboard'),
]