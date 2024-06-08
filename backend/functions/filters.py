import calendar
from datetime import datetime, date

from flask_jwt_extended import jwt_required

from app import app, jsonify, contains_eager, db, desc
from backend.functions.utils import find_calendar_date, number_of_days_in_month, api, iterate_models
from backend.models.models import Locations, AccountingPeriod, Teachers, CalendarMonth, EducationLanguage, CalendarDay, \
    CalendarYear, PaymentTypes, CourseTypes, Subjects, Students, LessonPlan, Users, Week, DeletedStudents, Professions, \
    Group_Room_Week, RegisterDeletedStudents, Groups, Rooms, GroupReason


@app.route(f'{api}/block_information2', defaults={"location_id": None})
@app.route(f'{api}/block_information2/<int:location_id>')
@jwt_required()
def block_information2(location_id):
    """

    :param location_id: Locations primary key
    :return: data list by location id
    """
    locations = Locations.query.order_by(Locations.id).all()
    locations_list = [{'id': location.id, "name": location.name} for location in locations]

    # subject
    subjects = Subjects.query.order_by(Subjects.id).all()
    subject_list = [{'id': sub.id, "name": sub.name} for sub in subjects]

    # course types
    course_types = CourseTypes.query.order_by(CourseTypes.id).all()
    course_types_list = [{'id': sub.id, "name": sub.name} for sub in course_types]

    # education language
    education_languages = EducationLanguage.query.all()
    education_languages_list = [{
        'id': sub.id,
        "name": sub.name
    } for sub in education_languages]

    #   payment types
    payment_types = PaymentTypes.query.all()
    payment_types_list = [{
        'id': sub.id,
        "name": sub.name
    } for sub in payment_types]
    rooms = Rooms.query.filter(Rooms.location_id == location_id).order_by(Rooms.id).all()
    room_list = [{
        "id": room.id,
        "name": room.name,
        "seats": room.seats_number,
        "electronic": room.electronic_board
    } for room in rooms]

    days = Week.query.filter(Week.location_id == location_id).order_by(Week.id).all()
    day_list = [{
        "id": day.id,
        "name": day.name
    } for day in days]
    calendar_years = CalendarYear.query.order_by(CalendarYear.id).all()

    group_reasons = GroupReason.query.order_by(GroupReason.id).all()

    data = {
        "locations": locations_list,
        "subjects": subject_list,
        "course_types": course_types_list,
        "langs": education_languages_list,
        "payment_types": payment_types_list,
        "rooms": room_list,
        "days": day_list,
        "years": iterate_models(calendar_years),
        "group_reasons": iterate_models(group_reasons)
    }
    return jsonify({
        "data": data
    })


def teacher_filter():
    """
    filter teacher by language and subject
    :return: language list, subject list
    """
    subjects = Subjects.query.order_by('id').all()
    languages = EducationLanguage.query.order_by(EducationLanguage.id).all()
    subject_list = [subject.name for subject in subjects]
    language_list = [language.name for language in languages]

    filters = {
        "subjects": {
            "id": 1,
            "title": "Fan boyicha",
            "type": "btn",
            "typeChange": "multiple",
            "activeFilters": [],
            "filtersList": subject_list
        },
        "language": {
            "id": 2,
            "title": "Til bo'yicha",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": [],
            "filtersList": language_list
        },

    }
    return filters


def staff_filter():
    """
    filter staff by language and job
    :return: language list, job list
    """
    languages = EducationLanguage.query.order_by('id').all()
    professions = Professions.query.order_by(Professions.id).all()
    profession_list = [profession.name for profession in professions]

    profession_list = list(dict.fromkeys(profession_list))
    language_list = [language.name for language in languages]
    filters = {
        "job": {
            "id": 1,
            "title": "Fan boyicha",
            "type": "btn",
            "typeChange": "multiple",
            "activeFilters": [],
            "filtersList": profession_list
        },
        "language": {
            "id": 2,
            "title": "Til bo'yicha",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": [],
            "filtersList": ["Uz", "Ru"]
        }
    }
    return filters


