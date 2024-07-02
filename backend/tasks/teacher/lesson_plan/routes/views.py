from app import app, request, db, jsonify

from datetime import datetime

from backend.group.models import Groups
from backend.models.models import Teachers, Users
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import LessonPlan
from backend.functions.utils import api, find_calendar_date
from backend.tasks.teacher.functions.statistics.create_tasks.func import change_teacher_tasks
from backend.tasks.teacher.functions.statistics.update_tasks.func import update_teacher_tasks
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.teacher.models import LessonPlanStudents
from backend.time_table.models import Week

from backend.functions.utils import find_calendar_date, get_json_field


# @app.route(f'{api}/teacher_tasks_lesson_plan/<int:location_id>', defaults={"group_id": None}, methods=['POST', "GET"])
@app.route(f'{api}/teacher_tasks_lesson_plan/<int:location_id>', methods=["GET", "POST"])
@jwt_required()
def teacher_tasks_lesson_plan(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    # teacher = Teachers.query.filter(Teachers.user_id == 3).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    task_type = Tasks.query.filter_by(name='lesson_plan', role='teacher').first()
    change_teacher_tasks(teacher, location_id)
    update_teacher_tasks(teacher, location_id)
    if request.method == "GET":
        lesson_plans_json = []
        completed_tasks = []

        day_name = today.strftime("%A")
        chosen_num = Week.query.filter(Week.location_id == location_id, Week.eng_name == day_name).first()
        group_ids = []

        lesson_plans = LessonPlan.query.filter(LessonPlan.date >= date_strptime,
                                               LessonPlan.teacher_id == teacher.id).order_by(LessonPlan.date).all()
        check_groups = Groups.query.filter(Groups.id.in_([lesson_plan.group_id for lesson_plan in lesson_plans])).all()

        groups = []

        for group in check_groups:
            week_orders = []
            for time_table in group.time_table:
                week_orders.append(time_table.week.order)
            greater_numbers = [num for num in week_orders if num > chosen_num.order]
            if greater_numbers:
                next_week_day = Week.query.filter(Week.location_id == location_id,
                                                  Week.order == min(greater_numbers)).first()
                for lesson_plan in lesson_plans:
                    if lesson_plan.date.strftime("%A") == day_name and lesson_plan.main_lesson == None:
                        group_ids.append(lesson_plan.group_id)
                        info = {
                            'id': group.id,
                            'name': group.name,
                            'student_count': len(group.student),
                            'price': group.price,
                            'lesson_plan_id': lesson_plan.id,
                            'students': [{'id': student.id, 'user': student.user.convert_json()} for student in
                                         group.student]
                        }
                        groups.append(info)
                    else:
                        if lesson_plan.date.strftime("%A") == next_week_day.eng_name:
                            group_ids.append(lesson_plan.group_id)
                            info = {
                                'id': group.id,
                                'name': group.name,
                                'student_count': len(group.student),
                                'price': group.price,
                                'lesson_plan_id': lesson_plan.id,
                                'students': [{'id': student.id, 'user': student.user.convert_json()} for student in
                                             group.student]
                            }
                            groups.append(info)
            else:
                for lesson_plan in lesson_plans:
                    if lesson_plan.date.strftime("%A") == day_name and lesson_plan.main_lesson == None:
                        group_ids.append(lesson_plan.group_id)
                        info = {
                            'id': group.id,
                            'name': group.name,
                            'student_count': len(group.student),
                            'price': group.price,
                            'lesson_plan_id': lesson_plan.id,
                            'students': [{'id': student.id, 'user': student.user.convert_json()} for student in
                                         group.student]
                        }
                        groups.append(info)
        completed = LessonPlan.query.filter_by(updated_date=date_strptime, teacher_id=teacher.id).all()
        for cm in completed:
            completed_tasks.append(cm.convert_json())
        return jsonify({"lesson_plans": groups, 'completed_tasks': completed_tasks})


    if request.method == "POST":
        plan_id = get_json_field('id')
        objective = get_json_field('objective')
        main_lesson = get_json_field('main_lesson')
        homework = get_json_field('homework')
        assessment = get_json_field('assessment')
        activities = get_json_field('activities')
        student_id_list = get_json_field("students")
        resources = get_json_field("resources")
        lesson_plan_get = LessonPlan.query.filter(LessonPlan.id == plan_id).first()
        lesson_plan_get.objective = objective
        lesson_plan_get.homework = homework
        lesson_plan_get.assessment = assessment
        lesson_plan_get.main_lesson = main_lesson
        lesson_plan_get.activities = activities
        lesson_plan_get.resources = resources
        db.session.commit()
        for student in student_id_list:
            info = {
                "comment": student['comment'],
                "student_id": student['student']['id'],
                "lesson_plan_id": plan_id
            }
            student_add = LessonPlanStudents.query.filter(LessonPlanStudents.lesson_plan_id == plan_id,
                                                          LessonPlanStudents.student_id == student['student'][
                                                              'id']).first()
            if not student_add:
                student_add = LessonPlanStudents(**info)
                student_add.add()
            else:
                student_add.comment = student['comment']
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
        return jsonify({"msg": "Lesson Plan muvaffaqqiyatli qo'shildi", "id": id}) #id uzgaruvchini togirlash kerak,lesson plan qushilvotti
