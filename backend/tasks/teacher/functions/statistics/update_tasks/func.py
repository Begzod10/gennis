from app import app, api, request, db
from datetime import datetime
from backend.models.models import Users, Students, AttendanceDays
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import find_calendar_date


def update_teacher_tasks(teacher, location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    april = datetime.strptime("2024-03", "%Y-%m")
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")

    excuses_task_type = Tasks.query.filter_by(name='excuses', role='teacher').first()

    attendance_task_type = Tasks.query.filter_by(name='attendance', role='teacher').first()
    lesson_plan_task_type = Tasks.query.filter_by(name='lesson_plan', role='teacher').first()

    student_ids = []
    attendance_tasks = []

    for group in teacher.group:
        for student in group.student:
            student_ids.append(student.id)

    excuses_task_count = 0
    students = db.session.query(Students).join(Students.user).filter(Users.balance < 0
                                                                     ).filter(
        Students.deleted_from_register == None, Students.id.in_(student_ids)).all()

    for student in students:
        if student.excuses:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                        -1].to_date <= date_strptime:
                        excuses_task_count += 1
            else:
                excuses_task_count += 1
        else:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    excuses_task_count += 1
            else:
                excuses_task_count += 1

    teacher_attendances = AttendanceDays.query.filter(AttendanceDays.teacher_id == teacher.id,
                                                      AttendanceDays.calling_status == False,
                                                      AttendanceDays.location_id == location_id).all()

    for teacher_attendance in teacher_attendances:
        attendance_tasks.append(teacher_attendance.student_id)
    unique_tasks = []
    for task in attendance_tasks:
        if not task in unique_tasks:
            unique_tasks.append(task)
    lesson_plan = LessonPlan.query.filter(LessonPlan.date > date_strptime, LessonPlan.teacher_id == teacher.id).count()

    excuses_statistics = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, user_id=teacher.user_id,
                                                         task_id=excuses_task_type.id).first()
    if excuses_statistics.in_progress_tasks < excuses_task_count:
        excuses_statistics.in_progress_tasks = excuses_task_count
        db.session.commit()
        excuses_statistics.completed_tasks_percentage = (
                                                                excuses_statistics.completed_tasks
                                                                / excuses_statistics.in_progress_tasks) * 100
        db.session.commit()

    attendance_statistics = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, user_id=teacher.user_id,
                                                            task_id=attendance_task_type.id).first()

    if attendance_statistics.in_progress_tasks < len(unique_tasks):
        attendance_statistics.in_progress_tasks = len(unique_tasks)
        db.session.commit()
        attendance_statistics.completed_tasks_percentage = (
                                                                   attendance_statistics.completed_tasks
                                                                   / attendance_statistics.in_progress_tasks) * 100
        db.session.commit()

    lesson_plan_statistics = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, user_id=teacher.user_id,
                                                             task_id=lesson_plan_task_type.id).first()

    if lesson_plan_statistics.in_progress_tasks < lesson_plan:
        lesson_plan_statistics.in_progress_tasks = lesson_plan
        db.session.commit()
        lesson_plan_statistics.completed_tasks_percentage = (
                                                                    lesson_plan_statistics.completed_tasks
                                                                    / lesson_plan_statistics.in_progress_tasks) * 100
        db.session.commit()

    task_daily_statistics = TaskDailyStatistics.query.filter_by(user_id=teacher.user_id, calendar_day=calendar_day.id,
                                                                location_id=location_id).first()
    task_daily_statistics.in_progress_tasks = excuses_statistics.in_progress_tasks + \
                                              attendance_statistics.in_progress_tasks + \
                                              lesson_plan_statistics.in_progress_tasks
    db.session.commit()
    task_daily_statistics.completed_tasks_percentage = (
                                                               task_daily_statistics.completed_tasks /
                                                               task_daily_statistics.in_progress_tasks) * 100
    db.session.commit()
