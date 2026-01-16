from attendance.models import Attendance
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employees.models import EmployeeProfile

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Temporary redirect (we will improve later)
            if user.is_superuser:
                return redirect('/admin-dashboard/')
            else:
                return redirect('/employee-dashboard/')
        

        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login/')

    return render(request, 'login.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('/signup/')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/signup/')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        EmployeeProfile.objects.create(
            user=user,
            department="Not Assigned",
            salary=0,
            experience=0
        )


        messages.success(request, "Account created successfully")
        return redirect('/login/')

    return render(request, 'signup.html')

from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def employee_dashboard(request):
    employee = EmployeeProfile.objects.get(user=request.user)
    today = timezone.now().date()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    return render(request, 'employee_dashboard.html', {
        'attendance': attendance
    })


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('/login/')