def new_students_filters():
    """
    student filter
    :return: language list, subject list and form for filtering students by their age
    """
    subjects = Subjects.query.order_by('id').all()
    languages = EducationLanguage.query.order_by('id').all()
    subject_list = [subject.name for subject in subjects]
    language_list = [language.name for language in languages]
    filters = {
        "subjects": {
            "id": 1,
            "title": "Fan boyicha",
            "type": "btn",
            "typeChange": "multiple",
            "activeFilters": [],
            "filtersList": subject_list
        },
        "language": {
            "id": 2,
            "title": "Til bo'yicha",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": [],
            "filtersList": language_list
        },
        "age": {
            "id": 4,
            "title": "Yosh bo'yicha",
            "type": "input",
            "fromTo": {

            }
        }
    }
    return filters


def group_filter(location_id):
    """

    :param location_id: branch primary key to filter teachers by their branch
    :return: filter blocks that user can filter groups by teachers, languages, course types, subjects and last one to
    separate groups to two list : active and nonactive
    """
    teachers = db.session.query(Teachers).join(Teachers.locations).options(contains_eager(Teachers.locations)).filter(
        Locations.id == location_id).order_by(Teachers.id).all()
    education_languages = EducationLanguage.query.all()
    education_languages_list = [sub.name for sub in education_languages]

    course_types = CourseTypes.query.order_by(CourseTypes.id).all()
    course_types_list = [sub.name for sub in course_types]

    teachers_list = [teacher.user.name.title() for teacher in teachers]

    subjects = Subjects.query.order_by(Subjects.id).all()
    subject_list = [sub.name.title() for sub in subjects]
    status = {
        "id": 2,
        "title": "Status",
        "type": "btn",
        "typeChange": "once",
        "activeFilters": ["True"],
        "filtersList": ["True", "False"]
    }
    subjects = {
        "id": 3,
        "title": "Fanlar",
        "type": "btn",
        "typeChange": "multiple",
        "activeFilters": [],
        "filtersList": subject_list
    }
    languages = {
        "id": 4,
        "title": "Til bo'yicha",
        "type": "btn",
        "typeChange": "once",
        "activeFilters": [],
        "filtersList": education_languages_list
    }
    courses = {
        "id": 5,
        "title": "Kurs turi",
        "type": "btn",
        "typeChange": "once",
        "activeFilters": [],
        "filtersList": course_types_list
    }
    teachers_list = list(dict.fromkeys(teachers_list))
    teachers = {
        "id": 6,
        "title": "O'qtuvchilar",
        "type": "btn",
        "typeChange": "once",
        "activeFilters": [],
        "filtersList": teachers_list
    }

    data = {
        "status": status,
        "subjects": subjects,
        "course_types": courses,
        "languages": languages,
        "teacherName": teachers
    }
    return data


