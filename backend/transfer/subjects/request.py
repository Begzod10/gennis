from backend.models.models import Subjects, SubjectLevels
import requests
from app import app


def transfer_subjects():
    with app.app_context():
        subjects = Subjects.query.order_by(Subjects.id).all()
        for subject in subjects:
            info = {
                'old_id': subject.id,
                'name': subject.name,
                'ball_number': subject.ball_number,
            }
            url = 'http://localhost:8000/Subjects/subject/'
            x = requests.post(url, json=info)
            print(x.text)
        return True


def transfer_subject_levels(token):
    with app.app_context():
        subject_levels = SubjectLevels.query.order_by(SubjectLevels.id).all()
        subjects_url = 'http://localhost:8000/Subjects/subject/'
        y = requests.get(url=subjects_url, headers={'Authorization': f"JWT {token}"})
        for subject in y.json()['subjects']:
            for subject_level in subject_levels:
                if subject_level.subject_id == subject.get('old_id'):
                    info = {
                        'old_id': subject_level.id,
                        'name': subject_level.name,
                        'subject': subject.get('id')
                    }
                    url = 'http://localhost:8000/Subjects/subject_level_create/'
                    x = requests.post(url, json=info)
                    print(x.text)
        return True
