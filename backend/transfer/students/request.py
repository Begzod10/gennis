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
