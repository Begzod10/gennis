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
from backend.group.models import GroupTest
import calendar
from backend.functions.utils import get_or_creat_datetime


@app.route('/create_test/<int:group_id>', methods=["POST", "GET"])
def create_test(group_id):
    print("hello")
    info = request.get_json()['info']
    year, month, day = get_or_creat_datetime(info['year'], info['month'], info['day'])
    create_test = GroupTest(title=info['title'], group_id=group_id, subject_id=info['subject_id'],
                            level_id=info['level_id'], calendar_year=year.id, calendar_month=month.id,
                            calendar_day=day.id)
    create_test.add()
    return jsonify({
        "status": True
    })


@app.route('/get_subject_date/<int:group_id>', methods=["POST", "GET"])
def get_subject_date(group_id):
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    _, num_days = calendar.monthrange(current_year, current_month)
    group = Groups.query.filter(Groups.id == group_id).first()
    info = {
        'subject': {
            'id': group.subject.id,
            'name': group.subject.name,
            'levels': [],
            'calendar': {
                'year': current_year,
                'month': current_month,
                'days': list(range(1, num_days + 1))
            }
        }
    }
    for level in group.subject.subject_level:
        level_date = {
            'id': level.id,
            'name': level.name,
            'subject_id': group.subject.id
        }
        info['subject']['levels'].append(level_date)
    return jsonify({
        "info": info
    })


@app.route('/group_subject/<int:group_id>', methods=["POST", "GET"])
def group_subject(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    send_subject_server(classroom_server, group.subject)
    return jsonify({
        "status": True
    })
