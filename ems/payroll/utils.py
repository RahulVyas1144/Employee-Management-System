import calendar
import os
from datetime import date

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from attendance.models import Attendance

MONTH_NAME_TO_NUMBER = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}


def _currency(value):
    try:
        return f"INR {float(value):,.2f}"
    except (TypeError, ValueError):
        return "INR 0.00"


def _safe_text(value):
    if value is None:
        return "N/A"
    if isinstance(value, str) and value.strip() == "":
        return "N/A"
    return str(value)


def _month_number(month_name):
    if not month_name:
        return None
    return MONTH_NAME_TO_NUMBER.get(month_name.strip().lower())


def _compute_paid_days(employee, month_name, year):
    month_number = _month_number(month_name)
    if not month_number:
        return 0

    try:
        year_int = int(year)
        start_date = date(year_int, month_number, 1)
        end_date = date(year_int, month_number, calendar.monthrange(year_int, month_number)[1])
    except (TypeError, ValueError):
        return 0

    return Attendance.objects.filter(
        employee=employee,
        date__range=(start_date, end_date),
        clock_in__isnull=False,
        clock_out__isnull=False,
    ).count()


def generate_payslip(payroll):
    file_name = f"payslip_{payroll.employee.user.username}_{payroll.month}_{payroll.year}.pdf"
    payslip_dir = os.path.join(settings.MEDIA_ROOT, 'payslips')
    os.makedirs(payslip_dir, exist_ok=True)

    file_path = os.path.join(payslip_dir, file_name)
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(colors.HexColor('#0F4C81'))
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 24)
    c.drawString(40, height - 70, 'Employee Management System')
    c.setFont('Helvetica-Bold', 34)
    c.drawRightString(width - 40, height - 60, 'PaySlip')

    # Logo block on top-left
    c.setFillColor(colors.white)
    c.rect(40, height - 105, 90, 70, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#0F4C81'))
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(85, height - 65, 'EMS')
    c.setFont('Helvetica', 8)
    c.drawCentredString(85, height - 80, 'Company Logo')

    # Employee / payroll panels
    employee = payroll.employee
    user = employee.user
    employee_name = _safe_text(user.get_full_name() or user.username)
    employee_id = _safe_text(employee.id)
    designation = _safe_text(getattr(employee, 'designation', None))
    pf_number = _safe_text(getattr(employee, 'pf_number', None))
    bank_account = _safe_text(getattr(employee, 'bank_account', None))

    month = _safe_text(payroll.month)
    year = _safe_text(payroll.year)
    joining_date = _safe_text(user.date_joined.date() if getattr(user, 'date_joined', None) else None)
    department = _safe_text(getattr(employee, 'department', None))
    paid_days = _safe_text(_compute_paid_days(employee, payroll.month, payroll.year))

    left_x = 40
    right_x = width / 2 + 10
    panel_top = height - 150
    line_height = 18

    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(left_x, panel_top, 'Employee Information')
    c.setFont('Helvetica', 10)
    c.drawString(left_x, panel_top - line_height, f'Employee Name: {employee_name}')
    c.drawString(left_x, panel_top - line_height * 2, f'Employee ID: {employee_id}')
    c.drawString(left_x, panel_top - line_height * 3, f'Designation: {designation}')
    c.drawString(left_x, panel_top - line_height * 4, f'PF Number: {pf_number}')
    c.drawString(left_x, panel_top - line_height * 5, f'Bank Account No: {bank_account}')

    c.setFont('Helvetica-Bold', 12)
    c.drawString(right_x, panel_top, 'Payroll Information')
    c.setFont('Helvetica', 10)
    c.drawString(right_x, panel_top - line_height, f'Month: {month}')
    c.drawString(right_x, panel_top - line_height * 2, f'Year: {year}')
    c.drawString(right_x, panel_top - line_height * 3, f'Joining Date: {joining_date}')
    c.drawString(right_x, panel_top - line_height * 4, f'Department: {department}')
    c.drawString(right_x, panel_top - line_height * 5, f'Paid Days: {paid_days}')

    # Earnings table
    table_top = panel_top - 160
    table_left = 40
    table_width = width - 80
    table_col1 = table_left
    table_col2 = table_left + table_width * 0.5
    table_col3 = table_left + table_width * 0.75
    row_height = 22

    c.setFillColor(colors.HexColor('#0F4C81'))
    c.rect(table_left, table_top + 4, table_width, row_height + 4, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(table_col1 + 6, table_top + 10, 'Earnings')
    c.drawString(table_col2 + 6, table_top + 10, 'Entitled Amount')
    c.drawString(table_col3 + 6, table_top + 10, 'Earned Amount')

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(table_left, table_top - row_height * 5, table_width, row_height * 6 + 4, fill=False, stroke=True)
    c.line(table_col2, table_top + 4, table_col2, table_top - row_height * 5 + 4)
    c.line(table_col3, table_top + 4, table_col3, table_top - row_height * 5 + 4)

    c.setFont('Helvetica', 10)
    earnings = [
        ('Basic Salary', _currency(payroll.basic_salary), _currency(payroll.basic_salary)),
        ('HRA', _currency(0), _currency(0)),
        ('Bonus', _currency(0), _currency(0)),
        ('Allowances', _currency(0), _currency(0)),
        ('Total Earnings', _currency(payroll.basic_salary), _currency(payroll.basic_salary)),
    ]
    for index, row in enumerate(earnings):
        y = table_top - row_height * (index + 1)
        c.drawString(table_col1 + 6, y + 6, row[0])
        c.drawRightString(table_col2 + table_width * 0.25 - 6, y + 6, row[1])
        c.drawRightString(table_col3 + table_width * 0.25 - 6, y + 6, row[2])
        c.line(table_left, y, table_left + table_width, y)

    # Deductions table
    deduction_top = table_top - row_height * 7 - 20
    c.setFillColor(colors.HexColor('#0F4C81'))
    c.rect(table_left, deduction_top + 4, table_width, row_height + 4, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(table_col1 + 6, deduction_top + 10, 'Deductions')
    c.drawString(table_col2 + 6, deduction_top + 10, 'Entitled Amount')
    c.drawString(table_col3 + 6, deduction_top + 10, 'Deducted Amount')

    c.setFillColor(colors.black)
    c.rect(table_left, deduction_top - row_height * 5, table_width, row_height * 6 + 4, fill=False, stroke=True)
    c.line(table_col2, deduction_top + 4, table_col2, deduction_top - row_height * 5 + 4)
    c.line(table_col3, deduction_top + 4, table_col3, deduction_top - row_height * 5 + 4)

    deductions = [
        ('PF', _currency(0), _currency(0)),
        ('Insurance', _currency(0), _currency(0)),
        ('Professional Tax', _currency(0), _currency(0)),
        ('Other Deductions', _currency(payroll.deductions), _currency(payroll.deductions)),
        ('Total Deductions', _currency(payroll.deductions), _currency(payroll.deductions)),
    ]
    for index, row in enumerate(deductions):
        y = deduction_top - row_height * (index + 1)
        c.drawString(table_col1 + 6, y + 6, row[0])
        c.drawRightString(table_col2 + table_width * 0.25 - 6, y + 6, row[1])
        c.drawRightString(table_col3 + table_width * 0.25 - 6, y + 6, row[2])
        c.line(table_left, y, table_left + table_width, y)

    # Net pay highlight
    net_box_top = deduction_top - row_height * 6 - 30
    net_box_height = 60
    c.setFillColor(colors.HexColor('#E8F1FF'))
    c.rect(table_left, net_box_top - net_box_height + 10, table_width, net_box_height, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#0F4C81'))
    c.setFont('Helvetica-Bold', 18)
    c.drawString(table_left + 10, net_box_top - 30, 'NET PAY')
    c.setFont('Helvetica-Bold', 22)
    c.drawRightString(table_left + table_width - 10, net_box_top - 30, _currency(payroll.net_salary))

    # Authorized signature / stamp
    sign_top = net_box_top - net_box_height - 70
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(table_left, sign_top, table_left + 220, sign_top)
    c.setFont('Helvetica', 10)
    c.drawString(table_left, sign_top - 14, 'Authorized Signature')
    c.rect(table_left + table_width - 180, sign_top - 30, 160, 30, fill=False, stroke=True)
    c.setFont('Helvetica', 10)
    c.drawCentredString(table_left + table_width - 100, sign_top - 14, 'Company Stamp')

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(40, 40, 'This is a system-generated payslip and does not require a physical signature.')

    c.showPage()
    c.save()

    return file_path
