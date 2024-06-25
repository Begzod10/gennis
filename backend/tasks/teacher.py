import json

import pprint

from app import app, api, request, db, jsonify, contains_eager, classroom_server, or_

import requests
from datetime import datetime
from backend.models.models import Users, Attendance, Students, AttendanceDays, Teachers, StudentExcuses
from backend.student.functions import get_student_info, get_completed_student_info
from backend.tasks.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import api, find_calendar_date


@app.route(f'{api}/teacher_tasks_debt/<int:location_id>', methods=["POST", "GET"])
# @jwt_required()
def teacher_tasks_debt(location_id):
    today = datetime.today()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    april = datetime.strptime("2024-03", "%Y-%m")
    teacher = Teachers.query.filter(Teachers.user_id == 3).first()
    change_teacher_tasks(teacher, location_id)
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
        data = request.get_json()
        reason = data.get('comment')
        select = data.get('select')
        to_date = data.get('date')
        user_id = data.get('id')

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d")
        next_day = datetime.strptime(f'{today.year}-{today.month}-{int(today.day) + 1}', "%Y-%m-%d")
        student = Students.query.filter(Students.user_id == user_id).first()
        new_excuse = StudentExcuses(reason=reason if select == "tel ko'tardi" else "tel ko'tarmadi",
                                    to_date=to_date if select == "tel ko'tardi" else next_day,
                                    added_date=calendar_day.date,
                                    student_id=student.id)
        db.session.add(new_excuse)
        db.session.commit()
        change_teacher_tasks(teacher, location_id)

        task_type = Tasks.query.filter(Tasks.name == 'excuses', Tasks.role == 'teacher').first()
        task_statistics = TasksStatistics.query.filter(
            TasksStatistics.task_id == task_type.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).first()

        students_excuses = StudentExcuses.query.filter(StudentExcuses.student_id.in_(student_ids),
                                                       StudentExcuses.added_date == calendar_day.date).count()

        task_statistics.completed_tasks = students_excuses
        db.session.commit()

        task_statistics.completed_tasks_percentage = (
                                                             task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
        db.session.commit()
        overall_location_statistics = TasksStatistics.query.filter(
            TasksStatistics.user_id == teacher.user_id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).all()
        tasks_daily_statistics = TaskDailyStatistics.query.filter(
            TaskDailyStatistics.user_id == teacher.user_id,
            TaskDailyStatistics.location_id == location_id,
            TaskDailyStatistics.calendar_day == calendar_day.id
        ).first()
        overall_complete = 0
        for overall in overall_location_statistics:
            overall_complete += overall.completed_tasks
        completed_tasks_percentage = round((
                                                   overall_complete / tasks_daily_statistics.in_progress_tasks) * 100 if tasks_daily_statistics.in_progress_tasks > 0 else 0)

        tasks_daily_statistics.completed_tasks = overall_complete
        tasks_daily_statistics.completed_tasks_percentage = completed_tasks_percentage
        db.session.commit()

        return jsonify({"student": {
            'msg': "Komment belgilandi",
            'id': student.user.id
        }})


@app.route(f'{api}/teacher_tasks_lesson_plan/<int:location_id>', methods=["POST", "GET"])
# @jwt_required()
def teacher_tasks_lesson_plan(location_id):
    if request.method == "POST":
        pass
    return jsonify({"status": "true"})


@app.route(f'{api}/teacher_tasks_attendance/<int:location_id>', methods=["POST", "GET"])
# @jwt_required()
def teacher_tasks_attendance(location_id):
    if request.method == "GET":
        student_ids = []
        students_list = []
        teacher = Teachers.query.filter(Teachers.user_id == 3).first()
        teacher_attendances = AttendanceDays.query.filter(AttendanceDays.teacher_id == teacher.id,
                                                          AttendanceDays.calling_status == False,
                                                          AttendanceDays.location_id == location_id).all()
        for teacher_attendance in teacher_attendances:
            student_ids.append(teacher_attendance.student_id)
        students = Students.query.filter(Students.id.in_(student_ids)).all()
        for student in students:
            info = {
                'student_id': student.id,
                'user': student.user.convert_json(),
                'subjects': [subject.name for subject in student.subject]
            }
            students_list.append(info)
        return jsonify({"students_list": students_list})


def change_teacher_tasks(teacher, location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    april = datetime.strptime("2024-03", "%Y-%m")
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    excuse_task_type = Tasks.query.filter_by(name='excuses', role='teacher').first()
    lesson_plan_task_type = Tasks.query.filter_by(name='lesson_plan', role='teacher').first()
    attendance_task_type = Tasks.query.filter_by(name='attendance', role='teacher').first()
    student_ids = []
    for group in teacher.group:
        for student in group.student:
            student_ids.append(student.id)
    students = db.session.query(Students).join(Students.user).filter(Users.balance < 0
                                                                     ).filter(
        Students.deleted_from_register == None, Students.id.in_(student_ids)).all()
    tasks = {
        'excuses': 0,
        'lesson_plan': 0,
        'attendance': 0,
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

    lesson_plan = LessonPlan.query.filter(LessonPlan.date > date_strptime, LessonPlan.teacher_id == teacher.id).all()
    tasks['lesson_plan'] = len(lesson_plan)
    attendance_tasks = []
    teacher_attendances = AttendanceDays.query.filter(AttendanceDays.teacher_id == teacher.id,
                                                      AttendanceDays.calling_status == False,
                                                      AttendanceDays.location_id == location_id).all()
    for teacher_attendance in teacher_attendances:
        attendance_tasks.append(teacher_attendance.student_id)
    unique_tasks = []
    for task in attendance_tasks:
        if not task in unique_tasks:
            unique_tasks.append(task)
    tasks['attendance'] = len(unique_tasks)
    filtered_excuse_tasks = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, task_id=excuse_task_type.id,
                                                            user_id=teacher.user_id, location_id=location_id).first()
    if not filtered_excuse_tasks:
        add_excuse = TasksStatistics(calendar_year=calendar_year.id, calendar_month=calendar_month.id,
                                     calendar_day=calendar_day.id, user_id=teacher.user_id, task_id=excuse_task_type.id,
                                     in_progress_tasks=tasks['excuses'], location_id=location_id)
        db.session.add(add_excuse)
        db.session.commit()
    filtered_lesson_plan_tasks = TasksStatistics.query.filter_by(calendar_day=calendar_day.id,
                                                                 task_id=lesson_plan_task_type.id,
                                                                 user_id=teacher.user_id,
                                                                 location_id=location_id).first()
    if not filtered_lesson_plan_tasks:
        add_lesson_plan = TasksStatistics(calendar_year=calendar_year.id, calendar_month=calendar_month.id,
                                          calendar_day=calendar_day.id, user_id=teacher.user_id,
                                          task_id=lesson_plan_task_type.id,
                                          in_progress_tasks=tasks['lesson_plan'], location_id=location_id)
        db.session.add(add_lesson_plan)
        db.session.commit()
    filtered_attendance_tasks = TasksStatistics.query.filter_by(calendar_day=calendar_day.id,
                                                                task_id=attendance_task_type.id,
                                                                user_id=teacher.user_id,
                                                                location_id=location_id).first()
    if not filtered_attendance_tasks:
        add_attendance = TasksStatistics(calendar_year=calendar_year.id, calendar_month=calendar_month.id,
                                         calendar_day=calendar_day.id, user_id=teacher.user_id,
                                         task_id=attendance_task_type.id,
                                         in_progress_tasks=tasks['attendance'], location_id=location_id)
        db.session.add(add_attendance)
        db.session.commit()
    filtered_task_daily_statistics = TaskDailyStatistics.query.filter(
        TaskDailyStatistics.calendar_day == calendar_day.id, TaskDailyStatistics.user_id == teacher.user_id,
        TaskDailyStatistics.location_id == location_id).first()

    if not filtered_task_daily_statistics:
        overall_tasks = tasks['excuses'] + tasks['attendance'] + tasks['lesson_plan']
        add_daily_statistic = TaskDailyStatistics(user_id=teacher.user_id, calendar_year=calendar_year.id,
                                                  calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                                  in_progress_tasks=overall_tasks, location_id=location_id)
        db.session.add(add_daily_statistic)
        db.session.commit()

