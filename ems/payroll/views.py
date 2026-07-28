from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employees.models import EmployeeProfile
from .models import Payroll
from .utils import generate_payslip
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
import calendar
from datetime import date
from leave_app.models import Leave
from attendance.models import Attendance
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
        return HttpResponseForbidden("Not allowed")

    employees = EmployeeProfile.objects.all()

    if request.method == "POST":
        # AJAX: load employee + attendance + salary info
        if request.POST.get('action') == 'load':
            employee_id = request.POST.get('employee_id')
            month = request.POST.get('month')
            year_raw = request.POST.get('year')
            try:
                year = int(year_raw)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Invalid year'}, status=400)

            try:
                employee = EmployeeProfile.objects.get(id=employee_id)
            except EmployeeProfile.DoesNotExist:
                return JsonResponse({'error': 'Employee not found'}, status=404)

            # resolve month number
            try:
                month_number = list(calendar.month_name).index(month.capitalize())
            except ValueError:
                try:
                    month_number = int(month)
                except Exception:
                    return JsonResponse({'error': 'Invalid month'}, status=400)

            month_start = date(year, month_number, 1)
            month_end = date(year, month_number, calendar.monthrange(year, month_number)[1])

            working_days = sum(1 for day in range(1, calendar.monthrange(year, month_number)[1] + 1)
                               if date(year, month_number, day).weekday() != 6)

            present_days = Attendance.objects.filter(
                employee=employee,
                date__range=(month_start, month_end),
                clock_in__isnull=False,
                clock_out__isnull=False
            ).count()

            approved_leaves = Leave.objects.filter(
                employee=employee,
                status='Approved',
                start_date__lte=month_end,
                end_date__gte=month_start
            )
            leave_days = 0
            for lv in approved_leaves:
                s = max(lv.start_date, month_start)
                e = min(lv.end_date, month_end)
                leave_days += (e - s).days + 1

            absent_days = max(0, working_days - present_days - leave_days)
            paid_days = present_days + leave_days

            basic_salary = getattr(employee, 'salary', 0) or 0
            hra = getattr(employee, 'hra', 0) or 0
            da = getattr(employee, 'da', 0) or 0
            other_allowances = getattr(employee, 'other_allowances', 0) or 0

            data = {
                'employee': {
                    'id': employee.id,
                    'username': employee.user.username,
                    'full_name': employee.user.get_full_name() or employee.user.username,
                    'department': getattr(employee, 'department', ''),
                    'designation': getattr(employee, 'designation', ''),
                    'email': employee.user.email,
                },
                'attendance': {
                    'working_days': working_days,
                    'present_days': present_days,
                    'leave_days': leave_days,
                    'absent_days': absent_days,
                    'paid_days': paid_days,
                },
                'salary': {
                    'basic_salary': basic_salary,
                    'hra': hra,
                    'da': da,
                    'other_allowances': other_allowances,
                }
            }

            return JsonResponse(data)

        # Regular generate flow
        employee_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        year_raw = request.POST.get('year')
        deductions = float(request.POST.get('deductions', 0) or 0)

        try:
            year = int(year_raw)
        except (TypeError, ValueError):
            messages.error(request, "Invalid year value. Please enter a valid year.")
            return render(request, 'admin_generate_payroll.html', {
                'employees': employees
            })

        # prevent duplicate payroll for same employee/month/year
        if Payroll.objects.filter(employee_id=employee_id, month=month, year=year).exists():
            messages.error(request, "Payroll already exists for this employee for the selected month and year.")
            return render(request, 'admin_generate_payroll.html', {
                'employees': employees
            })

        employee = EmployeeProfile.objects.get(id=employee_id)
        basic_salary = employee.salary or 0

        # fetch editable components
        bonus = float(request.POST.get('bonus', 0) or 0)
        incentive = float(request.POST.get('incentive', 0) or 0)
        other_allowances = float(request.POST.get('other_allowances', 0) or 0)
        tax = float(request.POST.get('tax', 0) or 0)
        pf = float(request.POST.get('pf', 0) or 0)
        esi = float(request.POST.get('esi', 0) or 0)
        other_deduction = float(request.POST.get('other_deduction', 0) or 0)

        gross = basic_salary + bonus + incentive + other_allowances
        total_deductions = tax + pf + esi + other_deduction + deductions
        net_salary = gross - total_deductions

        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            basic_salary=basic_salary,
            deductions=int(total_deductions),
            net_salary=int(net_salary)
        )
        file_path = generate_payslip(payroll)

        print(f"[EMAIL DEBUG] EMAIL_HOST={settings.EMAIL_HOST}")
        print(f"[EMAIL DEBUG] EMAIL_PORT={settings.EMAIL_PORT}")
        print(f"[EMAIL DEBUG] EMAIL_HOST_USER={settings.EMAIL_HOST_USER}")

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

