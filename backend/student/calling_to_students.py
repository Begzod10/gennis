import pprint

from app import app, request, jsonify, db, extract
from backend.models.models import Students, StudentCallingInfo, Users, StudentExcuses
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.functions.utils import api, find_calendar_date
from backend.student.functions import get_student_info, get_completed_student_info, change_statistics, \
    update_all_ratings, update_tasks_in_progress
from backend.models.models import Locations

from backend.lead.functions import get_lead_tasks, get_completed_lead_tasks

from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics, TaskStudents
from backend.models.models import CalendarDay, Lead, DeletedStudents, desc, contains_eager, Teachers
from datetime import datetime
from sqlalchemy import asc
from sqlalchemy.orm import aliased
from sqlalchemy import func, case, and_, or_
import time


@app.route(f'{api}/new_students_calling/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def new_students_calling(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    students = Students.query.join(Users).filter(Users.location_id == location_id, Users.student != None,
                                                 Students.subject != None,
                                                 Students.deleted_from_register == None).order_by(
        desc(Students.id)).all()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    students_info = []
    completed_tasks = []
    for student in students:
        phone = next((phones.phone for phones in student.user.phone if phones.personal), None)
        subjects = [subject.name for subject in student.subject]
        shift = '1-smen' if student.morning_shift else '2-smen' if student.night_shift else 'Hamma vaqt'
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
        task_type = Tasks.query.filter(Tasks.name == 'new_students').first()

        task_statistics = TasksStatistics.query.filter(
            TasksStatistics.task_id == task_type.id,
            TasksStatistics.calendar_day == calendar_day.id,
            TasksStatistics.location_id == location_id
        ).first()
        task_statistics.completed_tasks = len(completed_tasks)
        task_statistics.in_progress_tasks = len(students_info)
        task_statistics.completed_tasks_percentage = round(
            (len(completed_tasks) / (len(completed_tasks) + len(students_info))) * 100)
        db.session.commit()
        update_all_ratings()
        return jsonify({
            "students": students_info,
            'completed_tasks': completed_tasks
        })

    if request.method == "POST":

        student_info = request.get_json()
        today = datetime.today().now()
        date = datetime.strptime(student_info['date'], "%Y-%m-%d")
        if date > calendar_day.date:
            exist_info = StudentCallingInfo.query.filter(StudentCallingInfo.student_id == student_info['id'],
                                                         StudentCallingInfo.day == today).first()
            if not exist_info:
                add_info = StudentCallingInfo(student_id=student_info['id'], comment=student_info['comment'], day=today,
                                              date=date)
                add_info.add()

            completed_tasks = []
            for student in students:
                phone = next((phones.phone for phones in student.user.phone if phones.personal), None)
                subjects = [subject.name for subject in student.subject]
                shift = '1-smen' if student.morning_shift else '2-smen' if student.night_shift else 'Hamma vaqt'
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

            student = Students.query.filter(Students.id == student_info['id']).first()
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
                'status': '',
                "today": False
            }

            if student.student_calling_info:
                if student.student_calling_info[-1].date == date:
                    info['today'] = True
                if student.student_calling_info[-1].date <= date_strptime:
                    if student.student_calling_info[-1].date.month == today.month:
                        index = int(today.day) - int(student.student_calling_info[-1].date.day)
                        index = max(0, min(index, 2))
                    else:
                        index = 2
                    info['today'] = True
                    info['status'] = ["green", 'yellow', 'red'][index]
                    for calling_info in student.student_calling_info:
                        calling_date = {
                            'id': calling_info.id,
                            'comment': calling_info.comment,
                            'day': f'{calling_info.day.year}-{calling_info.day.month}-{calling_info.day.day}'
                        }
                        info['history'].append(calling_date)
                    return jsonify({
                        "student": info,
                    })
            task_type = Tasks.query.filter(Tasks.name == 'new_students').first()

            task_statistics = TasksStatistics.query.filter(
                TasksStatistics.task_id == task_type.id,
                TasksStatistics.calendar_day == calendar_day.id,
                TasksStatistics.location_id == location_id
            ).first()
            task_statistics.completed_tasks = len(completed_tasks)
            task_statistics.in_progress_tasks = len(students_info)

            db.session.commit()
            task_statistics.completed_tasks_percentage = round(
                (len(completed_tasks) / task_statistics.total_tasks) * 100)
            db.session.commit()
            update_all_ratings()
            task_type = Tasks.query.filter(Tasks.name == 'new_students').first()

            task_statistics = TasksStatistics.query.filter(
                TasksStatistics.task_id == task_type.id,
                TasksStatistics.calendar_day == calendar_day.id,
                TasksStatistics.location_id == location_id
            ).first()
            return jsonify({"student": {
                'msg': "Komment belgilandi",
                'id': student.id,
                "info": info,
                "students_num": task_statistics.in_progress_tasks
            }})
        else:
            return jsonify({
                'msg': "Eski sana kiritilgan",

            })
        # return jsonify({'v  ': "Komment belgilandi", "student": {'id': student.id}})