def accounting_payments(type_filter=None):
    if type_filter == "undefined":
        type_filter = None
    years = CalendarYear.query.order_by(
        CalendarYear.date).all()
    years_id_list = []
    for year in years:
        years_id_list.append(year.id)
    months = CalendarMonth.query.order_by(CalendarMonth.date).all()
    months_id_list = []
    for month in months:
        months_id_list.append(month.id)
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    days = CalendarDay.query.filter(CalendarDay.account_period_id == accounting_period.id).order_by(
        CalendarDay.date).all()
    years_list = [{
        "value": str(year.id),
        "name": year.date.strftime("%Y")
    } for year in years]

    month_list = [{
        "value": str(month.id),
        "name": month.date.strftime("%m"),
        "year_id": month.year_id
    } for month in months]

    day_list = [{
        "value": str(day.id),
        "name": day.date.strftime("%d"),
        "month_id": day.month_id
    } for day in days]

    payment_types = PaymentTypes.query.all()
    payment_types_list = [sub.name for sub in payment_types]

    day_dict = {gr['value']: gr for gr in day_list}
    filtered_days = list(day_dict.values())
    if type_filter:
        filtered_days = []
        days = CalendarDay.query.filter(CalendarDay.account_period_id == accounting_period.id).order_by(
            CalendarDay.date).all()
        day_list = [{
            "value": str(day.id),
            "name": day.date.strftime("%d"),
            "month_id": day.month_id
        } for day in days]

        day_dict = {gr['value']: gr for gr in day_list}
        filtered_days = list(day_dict.values())

        day_dict = {gr['name']: gr for gr in month_list}
        filtered_months = list(day_dict.values())

        day_dict = {gr['name']: gr for gr in years_list}
        filtered_years = list(day_dict.values())
        filters = {
            "day": {
                "id": 1,
                "title": "Kun bo'yicha",
                "name": "Kun",
                "type": "select",
                "activeFilters": [],
                "filtersList": filtered_days,

            },
            "month": {
                "id": 2,
                "title": "Oy bo'yicha",
                "name": "Oy",
                "type": "select",
                "activeFilters": [],
                "filtersList": filtered_months,

            },
            "year": {
                "id": 3,
                "title": "Yil bo'yicha",
                "name": "Yil",
                "type": "select",
                "activeFilters": [],
                "filtersList": filtered_years,

            },
            "typePayment": {
                "id": 1,
                "title": "To'lov turi bo'yicha",
                "type": "btn",
                "typeChange": "multiple",
                "activeFilters": [],
                "filtersList": payment_types_list
            },

            "moneyType": ["red", "yellow", "black"],

        }
    else:
        filters = {
            "day": {
                "id": 1,
                "title": "Kun bo'yicha",
                "name": "Kun",
                "type": "select",
                "activeFilters": [],
                "filtersList": filtered_days,

            },
            "typePayment": {
                "id": 2,
                "title": "To'lov turi bo'yicha",
                "type": "btn",
                "typeChange": "multiple",
                "activeFilters": [],
                "filtersList": payment_types_list
            },

            "name": {
                "id": 3,
                "title": "Xarajat turi bo'yicha",
                "type": "btn",
                "typeChange": "multiple",
                "activeFilters": [],
                "filtersList": ["gaz", "suv", "svet", "arenda"]
            }
        }
    return filters


def collection():
    """

    :return: PaymentTypes datas
    """
    payment_types = PaymentTypes.query.all()
    payment_types_list = [sub.name for sub in payment_types]
    object = {
        "typePayment": {
            "id": 1,
            "title": "To'lov turi bo'yicha",
            "type": "btn",
            "typeChange": "multiple",
            "activeFilters": [],
            "filtersList": payment_types_list
        }
    }
    return object


