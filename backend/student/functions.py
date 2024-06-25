from backend.teacher.models import Teachers
from backend.functions.utils import find_calendar_date
from datetime import datetime


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
        if student.excuses[-1].to_date != None:
            if student.excuses[-1].to_date <= date_strptime:
                for exc in student.excuses:
                    if exc.to_date and exc.added_date:
                        info['history'] = [{'id': exc.id, 'added_date': exc.added_date.strftime("%Y-%m-%d"),
                                            'to_date': exc.to_date.strftime("%Y-%m-%d") if exc.to_date else '',
                                            'comment': exc.reason}]
                return info
    else:
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
