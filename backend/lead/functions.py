from backend.models.models import db, extract
from backend.functions.utils import desc
from backend.tasks.models.models import Tasks, TasksStatistics, TaskDailyStatistics
from datetime import datetime
from backend.models.models import Lead, LeadInfos, Users
from backend.functions.utils import find_calendar_date
from flask_jwt_extended import get_jwt_identity


def update_task_statistics(user, status, calendar_day, location_id, task_type):
    def update_statistics(task_statistics, completed_tasks_delta):
        completed_tasks = max(task_statistics.completed_tasks + completed_tasks_delta, 0)
        in_progress_tasks = task_statistics.in_progress_tasks - 1

        completed_tasks_percentage = (completed_tasks / in_progress_tasks * 100) if in_progress_tasks else 0

        TasksStatistics.query.filter_by(id=task_statistics.id).update({
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'completed_tasks_percentage': completed_tasks_percentage
        })
        db.session.commit()

        daily_tasks = TaskDailyStatistics.query.filter_by(calendar_day=calendar_day.id, location_id=location_id).first()
        completed_tasks_daily = max(daily_tasks.completed_tasks + completed_tasks_delta, 0)
        in_progress_tasks_daily = daily_tasks.in_progress_tasks - 1

        TaskDailyStatistics.query.filter_by(calendar_day=calendar_day.id, location_id=location_id).update({
            'in_progress_tasks': in_progress_tasks_daily,
            'completed_tasks': completed_tasks_daily
        })
        db.session.commit()

    task_statistics = TasksStatistics.query.filter_by(
        calendar_day=calendar_day.id,
        location_id=location_id,
        task_id=task_type.id
    ).first()

    if status in ["green", "yellow"]:
        update_statistics(task_statistics, completed_tasks_delta=-1)

        overall_statistics = TasksStatistics.query.filter_by(
            user_id=user.id, calendar_day=calendar_day.id, location_id=location_id
        ).all()

        total_completed_tasks = sum(stat.completed_tasks for stat in overall_statistics)
        tasks_daily_statistics = TaskDailyStatistics.query.filter_by(
            user_id=user.id, location_id=location_id, calendar_day=calendar_day.id
        ).first()
        completed_tasks_percentage = (
                total_completed_tasks / tasks_daily_statistics.in_progress_tasks * 100) if total_completed_tasks else 0
        TaskDailyStatistics.query.filter_by(
            user_id=user.id, location_id=location_id, calendar_day=calendar_day.id
        ).update({
            'completed_tasks': total_completed_tasks,
            'completed_tasks_percentage': completed_tasks_percentage
        })
        db.session.commit()
    else:
        update_statistics(task_statistics, completed_tasks_delta=0)
        overall_statistics = TasksStatistics.query.filter_by(
            user_id=user.id, calendar_day=calendar_day.id, location_id=location_id
        ).all()

        total_completed_tasks = sum(stat.completed_tasks for stat in overall_statistics)
        tasks_daily_statistics = TaskDailyStatistics.query.filter_by(
            user_id=user.id, location_id=location_id, calendar_day=calendar_day.id
        ).first()
        completed_tasks_percentage = (
                total_completed_tasks / tasks_daily_statistics.in_progress_tasks * 100) if total_completed_tasks else 0
        TaskDailyStatistics.query.filter_by(
            user_id=user.id, location_id=location_id, calendar_day=calendar_day.id
        ).update({
            'completed_tasks': total_completed_tasks,
            'completed_tasks_percentage': completed_tasks_percentage
        })
        db.session.commit()


def update_posted_tasks():
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    task_type = Tasks.query.filter_by(name='leads').first()
    task_statistics = TasksStatistics.query.filter_by(
        task_id=task_type.id,
        calendar_day=calendar_day.id,
        location_id=user.location_id
    ).first()
    leads = Lead.query.filter(Lead.location_id == user.location_id, Lead.deleted != True).all()
    lead_infos = LeadInfos.query.filter(
        extract("day", LeadInfos.added_date) == int(calendar_day.date.strftime("%d")),
        LeadInfos.lead_id.in_([lead.id for lead in leads])).count()
    TasksStatistics.query.filter_by(id=task_statistics.id).update({
        'completed_tasks': lead_infos,
    })
    db.session.commit()
    task_statistics.in_progress_tasks = task_statistics.total_tasks - lead_infos
    db.session.commit()
    updated_task_statistics = TasksStatistics.query.filter_by(id=task_statistics.id).first()
    cm_tasks = round(
        (task_statistics.completed_tasks / task_statistics.total_tasks) * 100) if task_statistics.completed_tasks else 0

    TasksStatistics.query.filter_by(id=updated_task_statistics.id).update({
        'completed_tasks_percentage': cm_tasks
    })
    db.session.commit()


    return {
        "in_progress": task_statistics.in_progress_tasks,
        "completed_tasks": task_statistics.completed_tasks
    }


def get_lead_tasks(lead):
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    history = []
    if lead.infos:
        for info in lead.infos:
            history.append(info.convert_json())
    if lead.infos:
        if lead.infos[0].day <= date_strptime:
            day = lead.infos[0].day
            lead_day = int(day.strftime("%d"))
            current_month = int(datetime.today().strftime("%m"))
            current_day = int(datetime.today().strftime("%d"))
            lead_month = int(day.strftime("%m"))
            if current_month == lead_month:
                index = current_day - lead_day
                if index > 1:
                    index = 1
                if index < 0:
                    index = 0
            else:
                index = 1
            return {
                "id": lead.id,
                "name": lead.name,
                "phone": lead.phone,
                "day": lead.day.date.strftime("%Y-%m-%d"),
                "deleted": lead.deleted,
                "comment": lead.comment,
                "status": ['yellow', 'red'][index],
                "history": history,
                "subjects": [subject.convert_json() for subject in lead.subject]
            }
    else:
        index = 1
        return {
            "id": lead.id,
            "name": lead.name,
            "phone": lead.phone,
            "day": lead.day.date.strftime("%Y-%m-%d"),
            "deleted": lead.deleted,
            "comment": lead.comment,
            "status": ['yellow', 'red'][index],
            "history": history,
            "subjects": [subject.convert_json() for subject in lead.subject]
        }


def get_completed_lead_tasks(lead):
    today = datetime.today()
    date_strptime = datetime.strptime(f"{today.year}-{today.month}-{today.day}", "%Y-%m-%d")
    history = []
    if lead.infos:
        for info in lead.infos:
            history.append(info.convert_json())
    if lead.infos:
        if lead.infos[0].added_date == date_strptime:
            return {
                "id": lead.id,
                "name": lead.name,
                "phone": lead.phone,
                "day": lead.day.date.strftime("%Y-%m-%d"),
                "deleted": lead.deleted,
                "comment": lead.comment,
                "status": 'green',
                "history": history,
                "subjects": [subject.convert_json() for subject in lead.subject]
            }
