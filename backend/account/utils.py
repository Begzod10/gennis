from backend.models.models import Capital, CapitalTerm, AccountingPeriod, CalendarMonth
from backend.student.models import Students
from backend.teacher.models import Teachers
from .models import TeacherSalary
from backend.functions.utils import find_calendar_date
from app import db, desc, contains_eager, session
from backend.models.models import func


def update_capital(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    capitals = Capital.query.filter(Capital.location_id == location_id).order_by(Capital.id).all()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    for capital in capitals:
        if capital.calendar_month != calendar_month.id:
            capex_down = CapitalTerm.query.filter(CapitalTerm.calendar_month == calendar_month.id,
                                                  CapitalTerm.calendar_year == calendar_year.id,
                                                  CapitalTerm.capital_id == capital.id).first()
            if not capex_down:
                down_cost = capital.price / (12 * capital.term)
                info = {
                    "calendar_month": calendar_month.id,
                    "calendar_year": calendar_year.id,
                    "capital_id": capital.id,
                    "account_period_id": accounting_period.id,
                    "down_cost": -down_cost,

                }
                capex_down = CapitalTerm(**info)
                capex_down.add()
            all_capex_down = \
                db.session.query(func.sum(CapitalTerm.down_cost).filter(CapitalTerm.capital_id == capital.id)).first()[
                    0]
            capital.total_down_cost = -all_capex_down
            db.session.commit()


def student_collection_api():
    students_report_types = {
        "green": {
            "total": "",
            "students": []
        },
        "yellow": {
            "total": "",
            "students": []
        },
        "red": {
            "total": "",
            "students": []
        },
    }
    students = Students.query.all()
    total_green = 0
    total_yellow = 0
    total_red = 0
    for student in students:
        info = {
            "user": student.user.convert_json(),
            "student": {
                "id": student.id,
                "subjects": [],
                "combined_debt": student.combined_debt
            },
        }
        for subject in student.subject:
            info_subject = {
                "id": subject.id,
                "name": subject.name
            }
            info["student"]["subjects"].append(info_subject)
        if student.debtor == 0:
            total_green += abs(student.combined_debt)
            students_report_types["green"]["students"].append(info)
        if student.debtor == 1:
            total_yellow += abs(student.combined_debt)
            students_report_types["yellow"]["students"].append(info)
        if student.debtor == 2:
            total_red += abs(student.combined_debt)
            students_report_types["red"]["students"].append(info)
    students_report_types["green"]["total"] = total_green
    students_report_types["yellow"]["total"] = -total_yellow
    students_report_types["red"]["total"] = -total_red
    return students_report_types


def teacher_collection_api():
    teacher_report_info = {
        "remaining_salaries": "",
        "taken_salaries": "",
        "teachers": []
    }
    remaining_salaries = 0
    taken_salaries = 0
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    teachers = db.session.query(Teachers).join(Students.group).options(
        contains_eager(Teachers.attendance_location)).filter(
        TeacherSalary.calendar_year == calendar_year.id, TeacherSalary.calendar_month == calendar_month.id).all()
    for teacher in teachers:
        info = {
            "user": teacher.user.convert_json(),
            "teacher": {
                "id": teacher.id,
                "table_color": teacher.table_color,
                "salary": None
            }
        }
        for salary in teacher.attendance_location:
            info_salary = {
                "total_salary": salary.total_salary,
                "remaining_salary": salary.remaining_salary,
                "taken_money": salary.taken_money,
                "status": salary.status
            }
            info["teacher"]["salary"] = info_salary
            if salary.status == True:
                taken_salaries += salary.taken_salary
            else:
                if salary.remaining_salary:
                    remaining_salaries += salary.remaining_salary
                    taken_salaries += salary.taken_salary
                else:
                    remaining_salaries += salary.total_salary
        teacher_report_info["teachers"].append(info)
    teacher_report_info["remaining_salaries"] = remaining_salaries
    teacher_report_info["taken_salaries"] = taken_salaries
    return teacher_report_info