@app.route(f'{api}/search_student_in_task/<int:location_id>', methods=["POST"])
@jwt_required()
def search_student_in_task(location_id):
    data = request.get_json()
    type = data.get('type')
    status = data.get('status')
    text = data.get('text')
    list = []
    if type == 'debtors' and status == False:
        april = datetime.strptime("2024-03", "%Y-%m")
        students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                         or_(Users.name.like('%' + text + '%'),
                                                                             Users.surname.like('%' + text + '%')),
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(Users.name, Users.surname,
                                                             asc(Users.balance)).all()
        for student in students:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    if get_student_info(student) != None:
                        list.append(get_student_info(student))
            else:
                if get_student_info(student) != None:
                    list.append(get_student_info(student))

    elif type == 'debtors' and status == True:

        students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                         or_(Users.name.like('%' + text + '%'),
                                                                             Users.surname.like('%' + text + '%')),
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(
            asc(Users.balance)).all()
        april = datetime.strptime("2024-03", "%Y-%m")
        for student in students:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    if get_completed_student_info(student) != None:
                        list.append(get_completed_student_info(student))
            else:
                if get_completed_student_info(student) != None:
                    list.append(get_completed_student_info(student))
    elif type == "lead" and status == False:
        leads = Lead.query.filter(Lead.location_id == location_id, Lead.deleted == False,
                                  Lead.name.like('%' + text + '%')).order_by(desc(Lead.id), Lead.name).all()
        for lead in leads:
            if get_lead_tasks(lead) != None:
                list.append(get_lead_tasks(lead))
    elif type == "lead" and status == True:

        leads = Lead.query.filter(Lead.location_id == location_id, Lead.deleted == False,
                                  Lead.name.like('%' + text + '%')).order_by(desc(Lead.id, Lead.name)).all()
        for lead in leads:
            if get_completed_lead_tasks(lead) != None:
                list.append(get_completed_lead_tasks(lead))
    elif type == "newStudents":
        students = Students.query.filter(Students.group == None).join(Students.user).filter(
            Users.location_id == location_id, Users.student != None,
            or_(Users.name.like('%' + text + '%'),
                Users.surname.like('%' + text + '%')),
            Students.subject != None,
            Students.deleted_from_register == None).order_by(Users.name, Users.surname).all()
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

        if status == False:
            list = students_info
        else:
            list = completed_tasks
    return jsonify({
        'students': list
    })


