from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os

def generate_payslip(payroll):
    file_name = f"payslip_{payroll.employee.user.username}_{payroll.month}_{payroll.year}.pdf"
    payslip_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
    os.makedirs(payslip_dir, exist_ok=True)

    file_path = os.path.join(payslip_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "PAYSLIP")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Employee: {payroll.employee.user.username}")
    c.drawString(50, height - 130, f"Month: {payroll.month} {payroll.year}")

    c.drawString(50, height - 180, f"Basic Salary: {payroll.basic_salary}")
    c.drawString(50, height - 210, f"Deductions: {payroll.deductions}")
    c.drawString(50, height - 240, f"Net Salary: {payroll.net_salary}")

    c.drawString(50, height - 300, "This is a system generated payslip.")

    c.showPage()
    c.save()

    return file_path
