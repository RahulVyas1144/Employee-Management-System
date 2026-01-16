from django.db import models
from employees.models import EmployeeProfile

class Payroll(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    basic_salary = models.IntegerField()
    deductions = models.IntegerField(default=0)
    net_salary = models.IntegerField()
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.month} {self.year}"
