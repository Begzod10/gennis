from backend.models.models import CourseTypes
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
