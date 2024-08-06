import requests

from app import app
from backend.teacher.models import Teachers


def transfer_teacher():
    with app.app_context():
        teachers = Teachers.query.order_by(Teachers.id).all()
        for teacher in teachers:
            info = {

                "user": teacher.user_id,
                "subject": [subject.id for subject in teacher.subject],
                "color": teacher.table_color,
                "total_students": teacher.total_students,
                'old_id':teacher.user_id

            }
            url = 'http://localhost:8000/Transfer/teachers/teachers/create/'
            x = requests.post(url, json=info)
            print(x.text)

    return True
