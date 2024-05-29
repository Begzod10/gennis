import json

import os
from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_, migrate

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_

from backend.functions.filters import old_current_dates
import requests
from backend.functions.debt_salary_update import salary_debt
from flask_jwt_extended import jwt_required
from backend.student.class_model import Student_Functions
from backend.group.class_model import Group_Functions
from datetime import datetime
from backend.functions.utils import find_calendar_date, update_salary, iterate_models, get_json_field
from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, Groups, Locations, Subjects, \
    StudentCharity, Roles, TeacherBlackSalary, GroupReason, TeacherObservationDay, DeletedStudents, \
    TeacherGroupStatistics
from datetime import timedelta
from backend.models.models import CalendarDay, CalendarMonth, CalendarYear
from backend.functions.utils import api, send_subject_server


@app.route('/group_subject/<int:group_id>', methods=["POST", "GET"])
def group_subject(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    send_subject_server(classroom_server, group.subject)
    return jsonify({
        "status": True
    })
