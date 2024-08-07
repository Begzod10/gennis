from backend.models.models import Students
import requests
from app import app


def transfer_students():
    with app.app_context():
        students = Students.query.order_by(Students.id).all()
        for student in students:
            subjects = []
            for subject in student.subject:
                subjects.append(subject.id)
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
                "user": student.user_id,
                "subject": subjects,
                "parents_number": phone,
                "shift": shift,
                "representative_name": student.representative_name,
                "representative_surname": student.representative_surname,
                "old_id": student.id,
                "extra_payment": student.extra_payment,
                "old_money": student.user.balance
            }
            print(info)
            url = 'http://localhost:8000/Transfer/students/students_create/'
            x = requests.post(url, json=info)
            print(x.text)
            break
            pass
        return True
