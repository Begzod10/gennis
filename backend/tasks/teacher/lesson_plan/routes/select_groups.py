from app import app, request, db, jsonify

from datetime import datetime

from backend.group.models import Groups
from backend.models.models import Teachers, Users
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import api, find_calendar_date

from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.functions.filters import update_lesson_plan


@app.route(f'{api}/select_teacher_groups/<int:location_id>', methods=["POST", "GET"])
# @jwt_required()
def select_teacher_groups(location_id):
    # user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    teacher = Teachers.query.filter(Teachers.user_id == 3).first()
    # teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    groups = Groups.query.filter_by(teacher_id=teacher.id, location_id=location_id).all()
    groups_json = [group.convert_json() for group in groups]
    for group in groups:
        update_lesson_plan(group.id)
    return jsonify({'groups': groups_json})
