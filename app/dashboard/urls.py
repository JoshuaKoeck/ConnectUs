# dashboard/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('english-test/', views.english_test, name='english_test'),
    path('end-test/', views.end_test, name='end_test'),
    path('reset-progress/', views.reset_progress, name='reset_progress'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:pk>/complete/', views.complete_session_template, name='complete_session'),
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('messages/send/', views.send_message, name='send_message'),
    path('mentor/assign/<int:user_id>/', views.mentor_assign_student, name='mentor_assign_student'),
    path('mentor/unassign/<int:user_id>/', views.mentor_unassign_student, name='mentor_unassign_student'),
    path('mentor/set-meeting/<int:user_id>/', views.mentor_set_meeting, name='mentor_set_meeting'),
    path('mentor/manage-sessions/<int:user_id>/', views.mentor_manage_sessions, name='mentor_manage_sessions'),
    path('mentor/messages/', views.mentor_messages, name='mentor_messages'),
    path('mentor/messages/<int:user_id>/', views.mentor_message_thread, name='mentor_message_thread'),
    path('messages/thread/<int:user_id>/', views.message_thread, name='message_thread'),
    path('logout/', logout_then_login, {'login_url': '/dashboard/login/'}, name='logout'),
    path('', views.dashboard, name='dashboard'),
]