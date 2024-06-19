import json

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_

from backend.functions.filters import old_current_dates
import requests
from backend.functions.debt_salary_update import salary_debt
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.student.class_model import Student_Functions
from backend.group.class_model import Group_Functions
from datetime import datetime
from backend.functions.utils import find_calendar_date, update_salary, iterate_models, get_json_field
from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, Groups, Locations, Subjects, \
    StudentCharity, Roles, TeacherBlackSalary, GroupReason, TeacherObservationDay, DeletedStudents, \
    TeacherGroupStatistics
from backend.student.functions import get_student_info, get_completed_student_info


@app.route(f'{api}/admin_tasks', methods=["POST", "GET"])
@jwt_required()
def admin_tasks():
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    students = Students.query.filter(Students.debtor > 0).join(Students.user).filter(
        Users.location_id == user.location_id).join(Students.student_debts)

    return jsonify({"status": "true"})

