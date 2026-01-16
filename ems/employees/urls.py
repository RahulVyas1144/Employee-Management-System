from django.urls import path
from .views import admin_employee_list, edit_employee, delete_employee

urlpatterns = [
    path('dashboard/employees/', admin_employee_list, name='admin_employees'),
    path('dashboard/employees/edit/<int:emp_id>/', edit_employee, name='edit_employee'),
    path('dashboard/employees/delete/<int:emp_id>/', delete_employee, name='delete_employee'),
]
