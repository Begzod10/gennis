from flask import session
from sqlalchemy import func

from app import app, db, desc, contains_eager, request, jsonify
from backend.group.models import Attendance, AttendanceDays

from backend.student.models import Students

from backend.account.utils import student_collection_api, teacher_collection_api
from backend.functions.utils import api, find_calendar_date, get_json_field, update_staff_salary_id, \
    update_teacher_salary_id, update_salary
from pprint import pprint
from sqlalchemy.orm import sessionmaker


@app.route('/collection', methods=["POST", "GET"])
def collection():
    return jsonify(
        {
            "students_collection": student_collection_api(),
            "teacher_collection": teacher_collection_api()
        }
    )


@app.route('/calculate_student_debts/<int:student_id>', methods=["POST", "GET"])
def calculate_student_debts(student_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    attendance = Attendance.query.filter(Attendance.student_id == student_id,
                                         Attendance.calendar_year == calendar_year.id,
                                         Attendance.calendar_month == calendar_month.id).first()
    student = Students.query.filter(Students.id == student_id).first()
    courses = []
    for group in student.group:
        attendance = Attendance.query.filter(Attendance.student_id == student_id,
                                             Attendance.calendar_year == calendar_year.id,
                                             Attendance.calendar_month == calendar_month.id,
                                             Attendance.group_id == group.id).first()
        attendance_days = AttendanceDays.query.filter(AttendanceDays.attendance_id == attendance.id).all()
        info = {
            "group": {
                "id": group.id,
                "name": group.name,
                "price": group.price
            },
            "result": ""
        }
        balance = 0
        balance_per_day = 0
        if attendance_days:
            for attendance_day in attendance_days:
                balance_per_day = attendance_day.balance_per_day
                balance += attendance_day.balance_per_day
            if len(attendance_days) < 13:
                calculate_day = 13 - len(attendance_days)
                calculate_debt = balance_per_day * calculate_day
                result = calculate_debt + balance
                info["result"] = result
        else:
            result = group.price
            info["result"] = result
        courses.append(info)
    total_debt = 0
    for course in courses:
        total_debt += int(course["result"])
    return jsonify({"total_debt": total_debt})
