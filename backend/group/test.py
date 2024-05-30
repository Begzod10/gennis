import json

import os
from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_, migrate

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_
import requests

from datetime import datetime

from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, Groups
from backend.models.models import CalendarDay, CalendarMonth, CalendarYear
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


@app.route('/filter_tests_in_group/<int:group_id>', methods=["POST", "GET"])
def filter_tests_in_group(group_id):
    if request.method == "GET":
        calendar_dict = {}
        group_tests = GroupTest.query.filter(GroupTest.group_id == group_id).all()
        for group_test in group_tests:
            year = group_test.year.date.year
            month = group_test.month.date.month

            if year not in calendar_dict:
                calendar_dict[year] = set()

            calendar_dict[year].add(month)

        calendar = [{'year': year, 'months': list(months)} for year, months in calendar_dict.items()]
        return jsonify({
            "calendar": calendar
        })
    else:
        tests = []
        info = request.get_json()['info']
        year = datetime.strptime(f"{info['year']}", "%Y")
        month = datetime.strptime(f"{info['year']}-{info['month']}", "%Y-%m")
        filtered_year = CalendarYear.query.filter(CalendarYear.date == year).first()
        filtered_month = CalendarMonth.query.filter(CalendarMonth.date == month).first()
        group_tests = GroupTest.query.filter(GroupTest.group_id == group_id,
                                             GroupTest.calendar_year == filtered_year.id,
                                             GroupTest.calendar_month == filtered_month.id).all()
        for group_test in group_tests:
            info = {
                'id': group_test.id,
                'title': group_test.title,
                'group_id': group_test.group_id,
                'subject_id': group_test.subject_id,
                'level_id': group_test.level_id
            }
            tests.append(info)
        return jsonify({
            "tests": tests
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
