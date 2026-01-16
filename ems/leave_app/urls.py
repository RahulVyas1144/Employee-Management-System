from django.urls import path
from .views import (
    apply_leave,
    leave_history,
    admin_leave_requests,
    approve_leave,
    reject_leave
)

urlpatterns = [
    path('employee/leave/apply/', apply_leave, name='apply_leave'),
    path('employee/leaves/', leave_history, name='leave_history'),

    path('dashboard/leaves/', admin_leave_requests, name='admin_leaves'),
    path('dashboard/leaves/approve/<int:leave_id>/', approve_leave),
    path('dashboard/leaves/reject/<int:leave_id>/', reject_leave),
]
