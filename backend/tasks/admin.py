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


@app.route('/teacher_tasks_home_page', methods=["POST", "GET"])
def teacher_tasks_home_page():
    students_yellow = Students.query.filter(Students.debtor == 1).all()
    students_red = Students.query.filter(Students.debtor == 2).all()
    print(students_yellow)
    print(students_red)
    return jsonify({"status": "true"})
