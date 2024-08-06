from backend.student.models import Students
import requests
from app import app


def transfer_students(token):
    with app.app_context():
        students = Students.query.order_by(Students.id).all()
        for student in students:
            subjects = []
            for subject in students.subject:
                subjects.append(subject.id)
            info = {
                "user": student.user_id,
                "subject": subjects,
                "parents_number": student,
                "shift": "string",
                "representative_name": "string",
                "representative_surname": "string",
                "old_id": -2147483648,
                "extra_payment": "string",
                "old_money": -9223372036854776000
            }
            url = 'http://localhost:8000/Users/users/create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
