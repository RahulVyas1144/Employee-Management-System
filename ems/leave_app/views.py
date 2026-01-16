from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.http import HttpResponseForbidden

from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from employees.models import EmployeeProfile
from .models import Leave

@login_required
def apply_leave(request):
    employee = EmployeeProfile.objects.get(user=request.user)

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        Leave.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        return redirect('/employee/leaves/')

    return render(request, 'apply_leave.html')


@login_required
def leave_history(request):
    employee = EmployeeProfile.objects.get(user=request.user)
    leaves = Leave.objects.filter(employee=employee).order_by('-id')
    return render(request, 'leave_history.html', {'leaves': leaves})


@login_required
def admin_leave_requests(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")
    
    leaves = Leave.objects.all().order_by('-id')
    return render(request, 'admin_leave_requests.html', {'leaves': leaves})

@login_required
def approve_leave(request, leave_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'Approved'
    leave.save()

    send_mail(
    subject='Leave Approved',
    message=f'Hi {leave.employee.user.username}, your leave has been APPROVED.',
    from_email=settings.EMAIL_HOST_USER,
    recipient_list=[leave.employee.user.email],
    fail_silently=False,
)


    return redirect('/dashboard/leaves/')


@login_required
def reject_leave(request, leave_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")
    leave = get_object_or_404(Leave, id=leave_id)
    leave.status = 'Rejected'
    leave.save()

    send_mail(
    subject='Leave Rejected',
    message=f'Hi {leave.employee.user.username}, your leave has been REJECTED.',
    from_email=settings.EMAIL_HOST_USER,
    recipient_list=[leave.employee.user.email],
    fail_silently=False,
)


    return redirect('/dashboard/leaves/')
