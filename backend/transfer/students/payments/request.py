import requests

from app import app
from backend.models.models import StudentPayments


def transfer_students_Payment():
    with app.app_context():
        students = StudentPayments.query.order_by(StudentPayments.id).all()
        for student in students:
            year_str = student.day.date.strftime(
                '%Y-%m-%d') if student.day and student.day.date else None
            info = {

                "student": student.id,
                "payment_type": student.payment_type_id,
                "payment_sum": student.payment_sum,
                "status": student.payment,
                "branch": student.location_id,
                "added_data": year_str

            }
            print(info)
            url = 'http://localhost:8000/Transfer/students/students_payment_create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
