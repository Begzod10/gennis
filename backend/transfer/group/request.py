from backend.models.models import CourseTypes, Groups
import requests
from app import app


def transfer_course_types():
    with app.app_context():
        course_types = CourseTypes.query.order_by(CourseTypes.id).all()
        for course_type in course_types:
            info = {
                'old_id': course_type.id,
                'name': course_type.name,
            }
            url = 'http://localhost:8000/Group/course_types/'
            x = requests.post(url, json=info)
            print(x.text)
        return True


def transfer_group():
    with app.app_context():
        groups = Groups.query.order_by(Groups.id).all()
        for group in groups:
            info = {
                'old_id': group.id,
                'name': group.name,
                'language': group.education_language,
                'level': group.level_id,
                'subject': group.subject_id,
                'teacher': [group.teacher_id],
                'students': [student.id for student in group.student],
                'course_type': group.course_type_id,
                'branch': group.location_id,
                'system': 1,
                'teacher_salary': group.teacher_salary,
                'attendance_days': group.attendance_days,
                'price': group.price,
                'deleted': group.deleted,
                'status': group.status
            }
            url = 'http://localhost:8000/Transfer/groups/create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
