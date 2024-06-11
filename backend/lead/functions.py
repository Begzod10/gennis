from backend.models.models import db, extract

from backend.tasks.models import Tasks, TasksStatistics, TaskDailyStatistics, LeadInfos, Lead


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


def update_posted_tasks(user, date, date_strptime, calendar_day, info, task_type, location_id):
    if date != date_strptime:
        task_statistics = TasksStatistics.query.filter_by(
            task_id=task_type.id,
            calendar_day=calendar_day.id,
            location_id=info.lead.location_id
        ).first()
        leads = Lead.query.filter(Lead.location_id == location_id, Lead.deleted != True).all()
        lead_infos = LeadInfos.query.filter(extract("day", LeadInfos.added_date) == int(calendar_day.date.strftime("%d")),
                                            LeadInfos.lead_id.in_([lead.id for lead in leads])).count()
        TasksStatistics.query.filter_by(id=task_statistics.id).update({
            'completed_tasks': lead_infos,
        })
        db.session.commit()
        updated_task_statistics = TasksStatistics.query.filter_by(id=task_statistics.id).first()
        cm_tasks = round((
                                 task_statistics.completed_tasks / task_statistics.in_progress_tasks) * 100) if task_statistics.completed_tasks else 0

        TasksStatistics.query.filter_by(id=updated_task_statistics.id).update({
            'completed_tasks_percentage': cm_tasks
        })
        db.session.commit()
        overall_location_statistics = TasksStatistics.query.filter_by(
            user_id=user.id,
            calendar_day=calendar_day.id,
            location_id=info.lead.location_id
        ).all()
        completed_tasks = sum(stat.completed_tasks for stat in overall_location_statistics)
        tasks_daily_statistics = TaskDailyStatistics.query.filter_by(
            user_id=user.id,
            location_id=updated_task_statistics.location_id,
            calendar_day=calendar_day.id
        ).first()
        completed_tasks_percentage = round((completed_tasks / tasks_daily_statistics.in_progress_tasks) * 100) if completed_tasks else 0

        TaskDailyStatistics.query.filter_by(
            user_id=user.id,
            location_id=updated_task_statistics.location_id,
            calendar_day=calendar_day.id
        ).update({
            'completed_tasks': completed_tasks,
            'completed_tasks_percentage': completed_tasks_percentage
        })
        db.session.commit()
