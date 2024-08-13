import requests

from app import app
from backend.models.models import TeacherSalary, TeacherSalaries,TeacherBlackSalary


def transfer_teacher_salary():
    with app.app_context():
        teachers = TeacherSalary.query.order_by(TeacherSalary.id).all()
        for teacher in teachers:
            year_str = teacher.calendar_month.date.strftime(
                '%Y-%m-%d') if teacher.calendar_month and teacher.calendar_month.date else None
            info = {
                "teacher": teacher.teacher_id,
                "branch": teacher.location_id,
                "teacher_salary_type": '',
                "month_date": year_str,
                "total_salary": teacher.total_salary,
                "remaining_salary": teacher.remaining_salary,
                "taken_salary": teacher.taken_money,
                "total_black_salary": 0,
                "percentage": 0,
                "worked_days": 0
            }
            url = 'http://localhost:8000/Transfer/teachers/teacher_salary/'
            x = requests.post(url, json=info)
            if x.status_code != 200:
                print(x.text)

    return True


def transfer_teacher_salary_list():
    with app.app_context():
        teachers = TeacherSalaries.query.order_by(TeacherSalaries.id).all()
        for teacher in teachers:
            info = {
                "teacher": teacher.teacher_id,
                "salary_id": teacher.salary_location_id,
                "payment": teacher.payment_type_id,
                "branch": teacher.location_id,
                "comment": teacher.reason,
                "deleted": False,
                "salary": teacher.payment_sum
            }
            url = 'http://localhost:8000/Transfer/teachers/teacher_salary_list/'
            x = requests.post(url, json=info)
            if x.status_code != 200:
                print(x.text)

    return True


def transfer_teacher_black_salary():
    with app.app_context():
        teachers = TeacherBlackSalary.query.order_by(TeacherBlackSalary.id).all()
        for teacher in teachers:
            year_str = teacher.calendar_month.date.strftime(
                '%Y-%m-%d') if teacher.calendar_month and teacher.calendar_month.date else None
            info = {
                "teacher": teacher.teacher_id,
                "group": None,
                "student": teacher.student_id,
                "black_salary": teacher.total_salary,
                "month_date": year_str,
                "status": teacher.status
            }
            url = 'http://localhost:8000/Transfer/teachers/teacher_black_salary/'
            x = requests.post(url, json=info)
            if x.status_code != 200:
                print(x.text)

    return True
