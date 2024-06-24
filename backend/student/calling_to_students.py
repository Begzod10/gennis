from app import app, request, jsonify, db, extract
from backend.models.models import Students, StudentCallingInfo, Users, StudentExcuses
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.functions.utils import api, find_calendar_date
from backend.student.functions import get_student_info, get_completed_student_info
from backend.models.models import Locations
from backend.lead.models import *
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import CalendarDay
from sqlalchemy import asc


# @app.route(f'{api}/new_students_calling', defaults={"location_id": None}, methods=["POST", "GET"])


@app.route(f'{api}/new_students_calling/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def new_students_calling(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    students = Students.query.filter(Students.group == None).join(Students.user).filter(
        Users.location_id == location_id, Users.student != None,
        Students.subject != None,
        Students.deleted_from_register == None).all()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    students_info = []
    completed_tasks = []
    for student in students:
        phone = next((phones.phone for phones in student.user.phone if phones.personal), None)
        subjects = [subject.name for subject in student.subject]
        shift = '1-smen' if student.morning_shift else '2-smen' if student.night_shift else 'shift unknown'
        info = {
            'id': student.id,
            'name': student.user.name,
            'surname': student.user.surname,
            'phone': phone,
            'subject': subjects,
            'registered_date': f'{student.user.year.date.year}-{student.user.month.date.month}-{student.user.day.date.day}',
            'shift': shift,
            'history': [],
            'status': ''
        }

        if student.student_calling_info:

            for calling_info in student.student_calling_info:
                calling_date = {
                    'id': calling_info.id,
                    'comment': calling_info.comment,
                    'day': f'{calling_info.day.year}-{calling_info.day.month}-{calling_info.day.day}'
                }
                info['history'].append(calling_date)

            if student.student_calling_info[-1].date <= date_strptime:
                if student.student_calling_info[-1].date.month == today.month:
                    index = int(today.day) - int(student.student_calling_info[-1].date.day)
                    index = max(0, min(index, 1))
                else:
                    index = 1
                info['status'] = ['yellow', 'red'][index]
                students_info.append(info)
            added_date = f'{student.student_calling_info[-1].day.year}-{student.student_calling_info[-1].day.month}-{student.student_calling_info[-1].day.day}'
            added_date_strptime = datetime.strptime(added_date, "%Y-%m-%d")
            if added_date_strptime == date_strptime and student.student_calling_info[-1].date > date_strptime:
                info['status'] = 'yellow'
                completed_tasks.append(info)
        else:
            info['status'] = 'red'
            students_info.append(info)

    if request.method == "GET":
        change_statistics(location_id)
        return jsonify({
            "students": students_info,
            'completed_tasks': completed_tasks
        })

    if request.method == "POST":
        info = request.get_json()
        today = datetime.today()
        date = datetime.strptime(info['date'], "%Y-%m-%d")
        add_info = StudentCallingInfo(student_id=info['id'], comment=info['comment'], day=today, date=date)
        add_info.add()
        change_statistics(location_id)
        student = Students.query.filter(Students.id == info['id']).first()
        phone = next((phones.phone for phones in student.user.phone if phones.personal), None)
        subjects = [subject.name for subject in student.subject]
        shift = '1-smen' if student.morning_shift else '2-smen' if student.night_shift else 'shift unknown'
        info = {
            'id': student.id,
            'name': student.user.name,
            'surname': student.user.surname,
            'number': phone,
            'registered_date': f'{student.user.year.date.year}-{student.user.month.date.month}-{student.user.day.date.day}',
            'shift': shift,
            'subject': subjects,
            'history': [],
            'status': ''
        }

        if student.student_calling_info:
            if student.student_calling_info[-1].date <= date_strptime:
                if student.student_calling_info[-1].date.month == today.month:
                    index = int(today.day) - int(student.student_calling_info[-1].date.day)
                    index = max(0, min(index, 2))
                else:
                    index = 2
                info['status'] = ['yellow', 'red'][index]
                for calling_info in student.student_calling_info:
                    calling_date = {
                        'id': calling_info.id,
                        'comment': calling_info.comment,
                        'day': f'{calling_info.day.year}-{calling_info.day.month}-{calling_info.day.day}'
                    }
                    info['history'].append(calling_date)

                return jsonify({"student": info})

        task_type = Tasks.query.filter(Tasks.name == 'new_students').first()

        task_statistics = TasksStatistics.query.filter(
            TasksStatistics.task_id == task_type.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).first()
        students = Students.query.join(Students.user).filter(
            Users.location_id == location_id).all()
        students_callings = StudentCallingInfo.query.filter(
            StudentCallingInfo.student_id.in_([st_id.id for st_id in students]),
            extract('day', StudentCallingInfo.day) == int(calendar_day.date.strftime("%d"))).count()

        task_statistics.completed_tasks = students_callings
        db.session.commit()

        task_statistics.completed_tasks_percentage = (
                                                             task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
        db.session.commit()

        overall_location_statistics = TasksStatistics.query.filter(
            TasksStatistics.user_id == user.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).all()

        tasks_daily_statistics = TaskDailyStatistics.query.filter(
            TaskDailyStatistics.user_id == user.id,
            TaskDailyStatistics.location_id == location_id,
            TaskDailyStatistics.calendar_day == calendar_day.id
        ).first()
        call_overall = 0
        for overall in overall_location_statistics:
            call_overall += overall.completed_tasks
        completed_tasks_percentage = (
                                             call_overall / tasks_daily_statistics.in_progress_tasks) * 100 if tasks_daily_statistics.in_progress_tasks > 0 else 0

        tasks_daily_statistics.completed_tasks = call_overall
        tasks_daily_statistics.completed_tasks_percentage = completed_tasks_percentage
        db.session.commit()
        return jsonify({'msg': "Komment belgilandi", "student": {'id': student.id}})


@app.route(f'{api}/student_in_debts', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/student_in_debts/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def student_in_debts(location_id):
    today = datetime.today()
    # date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    april = datetime.strptime("2024-03", "%Y-%m")
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    completed_tasks = []

    if request.method == "GET":
        change_statistics(location_id)
        update_tasks_in_progress(location_id)
        students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(asc(Users.balance)).limit(100).all()
        payments_list = []
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
        return jsonify({"students": payments_list, 'completed_tasks': completed_tasks})

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
        change_statistics(location_id)

        task_type = Tasks.query.filter(Tasks.name == 'excuses').first()
        task_statistics = TasksStatistics.query.filter(
            TasksStatistics.task_id == task_type.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).first()
        students = Students.query.filter(Students.group != None).join(Students.user).filter(
            Users.location_id == location_id).all()

        students_excuses = StudentExcuses.query.filter(StudentExcuses.student_id.in_([st_id.id for st_id in students]),
                                                       StudentExcuses.added_date == calendar_day.date).count()

        task_statistics.completed_tasks = students_excuses
        db.session.commit()

        task_statistics.completed_tasks_percentage = (
                                                             task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
        db.session.commit()
        overall_location_statistics = TasksStatistics.query.filter(
            TasksStatistics.user_id == user.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).all()
        tasks_daily_statistics = TaskDailyStatistics.query.filter(
            TaskDailyStatistics.user_id == user.id,
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


@app.route(f'{api}/daily_statistics', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/daily_statistics/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def daily_statistics(location_id):
    date = request.get_json()
    date_strptime = datetime.strptime(date, "%Y-%m-%d")
    day = CalendarDay.query.filter(CalendarDay.date == date_strptime).first()
    if day:
        daily_statistics = TaskDailyStatistics.query.filter(TaskDailyStatistics.calendar_day == day.id,
                                                            TaskDailyStatistics.location_id == location_id).order_by(
            TaskDailyStatistics.id).first()
        if daily_statistics:

            info = {
                'id': daily_statistics.id,
                'in_progress_tasks': daily_statistics.in_progress_tasks,
                'completed_tasks': daily_statistics.completed_tasks,
                'completed_tasks_percentage': daily_statistics.completed_tasks_percentage,
                'date': f'{daily_statistics.year.date.year}-{daily_statistics.month.date.month}-{daily_statistics.day.date.day}'
            }

            return jsonify({
                'info': info
            })
        else:
            return jsonify({
                'status': "Bu kunda statistika yo'q",
                'info': ''
            })
    else:
        return jsonify({
            'status': "Bu kunda statistika yo'q",
            'info': ''
        })


def add_tasks():
    tasks = ['excuses', 'new_students', 'leads']
    for task in tasks:
        filtered_task = Tasks.query.filter(Tasks.name == task).first()
        if not filtered_task:
            add = Tasks(name=task)
            db.session.add(add)
            db.session.commit()


def change_statistics(location_id):
    add_tasks()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    april = datetime.strptime("2024-03", "%Y-%m")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    location = Locations.query.filter(Locations.id == location_id).first()
    locations_info = {
        location.id: {
            'excuses': 0,
            'new_students': 0,
            'leads': 0
        }
    }
    excuses_students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                             Users.location_id == location.id
                                                                             ).filter(
        Students.deleted_from_register == None).order_by(asc(Users.balance)).limit(100).all()
    for student in excuses_students:
        loc_id = student.user.location_id
        if loc_id:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:

                    if student.excuses:
                        if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                            -1].to_date <= date_strptime:
                            locations_info[loc_id]['excuses'] += 1
                    else:
                        locations_info[loc_id]['excuses'] += 1
            else:
                if student.excuses:
                    if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                        -1].to_date <= date_strptime:
                        locations_info[loc_id]['excuses'] += 1
                else:
                    locations_info[loc_id]['excuses'] += 1

    new_students = Students.query.filter(Students.group == None).join(Students.user).filter(
        Users.student != None,
        Students.subject != None,
        Students.deleted_from_register == None, Users.location_id == location.id).all()

    for student in new_students:
        loc_id = student.user.location_id

        if loc_id:

            if student.student_calling_info:
                if student.student_calling_info[-1].date <= date_strptime:
                    locations_info[loc_id]['new_students'] += 1
            else:
                locations_info[loc_id]['new_students'] += 1

    leads = Lead.query.filter(Lead.deleted == False, Lead.location_id == location.id).all()
    for lead in leads:
        loc_id = lead.location_id
        if loc_id:
            if lead.infos:
                if lead.infos[-1].day <= date_strptime:
                    locations_info[loc_id]['leads'] += 1
            else:
                locations_info[loc_id]['leads'] += 1
    task_excuses = Tasks.query.filter(Tasks.name == "excuses").first()
    task_leads = Tasks.query.filter(Tasks.name == 'leads').first()
    task_new_students = Tasks.query.filter(Tasks.name == 'new_students').first()
    if user.role_info.type_role == "admin":
        for loc_id, counts in locations_info.items():
            filtered_daily_statistics = TaskDailyStatistics.query.filter(
                TaskDailyStatistics.location_id == loc_id,
                TaskDailyStatistics.calendar_day == calendar_day.id,
                TaskDailyStatistics.user_id == user.id
            ).first()

            if not filtered_daily_statistics:
                overall_tasks = counts['excuses'] + counts['leads'] + counts['new_students']
                add_daily_statistics = TaskDailyStatistics(
                    user_id=user.id, calendar_year=calendar_year.id,
                    calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                    in_progress_tasks=overall_tasks, location_id=loc_id
                )
                db.session.add(add_daily_statistics)
                db.session.commit()

            for task, count in [(task_excuses, counts['excuses']), (task_leads, counts['leads']),
                                (task_new_students, counts['new_students'])]:
                filtered_task_stat = TasksStatistics.query.filter(
                    TasksStatistics.task_id == task.id,
                    TasksStatistics.location_id == loc_id,
                    TasksStatistics.calendar_day == calendar_day.id
                ).first()
                if not filtered_task_stat:
                    add_task_stat = TasksStatistics(
                        task_id=task.id, calendar_year=calendar_year.id,
                        calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                        location_id=loc_id, user_id=user.id, in_progress_tasks=count
                    )
                    db.session.add(add_task_stat)
                    db.session.commit()


def update_tasks_in_progress(location_id):
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    april = datetime.strptime("2024-03", "%Y-%m")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    task_excuses = Tasks.query.filter_by(name='excuses').first()
    task_new_students = Tasks.query.filter_by(name='new_students').first()
    task_leads = Tasks.query.filter_by(name='leads').first()
    task_statistic_excuses = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, task_id=task_excuses.id,
                                                             location_id=location_id).first()

    task_statistic_new_students = TasksStatistics.query.filter_by(calendar_day=calendar_day.id,
                                                                  task_id=task_new_students.id,
                                                                  location_id=location_id).first()
    task_statistic_leads = TasksStatistics.query.filter_by(calendar_day=calendar_day.id, task_id=task_leads.id,
                                                           location_id=location_id).first()
    if task_statistic_excuses:
        excuses_students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                                 Users.location_id == location_id
                                                                                 ).filter(
            Students.deleted_from_register == None).order_by(
            asc(Users.balance)).limit(100).all()
        tasks_count = 0
        for student in excuses_students:
            if student.excuses:
                if student.deleted_from_group:
                    if student.deleted_from_group[-1].day.month.date >= april:
                        if student.excuses[-1].reason == "tel ko'tarmadi" or student.excuses[
                            -1].to_date <= date_strptime:
                            tasks_count += 1
                else:
                    tasks_count += 1
            else:
                if student.deleted_from_group:
                    if student.deleted_from_group[-1].day.month.date >= april:
                        tasks_count += 1
                else:
                    tasks_count += 1
    if int(task_statistic_excuses.in_progress_tasks) < tasks_count:
        task_statistic_excuses.in_progress_tasks = tasks_count
        db.session.commit()
        percentage = (
                             task_statistic_excuses.completed_tasks / task_statistic_excuses.in_progress_tasks) * 100 if task_statistic_excuses.in_progress_tasks > 0 else 0
        task_statistic_excuses.completed_tasks_percentage = percentage
        db.session.commit()
        daily_task = TaskDailyStatistics.query.filter_by(location_id=location_id,
                                                         calendar_day=calendar_day.id).first()
        if daily_task:
            overall_tasks = tasks_count + task_statistic_new_students.in_progress_tasks + task_statistic_leads.in_progress_tasks
            daily_task.in_progress_tasks = overall_tasks
            daily_task.completed_tasks_percentage = (
                                                            daily_task.completed_tasks / overall_tasks) * 100 if overall_tasks > 0 else 0
            db.session.commit()
