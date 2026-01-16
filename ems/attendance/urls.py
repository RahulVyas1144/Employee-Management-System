from django.urls import path
from .views import (
    clock_in,
    clock_out,
    attendance_history,
    admin_attendance
)

urlpatterns = [
    path('attendance/clock-in/', clock_in, name='clock_in'),
    path('attendance/clock-out/', clock_out, name='clock_out'),
    path('attendance/history/', attendance_history, name='attendance_history'),
    path('dashboard/attendance/', admin_attendance, name='admin_attendance'),
]
