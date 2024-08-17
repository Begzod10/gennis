from backend.teacher.models import Teachers
from backend.functions.utils import find_calendar_date
from datetime import datetime
from backend.models.models import Users, TasksStatistics, TaskDailyStatistics, db, TaskStudents, Tasks, Students, Lead, \
    Locations, desc, LeadInfos, StudentCallingInfo, StudentExcuses
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import asc


def update_all_ratings():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    overall_location_statistics = TasksStatistics.query.filter_by(
        user_id=user.id,
        calendar_day=calendar_day.id,
        location_id=user.location_id
    ).all()
    completed_tasks = sum(stat.completed_tasks for stat in overall_location_statistics)
    tasks_daily_statistics = TaskDailyStatistics.query.filter_by(
        user_id=user.id,
        location_id=user.location_id,
        calendar_day=calendar_day.id
    ).first()

    completed_tasks_percentage = round(
        (completed_tasks / tasks_daily_statistics.total_tasks) * 100) if completed_tasks else 0

    TaskDailyStatistics.query.filter_by(
        user_id=user.id,
        location_id=user.location_id,
        calendar_day=calendar_day.id
    ).update({
        'completed_tasks': completed_tasks,
        'completed_tasks_percentage': completed_tasks_percentage,
        "in_progress_tasks": tasks_daily_statistics.total_tasks - completed_tasks

    })
    db.session.commit()
    return {
        "completed_tasks": completed_tasks,
        "completed_tasks_percentage": completed_tasks_percentage,
        "in_progress": tasks_daily_statistics.in_progress_tasks
    }


def add_tasks():
    tasks = ['excuses', 'new_students', 'leads']
    for task in tasks:
        filtered_task = Tasks.query.filter(Tasks.name == task).first()
        if not filtered_task:
            add = Tasks(name=task)
            db.session.add(add)
            db.session.commit()
        else:
            filtered_task.role = "admin"
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

    # number_new = 20 * number
    # number_old = number - 1 * 20
    # id_first = number_old + id
    # id_last = id + number_new
    task_type = Tasks.query.filter(Tasks.name == 'excuses').first()
    task_statistics = TasksStatistics.query.filter(
        TasksStatistics.task_id == task_type.id,
        TasksStatistics.calendar_day == calendar_day.id,
        TasksStatistics.location_id == location_id
    ).first()
    #
    # lead_infos = LeadInfos.query.all()
    # excuses = StudentExcuses.query.all()
    # calling = StudentCallingInfo.query.all()
    # for lead in lead_infos:
    #     db.session.delete(lead)
    #     db.session.commit()
    #
    # for exc in excuses:
    #     db.session.delete(exc)
    #     db.session.commit()
    #
    # for call in calling:
    #     db.session.delete(call)
    #     db.session.commit()
    #
    # task_students = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
    #                                           TaskStudents.tasksstatistics_id == task_statistics.id,
    #                                           ).all()
    # for st in task_students:
    #     db.session.delete(st)
    #     db.session.commit()
    #
    # task_statistics = TasksStatistics.query.all()
    # for task in task_statistics:
    #     db.session.delete(task)
    # task_daily = TaskDailyStatistics.query.all()
    # for task in task_daily:
    #     db.session.delete(task)
    #     db.session.commit()

    if task_statistics:
        task_student = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                 TaskStudents.tasksstatistics_id == task_statistics.id).first()
        task_students = TaskStudents.query.filter(TaskStudents.task_id == task_type.id,
                                                  TaskStudents.tasksstatistics_id == task_statistics.id,
                                                  TaskStudents.status == False).all()
        if task_student:
            students = Students.query.filter(Students.id.in_([st.student_id for st in task_students]))
        else:

            students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                             Users.location_id == location_id
                                                                             ).filter(
                Students.deleted_from_register == None).order_by(
                asc(Users.balance)).limit(100).all()

            if not task_student:
                for st in students:
                    add_task_student = TaskStudents(task_id=task_type.id, tasksstatistics_id=task_statistics.id,
                                                    student_id=st.id)
                    add_task_student.add()
    else:

        students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(
            asc(Users.balance)).limit(100).all()
    for student in students:
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

    new_students = Students.query.join(Users).filter(Users.location_id == location_id, Users.student != None,
                                                     Students.subject != None,
                                                     Students.deleted_from_register == None).order_by(
        desc(Students.id)).all()
    for student in new_students:
        loc_id = student.user.location_id

        if loc_id:

            if student.student_calling_info:
                if student.student_calling_info[-1].date <= date_strptime:
                    locations_info[loc_id]['new_students'] += 1
                else:
                    print(student.user.name)
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
            overall_tasks = counts['excuses'] + counts['leads'] + counts['new_students']
            if not filtered_daily_statistics:
                add_daily_statistics = TaskDailyStatistics(
                    user_id=user.id, calendar_year=calendar_year.id,
                    calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                    in_progress_tasks=overall_tasks, location_id=loc_id, total_tasks=overall_tasks,
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
                        location_id=loc_id, user_id=user.id, in_progress_tasks=count,
                        total_tasks=count
                    )
                    db.session.add(add_task_stat)
                    db.session.commit()


