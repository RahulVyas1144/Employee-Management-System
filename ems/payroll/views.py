from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from employees.models import EmployeeProfile
from .models import Payroll
from .utils import generate_payslip
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import FileResponse, Http404
import os

@login_required
def employee_payroll(request):
    if request.user.is_superuser:
        return redirect('/')

    employee = EmployeeProfile.objects.get(user=request.user)
    payrolls = Payroll.objects.filter(employee=employee).order_by('-year')

    return render(request, 'employee_payroll.html', {
        'payrolls': payrolls
    })


@login_required
def admin_generate_payroll(request):
    if not request.user.is_superuser:
        return redirect('/')

    employees = EmployeeProfile.objects.all()

    if request.method == "POST":
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        year = request.POST.get('year')
        deductions = int(request.POST.get('deductions', 0))

        employee = EmployeeProfile.objects.get(id=employee_id)
        basic_salary = employee.salary
        net_salary = basic_salary - deductions

        payroll = Payroll.objects.create(
                employee=employee,
                month=month,
                year=year,
                basic_salary=basic_salary,
                deductions=deductions,
                net_salary=net_salary
        )
        file_path = generate_payslip(payroll)

        email = EmailMessage(
            subject="Payslip Generated",
            body="Your payslip is attached. Please find the PDF.",
            from_email=settings.EMAIL_HOST_USER,
            to=[employee.user.email],
        )

        email.attach_file(file_path)
        email.send(fail_silently=False)

        return redirect('/dashboard/payroll/')

    return render(request, 'admin_generate_payroll.html', {
        'employees': employees
    })


@login_required
def download_payslip(request, payroll_id):
    payroll = Payroll.objects.get(id=payroll_id)

    if request.user != payroll.employee.user and not request.user.is_superuser:
        raise Http404("Not allowed")

    file_name = f"payslip_{payroll.employee.user.username}_{payroll.month}_{payroll.year}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'payslips', file_name)

    if not os.path.exists(file_path):
        raise Http404("Payslip not found")

    return FileResponse(open(file_path, 'rb'), as_attachment=True)

