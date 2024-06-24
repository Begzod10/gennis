from app import db, jsonify, contains_eager, or_
from .models import TeacherObservation
from backend.models.models import CalendarYear, CalendarMonth, Students, Groups
from datetime import datetime
from backend.functions.utils import get_json_field


# for teachers.py

def prepare_scores(subject_ball_number):
    base_scores = [
        {"name": "homework", "id": 1, "title": "Uy ishi", "activeStars": 0, "stars": [{"active": False}] * 5},
        {"name": "active", "id": 1, "title": "Darsda qatnashishi", "activeStars": 0, "stars": [{"active": False}] * 5}
    ]

    if subject_ball_number > 2:
        base_scores.append(
            {"name": "dictionary", "id": 1, "title": "Lug'at", "activeStars": 0, "stars": [{"active": False}] * 5})

    return base_scores


def get_students_info(group_id, hour2):
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id, or_(Students.ball_time <= hour2, Students.ball_time == None)
    ).order_by(Students.id).all()

    student_list = []
    for student in students:
        debtor_color = ["green", "yellow", "red", "navy", "black"][student.debtor]
        student_info = {
            "id": student.user.id,
            "name": student.user.name.title(),
            "surname": student.user.surname.title(),
            "money": student.user.balance,
            "active": False,
            "checked": False,
            "profile_photo": student.user.photo_profile,
            "typeChecked": "",
            "date": {},
            "scores": {},
            "money_type": debtor_color
        }
        student_list.append(student_info)
    return student_list


