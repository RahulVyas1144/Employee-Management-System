from django.db import models
from employees.models import EmployeeProfile

class Attendance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.employee.user.username} - {self.date}"
