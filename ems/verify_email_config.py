import os
import smtplib
import socket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ems.settings')
import django

django.setup()

from django.conf import settings

print('EMAIL_BACKEND=', settings.EMAIL_BACKEND)
print('EMAIL_HOST=', settings.EMAIL_HOST)
print('EMAIL_PORT=', settings.EMAIL_PORT)
print('EMAIL_USE_TLS=', settings.EMAIL_USE_TLS)
print('EMAIL_HOST_USER=', settings.EMAIL_HOST_USER)

try:
    print('RESOLVES=', socket.gethostbyname(settings.EMAIL_HOST))
except Exception as exc:
    print('RESOLVE_ERROR=', exc)

try:
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    server.ehlo()
    if settings.EMAIL_USE_TLS:
        server.starttls()
        server.ehlo()
    print('SMTP_CONNECT=OK')
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print('SMTP_LOGIN=OK')
    server.quit()
except Exception as exc:
    print('SMTP_ERROR=', type(exc).__name__, exc)
