from app import app
from backend.teacher.models import Teachers


def transfer_teacher():
    with app.app_context():
        teachers = Teachers.query.order_by(Teachers.id).all()
        for teacher in teachers:
            info = {
                'old_id_filter': teacher.user_id,  # Use old_id for filtering
                'user': teacher.user_id,
                "subject": [subject.id for subject in teacher.subject],
                "color": teacher.table_color,
                "total_students": teacher.total_students,
                'old_id': teacher.user_id
            }
            print(info)
            url = 'http://localhost:8000/Transfer/teachers/teachers/create/'
            x = requests.post(url, json=info)
            print(x.text)

    return True


import requests


def transfer_teacher_branches():
    with app.app_context():
        teachers = Teachers.query.filter(Teachers.locations != None).order_by(Teachers.id).all()

        for teacher in teachers:
            for location in teacher.locations:

                info = {
                    "teacher_id": teacher.id,
                    "branch_id": location.id
                }

                url = 'http://localhost:8000/Transfer/teachers/teachers/add-branch/'
                x = requests.post(url, json=info)
                if x.status_code != 200 or x.status_code != 201:
                    print(x.text)
    return True
