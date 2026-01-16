from django.urls import path
from .views import employee_payroll, admin_generate_payroll,download_payslip

urlpatterns = [
    path('employee/payroll/', employee_payroll, name='employee_payroll'),
    path('dashboard/payroll/', admin_generate_payroll, name='admin_payroll'),
    path('payroll/download/<int:payroll_id>/', download_payslip, name='download_payslip'),
]
