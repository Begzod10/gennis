from backend.models.models import Students, StudentHistoryGroups, StudentCharity
import requests

from app import app
from backend.models.models import Students, RegisterDeletedStudents


def transfer_students():
    with app.app_context():
        students = Students.query.filter(Students.id >= 7402).order_by(Students.id).all()
        for student in students:
            phone = 0
            for number in student.user.phone:
                if phone and phone.parent == True:
                    phone = number.phone
            shift = 0
            if student.morning_shift == True:
                shift = 1
            if student.night_shift == True:
                shift = 2
            info = {
                'old_id_filter': student.user_id,
                "user": student.user_id,
                "subject": [subject.id for subject in student.subject],
                "parents_number": phone,
                "shift": shift,
                "representative_name": student.representative_name,
                "representative_surname": student.representative_surname,
                "old_id": student.id,
                "extra_payment": student.extra_payment,
                "old_money": student.user.balance
            }
            url = 'http://localhost:8000/Transfer/students/students_create/'
            x = requests.post(url, json=info)
        return True


def transfer_deleted_students():
    with app.app_context():
        students = RegisterDeletedStudents.query.order_by(RegisterDeletedStudents.id).all()
        for student in students:
            year_str = student.day.date.strftime(
                '%Y-%m-%d') if student.day.date and student.day.date else None
            info = {
                "student": student.student_id,
                "comment": student.reason,
                "created": year_str
            }
            url = 'http://localhost:8000/Transfer/students/deleted_students_create/'
            x = requests.post(url, json=info)
        return True


def transfer_students_history_group():
    with app.app_context():
        student_history_groups = StudentHistoryGroups.query.order_by(StudentHistoryGroups.id).all()
        for student_history_group in student_history_groups:
            info = {
                'old_id': student_history_group.id,
                "student": student_history_groups.student_id,
                "teacher": student_history_groups.teacher_id,
                "reason": student_history_groups.reason,
                "group": student_history_groups.group_id,
                "left_day": student_history_group.left_day.strftime("%Y-%m-%d"),
                "joined_day": student_history_group.joined_day.strftime("%Y-%m-%d")
            }
            print(info)
            url = 'http://localhost:8000/Transfer/students/students-history-group/'
            x = requests.post(url, json=info)
            print(x.text)
        return True


def transfer_students_charity():
    with app.app_context():
        student_charities = StudentCharity.query.order_by(StudentCharity.id).all()
        for student_charity in student_charities:
            info = {
                'old_id': student_charity.id,
                "student": student_charity.student_id,
                "group": student_charity.group_id,
                "charity_sum": student_charity.discount,
                "added_data": student_charity.day.date.strftime("%Y-%m-%d"),
                "branch": student_charity.location_id
            }
            print(info)
            url = 'http://localhost:8000/Transfer/students/students-charity/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
