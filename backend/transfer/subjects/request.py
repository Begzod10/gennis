from backend.models.models import Subjects, SubjectLevels
import requests
from backend.transfer.api import token

def transfer_subjects():
    request = 'transfer_subjects: '
    subjects = Subjects.query.order_by(Subjects.id).all()
    for subject in subjects:
        info = {
            'old_id': subject.id,
            'name': subject.name,
            'ball_number': subject.ball_number,
        }
        url = 'http://localhost:8000/Subjects/subject/'
        x = requests.post(url, json=info)
        print(x.status_code)
        request += f'{x.status_code} '
    return request


def transfer_subject_levels():
    request = 'transfer_subject_levels: '
    subject_levels = SubjectLevels.query.order_by(SubjectLevels.id).all()
    for subject_level in subject_levels:
        subject_id = 0
        subjects_url = 'http://localhost:8000/Subjects/subject/'
        y = requests.get(subjects_url)
        print(y.text)
        info = {
            'old_id': subject_level.id,
            'name': subject_level.name,
            'subject_id': subject_id
        }
        url = 'http://localhost:8000/Subjects/subject_level_create/'
        # x = requests.post(url, json=info)
        # print(x.status_code)
        # request += f'{x.status_code} '
    return request
