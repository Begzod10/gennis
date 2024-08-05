from backend.models.models import CourseTypes
import requests


def transfer_course_types():
    request = 'transfer_course_types:'
    course_types = CourseTypes.query.order_by(CourseTypes.id).all()
    for course_type in course_types:
        info = {
            'old_id': course_type.id,
            'name': course_type.name,
        }
        url = 'http://localhost:8000/Group/course_types/'
        x = requests.post(url, json=info)
        print(x.status_code)
        request += f' {x.status_code}'
    return request
