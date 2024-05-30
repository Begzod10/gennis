import json

import os
from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_, migrate

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_
import requests

from datetime import datetime

from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, Groups

from backend.functions.utils import api, send_subject_server
from backend.group.models import GroupTest
import calendar
from backend.functions.utils import get_or_creat_datetime
from backend.student.models import StudentTest


@app.route('/create_test/<int:group_id>', methods=["POST", "GET"])
def create_test(group_id):
    info = request.get_json()['info']
    year, month, day = get_or_creat_datetime(info['year'], info['month'], info['day'])
    create_test = GroupTest(title=info['title'], group_id=group_id, subject_id=info['subject_id'],
                            level_id=info['level_id'], calendar_year=year.id, calendar_month=month.id,
                            calendar_day=day.id)
    create_test.add()
    return jsonify({
        "status": True
    })


@app.route('/evaluation_test/<int:group_id>', methods=["POST", "GET"])
def evaluation_test(group_id):
    info = request.get_json()['info']
    for student in info['students']:
        add_test_result = StudentTest(subject_id=info['subject_id'], level_id=info['level_id'],
                                      group_test_id=info['group_test_id'],
                                      student_id=student['id'], true_answers=int(student['true_answers']),
                                      false_answers=int(student['false_answers']), ball=int(student['overall_ball']),
                                      group_id=group_id)
        add_test_result.add()
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
