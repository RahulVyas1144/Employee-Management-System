from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Announcement




@login_required
def create_announcement(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == "POST":
        title = request.POST.get('title')
        message = request.POST.get('message')

        Announcement.objects.create(
            title=title,
            message=message
        )

        emails = User.objects.values_list('email', flat=True)

        send_mail(
            subject=title,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
            fail_silently=False
        )

        return redirect('/dashboard/announcements/')

    return render(request, 'admin_create_announcement.html')




@login_required
def employee_announcements(request):
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'employee_announcements.html', {
        'announcements': announcements
    })