# shu joyidan ishlash kere
def update_tasks_in_progress(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    task = Tasks.query.filter(Tasks.role == "admin", Tasks.name == "excuses").first()

    task_statistics = TasksStatistics.query.filter(TasksStatistics.location_id == location_id,
                                                   TasksStatistics.calendar_day == calendar_day.id,
                                                   TasksStatistics.task_id == task.id).first()

    task_student = TaskStudents.query.filter(TaskStudents.task_id == task.id,
                                             TaskStudents.tasksstatistics_id == task_statistics.id).first()
    task_students = TaskStudents.query.filter(TaskStudents.task_id == task.id,
                                              TaskStudents.tasksstatistics_id == task_statistics.id,
                                              TaskStudents.status == False).all()

    if task_student:
        students = Students.query.filter(Students.id.in_([st.student_id for st in task_students])).all()
    else:

        students = db.session.query(Students).join(Students.user).filter(Users.balance < 0,
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(
            asc(Users.balance)).limit(100).all()
    if not task_student:
        for st in students:
            add_task_student = TaskStudents(task_id=task.id, tasksstatistics_id=task_statistics.id,
                                            student_id=st.id)
            add_task_student.add()
    else:
        students = db.session.query(Students).join(Students.user).filter(Users.balance > 0,
                                                                         Users.location_id == location_id
                                                                         ).filter(
            Students.deleted_from_register == None).order_by(
            asc(Users.balance)).limit(100).all()
        for st in students:
            task_student = TaskStudents.query.filter(TaskStudents.task_id == task.id,
                                                     TaskStudents.tasksstatistics_id == task_statistics.id,
                                                     TaskStudents.student_id == st.id).first()
            if task_student:
                task_student.status = True
                db.session.commit()
    completed_students = TaskStudents.query.filter(TaskStudents.task_id == task.id,
                                                   TaskStudents.tasksstatistics_id == task_statistics.id,
                                                   TaskStudents.status == True).count()
    task_statistics.completed_tasks = completed_students
    task_statistics.in_progress_tasks = task_statistics.total_tasks - completed_students
    task_statistics.completed_tasks_percentage = round(
        (task_statistics.completed_tasks / task_statistics.total_tasks) * 100)
    db.session.commit()


def get_student_info(student):
    april = datetime.strptime("2024-03", "%Y-%m")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    info = {
        "id": student.id,
        "name": student.user.name.title(),
        "surname": student.user.surname.title(),
        "status": ["green", "yellow", "red"][student.debtor] if student.debtor < 2 else ["green", "yellow", "red"][2],
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

    if student.excuses:
        # if student.excuses[-1].to_date != None:
        #     if student.excuses[-1].to_date <= date_strptime:
        for exc in student.excuses:
            if exc.to_date and exc.added_date:
                info['history'] += [{'id': exc.id, 'added_date': exc.added_date.strftime("%Y-%m-%d"),
                                     'to_date': exc.to_date.strftime("%Y-%m-%d") if exc.to_date else '',
                                     'comment': exc.reason}]

    # else:
    return info


def get_completed_student_info(student):
    april = datetime.strptime("2024-03", "%Y-%m")
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    info = {
        "id": student.id,
        "name": student.user.name.title(),
        "surname": student.user.surname.title(),
        "status": ["green", "yellow", "red"][student.debtor] if student.debtor < 2 else ["green", "yellow", "red"][2],
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
        return info