def debt_students(location_id):
    """
    filter Student table data
    :param location_id: Locations table primary key
    :return: Student table data
    """
    students = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
        Users.balance < 0, Users.location_id == location_id).order_by(Users.balance).all()

    teacher_list = []
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    reasons_days = []
    for student in students:
        if student.group:
            for gr in student.group:
                teacher = Teachers.query.filter(Teachers.id == gr.teacher_id).first()
                if teacher:
                    for_teacher = {
                        "value": str(teacher.user.id),
                        "name": f"{teacher.user.name.title()} {teacher.user.surname.title()}",
                    }
                    teacher_list.append(for_teacher)

        if student.reasons_list:
            for reason in student.reasons_list:
                if reason.to_date:
                    if calendar_day.date <= reason.to_date:
                        info = {

                            "name": reason.to_date.strftime("%Y-%m-%d")
                        }
                        reasons_days.append(info)
                if calendar_day.date == reason.added_date:
                    info = {
                        "name": reason.added_date.strftime("%Y-%m-%d")
                    }
                    reasons_days.append(info)

    day_dict = {gr['value']: gr for gr in teacher_list}
    final_list = list(day_dict.values())

    day_dict = {gr['name']: gr for gr in reasons_days}
    filtered_days = list(day_dict.values())
    debt_students_list = {
        "moneyType": {
            "id": 2,
            "title": "Rangi bo'yicha",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": [],
            "filtersList": ['black', "red", "yellow"],
        },
        "status": {
            "id": 2,
            "title": "Status",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": "Guruh",
            "filtersList": ["Guruh", "Guruhsiz"]
        },
        "teacher": {
            "id": 3,
            "title": "O'qtuvchi bo'yicha",
            "name": "O'qtuvchi",
            "type": "select",
            "activeFilters": [],
            "filtersList": final_list
        },
        "payment_reason": {
            "id": 4,
            "title": "Telefon status",
            "type": "btn",
            "typeChange": "once",
            "activeFilters": [],
            "filtersList": ["tel ko'tardi", "tel ko'tarmadi", "tel qilinmaganlar"]
        },
        "reason_days": {
            "id": 5,
            "title": "To'lov olib kelish kunlari",
            "name": "To'lov kunlari",
            "type": "select",
            "activeFilters": [],
            "filtersList": filtered_days
        },

    }

    return debt_students_list


def deleted_students_filter(location_id):
    """
    filter DeletedStudents data by location_id
    :param location_id: Locations table primary key
    :return:
    """
    user_list = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
        Students.deleted_from_group != None, Users.location_id == location_id).order_by('id').all()
    user_id = []
    for user in user_list:
        user_id.append(user.id)
    user_id = list(dict.fromkeys(user_id))

    students_list = db.session.query(DeletedStudents).join(DeletedStudents.day).options(
        contains_eager(DeletedStudents.day)).filter(
        DeletedStudents.student_id.in_([user_id for user_id in user_id])).order_by(CalendarDay.date).all()
    days = []
    groups = []
    teachers = []
    for st in students_list:
        day_info = {
            "value": st.day.id,
            "name": st.day.date.strftime("%Y-%m-%d")
        }
        days.append(day_info)

        teacher_info = {
            "value": st.teacher_id,
            "name": f" {st.teacher.user.name.title()} {st.teacher.user.surname.title()}"
        }
        teachers.append(teacher_info)

        group_info = {
            "value": st.group.id,
            "name": st.group.name.title()
        }
        groups.append(group_info)

    day_dict = {gr['value']: gr for gr in days}
    day_list = list(day_dict.values())

    day_dict = {gr['value']: gr for gr in teachers}
    teachers_list = list(day_dict.values())

    day_dict = {gr['value']: gr for gr in groups}
    group_list = list(day_dict.values())

    filters = {
        "day": {
            "id": 1,
            "title": "Kun bo'yicha",
            "name": "Kun",
            "type": "select",
            "activeFilters": [],
            "filtersList": day_list
        },
        "teacher": {
            "id": 2,
            "title": "O'qtuvchi bo'yicha",
            "name": "O'qtuvchi",
            "type": "select",
            "activeFilters": [],
            "filtersList": teachers_list
        },
        "group": {
            "id": 3,
            "title": "Guruh bo'yicha",
            "name": "Guruh",
            "type": "select",
            "activeFilters": [],
            "filtersList": group_list
        },

    }
    return filters


def deleted_reg_students_filter(location_id):
    """
    filter RegisterDeletedStudents data by location_id
    :param location_id: Locations table primary key
    :return:
    """
    user_list = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
        Students.deleted_from_register != None, Users.location_id == location_id).order_by('id').all()
    user_id = []
    for user in user_list:
        user_id.append(user.id)
    user_id = list(dict.fromkeys(user_id))
    students_list = db.session.query(RegisterDeletedStudents).join(RegisterDeletedStudents.day).options(
        contains_eager(RegisterDeletedStudents.day)).filter(
        RegisterDeletedStudents.student_id.in_([user_id for user_id in user_id])).order_by(CalendarDay.date).all()
    days = [{
        "kun": st.day.id,
        "name": st.day.date.strftime("%Y-%m-%d")
    } for st in students_list]

    day_dict = {gr['kun']: gr for gr in days}
    day_list = list(day_dict.values())
    filters = {
        "deleted_date": {
            "id": 1,
            "title": "Kun bo'yicha",
            "name": "Kun",
            "type": "select",
            "activeFilters": [],
            "filtersList": day_list
        },
    }
    return filters


