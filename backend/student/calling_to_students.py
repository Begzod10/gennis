from pprint import pprint

from app import app, api, request, jsonify, db, contains_eager
from backend.models.models import Students, StudentCallingInfo, Users, StudentExcuses
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.functions.utils import get_json_field, api, find_calendar_date

from backend.student.functions import get_student_info
from backend.models.models import Locations
from backend.lead.models import *
from backend.tasks.models import Tasks, TasksStatistics, TaskDailyStatistics
from backend.models.models import CalendarDay, CalendarYear, CalendarMonth


@app.route(f'{api}/new_students_calling', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/new_students_calling/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def new_students_calling(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    location_id = user.location_id if not location_id else location_id
    students = Students.query.filter(Students.group == None).join(Students.user).filter(
        Users.location_id == location_id).all()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    students_info = []

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
                    index = max(0, min(index, 2))
                else:
                    index = 2
                info['status'] = ['green', 'yellow', 'red'][index]
                students_info.append(info)
        else:
            info['status'] = 'red'
            students_info.append(info)

    if request.method == "GET":
        change_statistics()
        return jsonify({"students": students_info})

    if request.method == "POST":
        info = request.get_json()
        today = datetime.today()
        date = datetime.strptime(info['date'], "%Y-%m-%d")
        add_info = StudentCallingInfo(student_id=info['id'], comment=info['comment'], day=today, date=date)
        add_info.add()
        change_statistics()
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
                info['status'] = ['green', 'yellow', 'red'][index]
                for calling_info in student.student_calling_info:
                    calling_date = {
                        'id': calling_info.id,
                        'comment': calling_info.comment,
                        'day': f'{calling_info.day.year}-{calling_info.day.month}-{calling_info.day.day}'
                    }
                    info['history'].append(calling_date)

                return jsonify({"student": info})

        task_type = Tasks.query.filter(Tasks.name == 'new_students').first()
        task_statistics = TasksStatistics.query.filter(TasksStatistics.task_id == task_type.id,
                                                       TasksStatistics.calendar_day == calendar_day.id,
                                                       TasksStatistics.location_id == location_id).first()
        TasksStatistics.query.filter(TasksStatistics.id == task_statistics.id).update({
            'completed_tasks': task_statistics.completed_tasks + 1,
        })
        db.session.commit()
        updated_task_statistics = TasksStatistics.query.filter(TasksStatistics.id == task_statistics.id).first()
        TasksStatistics.query.filter(TasksStatistics.id == updated_task_statistics.id).update({
            'completed_tasks_percentage': (task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
        })
        db.session.commit()
        overall_location_statistics = TasksStatistics.query.filter(
            TasksStatistics.user_id == user.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == task_statistics.location_id).all()
        # percentage_tasks = sum(overall.completed_tasks_percentage for overall in overall_location_statistics) / len(
        #     overall_location_statistics)
        tasks_daily_statistics = TaskDailyStatistics.query.filter(TaskDailyStatistics.user_id == user.id,
                                                                  TaskDailyStatistics.location_id == updated_task_statistics.location_id,
                                                                  TaskDailyStatistics.calendar_day == calendar_day.id).first()
        percentage_tasks = 0
        completed_tasks = 0
        for overall_location_st in overall_location_statistics:
            completed_tasks += overall_location_st.completed_tasks
            percentage_tasks += overall_location_st.completed_tasks_percentage
        if completed_tasks == 0:
            completed_tasks_percentage = 0
        else:
            completed_tasks_percentage = (completed_tasks / tasks_daily_statistics.in_progress_tasks) * 100
        completed_tasks = sum(overall.completed_tasks for overall in overall_location_statistics)
        TaskDailyStatistics.query.filter(TaskDailyStatistics.user_id == user.id,
                                         TaskDailyStatistics.location_id == updated_task_statistics.location_id,
                                         TaskDailyStatistics.calendar_day == calendar_day.id).update({
            'completed_tasks': completed_tasks,
            'completed_tasks_percentage': completed_tasks_percentage
        })
        db.session.commit()

        return jsonify({"student": {'id': student.id}})


@app.route(f'{api}/student_in_debts', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/student_in_debts/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def student_in_debts(location_id):
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    location_id = user.location_id if not location_id else location_id

    if request.method == "GET":
        change_statistics()
        students = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
            Users.balance < 0, Users.location_id == location_id).order_by(Users.balance).all()

        payments_list = []
        for student in students:
            if get_student_info(student) != None:
                payments_list.append(get_student_info(student))

        return jsonify({"students": payments_list})

    if request.method == "POST":
        data = request.get_json()
        reason = data.get('comment')
        select = data.get('select')
        to_date = data.get('date')
        user_id = data.get('id')

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d")

        student = Students.query.filter(Students.user_id == user_id).first()
        new_excuse = StudentExcuses(reason=reason if select == "yes" else "tel ko'tarmadi",
                                    to_date=to_date if select == "yes" else None, added_date=calendar_day.date,
                                    student_id=student.id)
        db.session.add(new_excuse)
        db.session.commit()

        change_statistics()
        if get_student_info(student) == None:
            task_type = Tasks.query.filter(Tasks.name == 'excuses').first()
            task_statistics = TasksStatistics.query.filter(TasksStatistics.task_id == task_type.id,
                                                           TasksStatistics.calendar_day == calendar_day.id,
                                                           TasksStatistics.location_id == location_id).first()
            TasksStatistics.query.filter(TasksStatistics.id == task_statistics.id).update({
                'completed_tasks': task_statistics.completed_tasks + 1,
            })
            db.session.commit()
            updated_task_statistics = TasksStatistics.query.filter(TasksStatistics.id == task_statistics.id).first()
            TasksStatistics.query.filter(TasksStatistics.id == updated_task_statistics.id).update({
                'completed_tasks_percentage': (
                                                      task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
            })
            db.session.commit()
            overall_location_statistics = TasksStatistics.query.filter(
                TasksStatistics.user_id == user.id,
                TasksStatistics.calendar_day == calendar_day.id,
                TasksStatistics.location_id == task_statistics.location_id).all()
            percentage_tasks = 0
            completed_tasks = 0
            for overall_location_st in overall_location_statistics:
                completed_tasks += overall_location_st.completed_tasks
                percentage_tasks += overall_location_st.completed_tasks_percentage
            tasks_daily_statistics = TaskDailyStatistics.query.filter(TaskDailyStatistics.user_id == user.id,
                                                                      TaskDailyStatistics.location_id == updated_task_statistics.location_id,
                                                                      TaskDailyStatistics.calendar_day == calendar_day.id).first()
            if completed_tasks == 0:
                completed_tasks_percentage = 0
            else:
                completed_tasks_percentage = (completed_tasks / tasks_daily_statistics.in_progress_tasks) * 100
            TaskDailyStatistics.query.filter(TaskDailyStatistics.user_id == user.id,
                                             TaskDailyStatistics.location_id == updated_task_statistics.location_id,
                                             TaskDailyStatistics.calendar_day == calendar_day.id).update({
                'completed_tasks': completed_tasks,
                'completed_tasks_percentage': completed_tasks_percentage
            })
            db.session.commit()
            return jsonify({"student": {
                'id': student.user.id
            }})
        else:
            return jsonify({"student": get_student_info(student)})


@app.route(f'{api}/daily_statistics', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/daily_statistics/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def daily_statistics(location_id):
    date = request.get_json()
    date_strptime = datetime.strptime(date, "%Y-%m-%d")
    day = CalendarDay.query.filter(CalendarDay.date == date_strptime).first()
    if day:
        daily_statistics = TaskDailyStatistics.query.filter(TaskDailyStatistics.calendar_day == day.id,
                                                            TaskDailyStatistics.location_id == location_id).first()
        if daily_statistics:

            print(daily_statistics)
            info = {
                'id': daily_statistics.id,
                'in_progress_tasks': daily_statistics.in_progress_tasks,
                'completed_tasks': daily_statistics.completed_tasks,
                'completed_tasks_percentage': daily_statistics.completed_tasks_percentage,
                'date': f'{daily_statistics.year.date.year}-{daily_statistics.month.date.month}-{daily_statistics.day.date.day}'
            }
            print(info)
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


def change_statistics():
    add_tasks()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    excuses_students = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
        Users.balance < 0).order_by(Users.balance).all()

    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    locations = Locations.query.all()
    locations_info = []
    for location in locations:
        info = {
            'location': {
                'id': location.id,
                'excuses': 0,
                'new_students': 0,
                'leads': 0
            }
        }
        locations_info.append(info)
    for student in excuses_students:

        for lc in locations_info:
            if int(lc['location']['id']) == int(student.user.location_id):
                if student.excuses:
                    if student.excuses[-1].reason == "tel ko'tarmadi":
                        lc['location']['excuses'] += 1
                    else:
                        if student.excuses[-1].to_date <= date_strptime:
                            lc['location']['excuses'] += 1
                else:
                    lc['location']['excuses'] += 1

    new_students = Students.query.filter(Students.group == None).all()
    for student in new_students:

        for lc in locations_info:

            if int(lc['location']['id']) == int(student.user.location_id):
                if student.student_calling_info:
                    if student.student_calling_info[-1].date <= date_strptime:
                        lc['location']['new_students'] += 1
                else:
                    lc['location']['new_students'] += 1

    leads = Lead.query.filter(Lead.deleted == False).order_by(
        desc(Lead.id)).all()

    for lead in leads:
        for lc in locations_info:
            if int(lc['location']['id']) == int(lead.location_id):
                if lead.deleted == False:
                    if lead.infos:
                        if lead.infos[-1].day <= date_strptime:
                            lc['location']['leads'] += 1
                    else:
                        lc['location']['leads'] += 1

    task_excuses = Tasks.query.filter(Tasks.name == "excuses").first()
    task_leads = Tasks.query.filter(Tasks.name == 'leads').first()
    task_new_students = Tasks.query.filter(Tasks.name == 'new_students').first()

    for location_info in locations_info:
        filtered_daily_statistics = TaskDailyStatistics.query.filter(
            TaskDailyStatistics.location_id == location_info['location']['id'],
            TaskDailyStatistics.calendar_day == calendar_day.id, TaskDailyStatistics.user_id == user.id).first()

        if not filtered_daily_statistics:
            overall_tasks = location_info['location']['excuses'] + location_info['location']['leads'] + \
                            location_info['location']['new_students']
            add_daily_statistics = TaskDailyStatistics(user_id=user.id, calendar_year=calendar_year.id,
                                                       calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                                       in_progress_tasks=overall_tasks,
                                                       location_id=location_info['location']['id'])
            db.session.add(add_daily_statistics)
            db.session.commit()

        filtered_tasks_excuses = TasksStatistics.query.filter(TasksStatistics.task_id == task_excuses.id,
                                                              TasksStatistics.location_id == location_info['location'][
                                                                  'id'],
                                                              TasksStatistics.calendar_day == calendar_day.id).first()
        if not filtered_tasks_excuses:
            add_excuse = TasksStatistics(task_id=task_excuses.id, calendar_year=calendar_year.id,
                                         calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                         location_id=location_info['location']['id'], user_id=user.id,
                                         in_progress_tasks=location_info['location']['excuses'])
            db.session.add(add_excuse)
            db.session.commit()

        filtered_tasks_leads = TasksStatistics.query.filter(TasksStatistics.task_id == task_leads.id,
                                                            TasksStatistics.location_id == location_info['location'][
                                                                'id'],
                                                            TasksStatistics.calendar_day == calendar_day.id).first()
        if not filtered_tasks_leads:
            add_leads = TasksStatistics(task_id=task_leads.id, calendar_year=calendar_year.id,
                                        calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                        location_id=location_info['location']['id'], user_id=user.id,
                                        in_progress_tasks=location_info['location']['leads'])
            db.session.add(add_leads)
            db.session.commit()

        filtered_tasks_new_students = TasksStatistics.query.filter(TasksStatistics.task_id == task_new_students.id,
                                                                   TasksStatistics.location_id ==
                                                                   location_info['location'][
                                                                       'id'],
                                                                   TasksStatistics.calendar_day ==
                                                                   calendar_day.id).first()
        if not filtered_tasks_new_students:
            add_new_students = TasksStatistics(task_id=task_new_students.id, calendar_year=calendar_year.id,
                                               calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                               location_id=location_info['location']['id'], user_id=user.id,
                                               in_progress_tasks=location_info['location']['new_students'])
            db.session.add(add_new_students)
            db.session.commit()
