from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    salary = models.IntegerField()
    experience = models.IntegerField()
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username