@app.route(f'{api}/student_in_debts/', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/student_in_debts/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def student_in_debts(location_id):
    today = datetime.today()
    change_statistics(location_id)
    # date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    print(calendar_day.date)
    april = datetime.strptime("2024-03-01", "%Y-%m-%d")
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    task_type = Tasks.query.filter(Tasks.name == 'excuses').first()
    task_statistics = TasksStatistics.query.filter(
        TasksStatistics.task_id == task_type.id,
        TasksStatistics.calendar_day == calendar_day.id,
        TasksStatistics.location_id == location_id
    ).first()
    if request.method == "GET":
        if user.role_info.type_role == "admin":
            update_tasks_in_progress(user.location_id)
            update_all_ratings()

        task_students = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                  TaskStudents.status == False,
                                                  TaskStudents.tasksstatistics_id == task_statistics.id,
                                                  ).all()
        task_student = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                 TaskStudents.tasksstatistics_id == task_statistics.id).first()
        if task_student:
            students = Students.query.filter(Students.id.in_([st.student_id for st in task_students]))
        else:

            students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                             Users.location_id == location_id
                                                                             ).filter(
                Students.deleted_from_register == None).order_by(
                asc(Users.balance)).limit(100).all()
        if not task_student:
            for student in students:
                if student.deleted_from_group:
                    if student.deleted_from_group[-1].day.month.date >= april:
                        add_task_student = TaskStudents(task_id=task_type.id, tasksstatistics_id=task_statistics.id,
                                                        student_id=student.id)
                        add_task_student.add()

                else:

                    add_task_student = TaskStudents(task_id=task_type.id, tasksstatistics_id=task_statistics.id,
                                                    student_id=student.id)
                    add_task_student.add()

        payments_list = []
        for student in students:
            if student.deleted_from_group:
                if student.deleted_from_group[-1].day.month.date >= april:
                    if get_student_info(student) != None:
                        payments_list.append(get_student_info(student))
            else:
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
        else:
            to_date = datetime.strptime(f'{today.year}-{today.month}-{int(today.day) + 1}', "%Y-%m-%d")

        student = Students.query.filter(Students.id == user_id).first()
        if to_date > calendar_day.date:
            exist_excuse = StudentExcuses.query.filter(StudentExcuses.added_date == calendar_day.date,
                                                       StudentExcuses.student_id == student.id).first()
            if not exist_excuse:
                new_excuse = StudentExcuses(reason=reason if select == "tel ko'tardi" else "tel ko'tarmadi",
                                            to_date=to_date,
                                            added_date=calendar_day.date,
                                            student_id=student.id)
                db.session.add(new_excuse)
                db.session.commit()

            task_student = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                     TaskStudents.tasksstatistics_id == task_statistics.id,
                                                     TaskStudents.student_id == student.id).first()
            task_student.status = True
            db.session.commit()
            update_tasks_in_progress(user.location_id)
            info = update_all_ratings()
            task_students = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                      TaskStudents.status == True,
                                                      TaskStudents.tasksstatistics_id == task_statistics.id,
                                                      ).count()

            return jsonify({"student": {
                'msg': "Komment belgilandi",
                'id': student.id,
                "info": info,
                "students_num": task_students
            }})
        else:
            return jsonify({
                'msg': "Eski sana kiritilgan",

            })


