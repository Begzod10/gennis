from app import app, request, db, jsonify

from datetime import datetime
from backend.models.models import Teachers, Users
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import api, find_calendar_date
from backend.tasks.teacher.functions.statistics.create_tasks.func import change_teacher_tasks
from backend.tasks.teacher.functions.statistics.update_tasks.func import update_teacher_tasks
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/teacher_tasks_lesson_plan/<int:location_id>/<int:group_id>', methods=["POST", "GET"])
# @jwt_required()
def teacher_tasks_lesson_plan(location_id, group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()

    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    # user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    teacher = Teachers.query.filter(Teachers.user_id == 3).first()
    # teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    task_type = Tasks.query.filter_by(name='lesson_plan', role='teacher').first()
    change_teacher_tasks(teacher, location_id)
    update_teacher_tasks(teacher, location_id)
    if request.method == "GET":
        lesson_plans_json = []
        completed_tasks = []
        lesson_plans = LessonPlan.query.filter(LessonPlan.date > date_strptime,
                                               LessonPlan.teacher_id == teacher.id,
                                               LessonPlan.group_id == group_id).order_by(LessonPlan.date).first()
        completed = LessonPlan.query.filter_by(updated_date=date_strptime).all()
        print(lesson_plans)
        # for lesson_plan in lesson_plans:
        #     lesson_plans_json.append(lesson_plan.convert_json())
        #
        # for cm in completed:
        #     completed_tasks.append(cm.convert_json())

        return jsonify({"lesson_plans": lesson_plans_json})
    if request.method == "POST":
        data = request.get_json()
        id = data.get('id')
        main_lesson = data.get('main_lesson')
        homework = data.get('homework')
        objective = data.get('objective')
        assessment = data.get('assessment')
        activities = data.get('activities')
        resources = data.get('resources')
        LessonPlan.query.filter(LessonPlan.id == id).update({
            'main_lesson': main_lesson,
            'homework': homework,
            'objective': objective,
            'assessment': assessment,
            'activities': activities,
            'resources': resources,
            'updated_date': date_strptime
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
        return jsonify({"msg": "Lesson Plan muvaffaqqiyatli qo'shildi", "id": id})
