import requests

from app import app
from backend.models.models import EducationLanguage, AttendanceHistoryStudent, AttendanceDays


def transfer_attendance_per_month():
    with app.app_context():
        request = 'attendance_per_month:'
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
                'month_date': attendance.calendar_month.date.strftime("%Y-%m"),
                'total_charity': attendance.total_discount,
                'system': 1,
                'absent_days': attendance.absent_days,
                'scored_days': attendance.scored_days,
                'present_days': attendance.present_days
            }
            url = 'http://localhost:8000/Transfer/attendance/create/'
            x = requests.post(url, json=info)
            print(x.text)
            print(x.status_code)
            request += f' {x.status_code}'
        return request


def transfer_attendance_per_day():
    with app.app_context():
        request = 'attendance_per_day:'
        attendances = AttendanceDays.query.order_by(AttendanceDays.id).all()
        for attendance in attendances:
            info = {
                'old_id': attendance.id,
                'student': attendance.student_id,
                'teacher': attendance.teacher_id,
                'group': attendance.group_id,
                'debt_per_day': attendance.balance_per_day,
                'salary_per_day': attendance.salary_per_day,
                'charity_per_day': attendance.discount_per_day,
                'day': attendance.calendar_day.date.strftime("%Y-%m-%d"),
                'homework_ball': attendance.homework,
                'dictionary_ball': attendance.dictionary,
                'activeness_ball': attendance.activeness,
                'average': attendance.average_ball,
                'reason': attendance.reason,
                'month_date': attendance.calendar_month.date.strftime("%Y-%m"),
                'teacher_ball': attendance.teacher_ball,
            }
            url = 'http://localhost:8000/Transfer/attendance/create/'
            x = requests.post(url, json=info)
            print(x.text)
            print(x.status_code)
            request += f' {x.status_code}'
        return request
