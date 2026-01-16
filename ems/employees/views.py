from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import EmployeeProfile


@login_required
def admin_employee_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")

    employees = EmployeeProfile.objects.all()
    return render(request, 'admin_employees.html', {'employees': employees})


from django.shortcuts import get_object_or_404, redirect

@login_required
def edit_employee(request, emp_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")
    employee = get_object_or_404(EmployeeProfile, id=emp_id)

    if request.method == "POST":
        employee.department = request.POST.get('department')
        employee.salary = request.POST.get('salary')
        employee.experience = request.POST.get('experience')
        employee.save()

        return redirect('/dashboard/employees/')

    return render(request, 'edit_employee.html', {'employee': employee})

@login_required
def delete_employee(request, emp_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")
    employee = get_object_or_404(EmployeeProfile, id=emp_id)
    employee.user.delete()   # deletes user + profile
    return redirect('/dashboard/employees/')

