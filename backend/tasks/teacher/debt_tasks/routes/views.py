from app import app, request, db, jsonify
from datetime import datetime
from backend.models.models import Users, Students, Teachers, StudentExcuses
from backend.student.functions import get_student_info, get_completed_student_info
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.functions.utils import api, find_calendar_date
from backend.tasks.teacher.functions.statistics.update_tasks.func import update_teacher_tasks
from backend.tasks.teacher.functions.statistics.create_tasks.func import change_teacher_tasks
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/teacher_tasks_debt2/<int:location_id>', methods=["GET", "POST"])
@jwt_required()
def teacher_tasks_debt(location_id):
    today = datetime.today()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    april = datetime.strptime("2024-03", "%Y-%m")
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    change_teacher_tasks(teacher, location_id)
    update_teacher_tasks(teacher, location_id)
    student_ids = []
    for group in teacher.group:
        for student in group.student:
            student_ids.append(student.id)
    students = db.session.query(Students).join(Students.user).filter(Users.balance < 0
                                                                     ).filter(
        Students.deleted_from_register == None, Students.id.in_(student_ids)).all()
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
        to_date = data.get('data')
        user_id = data.get('id')

        print(data)
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
                                                             task_statistics.completed_tasks /
                                                             task_statistics.in_progress_tasks) * 100
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
                                                   overall_complete / tasks_daily_statistics.in_progress_tasks)
                                           * 100 if tasks_daily_statistics.in_progress_tasks > 0 else 0)

        tasks_daily_statistics.completed_tasks = overall_complete
        tasks_daily_statistics.completed_tasks_percentage = completed_tasks_percentage
        db.session.commit()

        return jsonify({"student": {
            'msg': "Komment belgilandi",
            'id': student.user.id
        }})