def old_current_dates(group_id=0, observation=False):
    """

    :param group_id: Groups primary key
    :return: old month days and current month days
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    current_month = datetime.now().month
    old_year = datetime.now().year
    old_month = datetime.now().month - 1
    old_month2 = datetime.now().month - 1
    if old_month == 0:
        old_month = "12"
        old_year = old_year - 1
    if len(str(old_month)) == 1:
        old_month = "0" + str(old_month)
    date = str(old_year) + "-" + str(old_month)
    date = datetime.strptime(date, "%Y-%m")
    current_year = datetime.now().year
    current_day = datetime.now().day
    week_list = []
    time_table_group = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).order_by(
        Group_Room_Week.id).all()
    for time_table in time_table_group:
        week_list.append(time_table.week.eng_name)
    day_list = []
    plan_days = []
    number_days = number_of_days_in_month(current_year, current_month)
    for num in range(1, number_days + 1):
        plan_days.append(num)

        if current_day >= num:
            day_list.append(num)
    old_days = []
    number_days = number_of_days_in_month(old_year, old_month2)
    for num in range(1, number_days + 1):
        old_days.append(num)

    day_list.sort()
    old_days.sort()
    if group_id != 0:
        day_list = weekday_from_date(day_list, current_month, current_year, week_list)
        old_days = weekday_from_date(old_days, old_month, old_year, week_list)
    if current_day > 7:
        data = [
            {
                "name": calendar_month.date.strftime("%h"),
                "value": calendar_month.date.strftime('%m'),
                "days": day_list
            }
        ]
    else:
        data = [
            {
                "name": calendar_month.date.strftime("%h"),
                "value": calendar_month.date.strftime('%m'),
                "days": day_list
            },
            {
                "name": date.strftime("%h"),
                "value": date.strftime('%m'),
                "days": old_days
            }
        ]

    return data


def update_lesson_plan(group_id):
    time_table_group = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).order_by(
        Group_Room_Week.id).all()
    week_list = []
    for time_table in time_table_group:
        week_list.append(time_table.week.eng_name)
    current_year = datetime.now().year
    current_month = datetime.now().month
    plan_days = []
    number_days = number_of_days_in_month(current_year, current_month)
    for num in range(1, number_days + 1):
        plan_days.append(num)
    plan_days = weekday_from_date(plan_days, current_month, current_year, week_list)
    group = Groups.query.filter(Groups.id == group_id).first()
    current_day2 = datetime.now().day
    current_day2 += 5
    for day in plan_days:
        if current_day2 >= day:
            date_get = str(current_year) + "-" + str(current_month) + "-" + str(day)
            date_get = datetime.strptime(date_get, "%Y-%m-%d")
            exist = LessonPlan.query.filter(LessonPlan.date == date_get, LessonPlan.group_id == group_id,
                                            LessonPlan.teacher_id == group.teacher_id).first()
            if not exist:
                lesson_plan_add = LessonPlan(group_id=group_id, teacher_id=group.teacher_id, date=date_get)
                lesson_plan_add.add()


def weekday_from_date(day_list, month, year, week_list):
    """
    check day data in week list
    :param day_list:
    :param month:
    :param year:
    :param week_list:
    :return: week name
    """
    filtered_days = []
    for days in day_list:
        if calendar.day_name[
            date(day=days, month=int(month), year=year).weekday()
        ] in week_list:
            filtered_days.append(days)
    return filtered_days
