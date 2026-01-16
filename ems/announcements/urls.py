from django.urls import path
from .views import create_announcement, employee_announcements

urlpatterns = [
    path('dashboard/announcements/', create_announcement, name='create_announcement'),
    path('employee/announcements/', employee_announcements, name='employee_announcements'),
]