@app.route(f'{api}/get_completed_tasks/', defaults={"location_id": None}, methods=["GET"])
@app.route(f'{api}/get_completed_tasks/<int:location_id>', methods=["GET"])
@jwt_required()
def get_completed_tasks(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    task_type = Tasks.query.filter(Tasks.name == 'excuses').first()
    task_statistics = TasksStatistics.query.filter(
        TasksStatistics.task_id == task_type.id,
        TasksStatistics.calendar_day == calendar_day.id,
        TasksStatistics.location_id == location_id
    ).first()
    task_students = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                              TaskStudents.tasksstatistics_id == task_statistics.id,
                                              TaskStudents.status == True).all()
    students = Students.query.filter(Students.id.in_([st.student_id for st in task_students])).all()
    completed_tasks = []
    update_tasks_in_progress(location_id)
    april = datetime.strptime("2024-03", "%Y-%m")
    for student in students:
        april = datetime.strptime("2024-03", "%Y-%m")
        calendar_year, calendar_month, calendar_day = find_calendar_date()
        today = datetime.today()
        date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
        info = {
            "id": student.id,
            "name": student.user.name.title(),
            "surname": student.user.surname.title(),
            "status": ["green", "yellow", "red"][student.debtor] if student.debtor < 2 else ["green", "yellow", "red"][
                2],
            "phone": student.user.phone[0].phone,
            "balance": student.user.balance,
            "teacher": [str(teacher.user_id) for gr in student.group for teacher in
                        Teachers.query.filter(Teachers.id == gr.teacher_id)] if student.group else [],
            "reason": "",
            "payment_reason": "tel qilinmaganlar",
            "reason_days": "",
            'history': [],
            'deleted_date': ''
        }
        if student.deleted_from_group:
            if student.deleted_from_group[-1].day.month.date >= april:
                info[
                    'deleted_date'] = f'{student.deleted_from_group[-1].day.date.year}-{student.deleted_from_group[-1].day.date.month}-{student.deleted_from_group[-1].day.date.day}'

        if student.reasons_list:
            for reason in student.reasons_list:
                if not reason.to_date and reason.added_date == calendar_day.date:
                    info['reason_days'] = reason.added_date.strftime("%Y-%m-%d")
                    info['payment_reason'] = "tel ko'tarmadi"
                elif reason.to_date and reason.to_date >= calendar_day.date:
                    info['reason'] = reason.reason
                    info['reason_days'] = reason.to_date.strftime("%Y-%m-%d")
                    info['payment_reason'] = "tel ko'tardi"
            # return info
        # if student.excuses and student.excuses[-1].added_date == date_strptime and student.excuses[
        #     -1].reason != "tel ko'tarmadi" and student.excuses[-1].to_date > date_strptime:
        if student.excuses and student.excuses[-1].added_date == date_strptime:
            for exc in student.excuses:
                if exc.added_date:
                    info['history'] = [{'id': exc.id, 'added_date': exc.added_date.strftime("%Y-%m-%d"),
                                        'to_date': exc.to_date.strftime("%Y-%m-%d") if exc.to_date else '',
                                        'comment': exc.reason}]
        completed_tasks.append(info)
    return jsonify({'completed_tasks': completed_tasks})


@app.route(f'{api}/daily_statistics', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/daily_statistics/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def daily_statistics(location_id):
    date = request.get_json()
    date_strptime = datetime.strptime(date, "%Y-%m-%d")
    day = CalendarDay.query.filter(CalendarDay.date == date_strptime).first()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    change_statistics(location_id)
    update_tasks_in_progress(user.location_id)
    update_all_ratings()
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

# user = Users.query.filter(Users.user_id == get_jwt_identity()).first()

#
# students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
#                                                                  Users.location_id == location_id
#                                                                  ).filter(
#     Students.deleted_from_register == None).order_by(
#     asc(Users.balance)).all()
# students_excuses = StudentExcuses.query.filter(StudentExcuses.student_id.in_([st_id.id for st_id in students]),
#                                                StudentExcuses.added_date == calendar_day.date,
#                                                StudentExcuses.to_date > calendar_day.date).count()
# task_statistics.completed_tasks = students_excuses
# db.session.commit()
# task_statistics.completed_tasks_percentage = (
#                                                      task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100
# db.session.commit()
# overall_location_statistics = TasksStatistics.query.filter(
#     TasksStatistics.user_id == user.id,
#     TasksStatistics.calendar_day == calendar_day.id,
#     TasksStatistics.location_id == location_id
# ).all()
# tasks_daily_statistics = TaskDailyStatistics.query.filter(
#     TaskDailyStatistics.user_id == user.id,
#     TaskDailyStatistics.location_id == location_id,
#     TaskDailyStatistics.calendar_day == calendar_day.id
# ).first()
# overall_complete = 0
# for overall in overall_location_statistics:
#     overall_complete += overall.completed_tasks
# completed_tasks_percentage = round((
#                                            overall_complete / tasks_daily_statistics.in_progress_tasks) * 100 if tasks_daily_statistics.in_progress_tasks > 0 else 0)
#
# tasks_daily_statistics.completed_tasks = overall_complete
# tasks_daily_statistics.completed_tasks_percentage = completed_tasks_percentage
# db.session.commit()
