from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from employees.models import EmployeeProfile
from .models import Attendance
from django.shortcuts import render
@login_required
def clock_in(request):
    if request.user.is_superuser:
        return redirect('/')

    employee = EmployeeProfile.objects.get(user=request.user)
    local_now = timezone.localtime(timezone.now())
    today = local_now.date()

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    if attendance.clock_in is None:
        attendance.clock_in = local_now.time()
        attendance.save()

    return redirect('/employee-dashboard/')



@login_required
def clock_out(request):
    if request.user.is_superuser:
        return redirect('/')

    employee = EmployeeProfile.objects.get(user=request.user)
    local_now = timezone.localtime(timezone.now())
    today = local_now.date()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if attendance and attendance.clock_out is None:
        attendance.clock_out = local_now.time()
        attendance.save()

    return redirect('/employee-dashboard/')




@login_required
def attendance_history(request):
    if request.user.is_superuser:
        return redirect('/')

    employee = EmployeeProfile.objects.get(user=request.user)
    attendance_list = Attendance.objects.filter(
        employee=employee
    ).order_by('-date')

    return render(request, 'attendance_history.html', {
        'attendance_list': attendance_list
    })


from django.http import HttpResponseForbidden

@login_required
def admin_attendance(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")

    attendance_list = Attendance.objects.select_related(
        'employee', 'employee__user'
    ).order_by('-date')

    return render(request, 'admin_attendance.html', {
        'attendance_list': attendance_list
    })
