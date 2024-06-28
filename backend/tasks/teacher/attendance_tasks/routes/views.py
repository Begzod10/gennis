from app import app, request, db, jsonify
from backend.models.models import Users, Students, AttendanceDays, Teachers
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.functions.utils import api, find_calendar_date
from datetime import datetime
from backend.tasks.teacher.functions.statistics.update_tasks.func import update_teacher_tasks
from backend.tasks.teacher.functions.statistics.create_tasks.func import change_teacher_tasks
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/teacher_tasks_attendance/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def teacher_tasks_attendance(location_id):
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    task_type = Tasks.query.filter_by(name='attendance', role='teacher').first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()

    if request.method == "GET":
        change_teacher_tasks(teacher, location_id)
        update_teacher_tasks(teacher, location_id)
        student_ids = []
        students_list = []
        completed_tasks = []
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

        teacher_attendances_completed = AttendanceDays.query.filter(AttendanceDays.teacher_id == teacher.id,
                                                                    AttendanceDays.calling_status == True,
                                                                    AttendanceDays.calling_date == date_strptime,
                                                                    AttendanceDays.location_id == location_id).all()

        for teacher_attendance in teacher_attendances_completed:
            student_ids.append(teacher_attendance.student_id)
        students_completed = Students.query.filter(Students.id.in_(student_ids)).all()

        for student in students_completed:
            info = {
                'student_id': student.id,
                'user': student.user.convert_json(),
                'subjects': [subject.name for subject in student.subject]
            }
            completed_tasks.append(info)

        return jsonify({"students_list": students_list, "completed_tasks": completed_tasks})
    if request.method == "POST":
        data = request.get_json()
        student_id = data.get('student_id')
        teacher_attendances = AttendanceDays.query.filter(AttendanceDays.teacher_id == teacher.id,
                                                          AttendanceDays.calling_status == False,
                                                          AttendanceDays.location_id == location_id,
                                                          AttendanceDays.student_id == student_id).all()
        for teacher_attendance in teacher_attendances:
            AttendanceDays.query.filter_by(id=teacher_attendance.id).update({
                'calling_status': True,
                'calling_date': date_strptime
            })
            db.session.commit()
        task_statistic = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, user_id=teacher.user_id,
                                                         task_id=task_type.id, location_id=location_id).first()
        task_statistic.completed_tasks += 1
        db.session.commit()
        task_statistic.completed_tasks_percentage = (
                                                            task_statistic.completed_tasks /
                                                            task_statistic.in_progress_tasks) * 100
        db.session.commit()
        daily_task_statistic = TaskDailyStatistics.query.filter_by(calendar_day=calendar_day.id,
                                                                   user_id=teacher.user_id,
                                                                   location_id=location_id).first()
        daily_task_statistic.completed_tasks += 1
        db.session.commit()
        daily_task_statistic.completed_tasks_percentage = (
                                                                  daily_task_statistic.completed_tasks /
                                                                  daily_task_statistic.in_progress_tasks) * 100
        db.session.commit()

        return jsonify({"student": {
            'msg': "Komment belgilandi",
            'id': student_id
        }})