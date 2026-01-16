from django.urls import path

from .views import (
    login_view,
    signup_view,
    admin_dashboard,
    employee_dashboard,
    logout_view
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('logout/', logout_view, name='logout'),

]