from django.urls import path
from .views import register, user_login, user_logout, dashboard, add_task,delete_task,profile, settings_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('settings/', settings_view, name='settings'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
path('add_task/', views.add_task, name='add_task'),
    path('delete-task/<str:task_title>/', views.delete_task, name='delete_task'),
    path('calendar/', views.calendar, name='calendar'),  
    path('motivational-quotes/', views.motivational_quotes, name='motivational_quotes'),
     # Password reset views (Django built-in)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

     path('profile/', views.profile_view, name='profile'), 
    path('update-profile/', views.update_profile, name='update_profile'),
    path('save-reminders/', views.save_reminder, name='save_reminders'),
    path('get-reminders/', views.get_reminders, name='get_reminders'),
]
