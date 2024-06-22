import json

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_

import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, Groups, Locations, Subjects, \
    StudentCharity, Roles, TeacherBlackSalary, GroupReason, TeacherObservationDay, DeletedStudents
from backend.student.functions import get_student_info, get_completed_student_info
from backend.tasks.models import Tasks


@app.route(f'{api}/teacher_tasks', methods=["POST", "GET"])
# @jwt_required()
def teacher_tasks():
    april = datetime.strptime("2024-03", "%Y-%m")
    teacher = Teachers.query.filter(Teachers.user_id == 3).first()
    change_teacher_tasks(teacher)
    student_ids = []
    for group in teacher.group:
        for student in group.student:
            student_ids.append(student.id)
    students = db.session.query(Students).join(Students.user).filter(Users.balance < 0).filter(Students.deleted_from_register == None, Students.id.in_(student_ids)).all()
    completed_tasks = []
    payments_list = []
    if request.method == "GET":
        for student in students:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    if get_student_info(student) != None:
                        payments_list.append(get_student_info(student))
                    if get_completed_student_info(student) != None:
                        completed_tasks.append(get_completed_student_info(student))
            else:
                if get_student_info(student) != None:
                    payments_list.append(get_student_info(student))
                if get_completed_student_info(student) != None:
                    completed_tasks.append(get_completed_student_info(student))
        return jsonify({'completed_tasks': completed_tasks, 'in_progress': payments_list})
    if request.method == "POST":
        return jsonify({"status": "true"})


def change_teacher_tasks(teacher):
    today = datetime.today()
    april = datetime.strptime("2024-03", "%Y-%m")
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    excuse_task_type = Tasks.query.filter_by(name='excuses', role='teacher').first()
    student_ids = []
    for group in teacher.group:
        for student in group.student:
            student_ids.append(student.id)
    students = db.session.query(Students).join(Students.user).filter(Users.balance < 0
                                                                     ).filter(
        Students.deleted_from_register == None, Students.id.in_(student_ids)).all()
    tasks = {
        'excuses': 0
    }
    for student in students:
        if student.deleted_from_group:
            if student.deleted_from_group[-1].day.month.date >= april:
                if student.excuses:
                    if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                        -1].to_date <= date_strptime:
                        tasks['excuses'] += 1
                else:
                    tasks['excuses'] += 1
        else:
            if student.excuses:
                if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                    -1].to_date <= date_strptime:
                    tasks['excuses'] += 1
            else:
                tasks['excuses'] += 1

