from app import app, api, request, db, jsonify

import requests
from datetime import datetime
from backend.models.models import Users, Students, AttendanceDays
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import api, find_calendar_date


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
