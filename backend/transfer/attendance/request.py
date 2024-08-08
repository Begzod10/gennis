import requests

from app import app
from backend.models.models import EducationLanguage, AttendanceHistoryStudent


def transfer_language():
    with app.app_context():
        request = 'language:'
        attendances = AttendanceHistoryStudent.query.order_by(AttendanceHistoryStudent.id).all()
        for attendance in attendances:
            info = {
                'old_id': attendance.id,
                'student': attendance.student_id,
                'teacher': attendance.teacher_id,
                'group': attendance.group_id,
                'total_debt': attendance.total_debt,
                'ball_percentage': attendance.average_ball,
                'payment': attendance.payment,
                'remaining_debt': attendance.remaining_debt,

            }
            url = 'http://localhost:8000/Transfer/attendance/create/'
            x = requests.post(url, json=info)
            print(x.text)
            print(x.status_code)
            request += f' {x.status_code}'
        return request
