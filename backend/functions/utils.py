from app import request, db, classroom_server
import requests
from backend.models.models import CalendarDay, CalendarMonth, CalendarYear, AccountingPeriod, Professions, PaymentTypes, \
    Week, AccountingInfo, TeacherSalaries, Teachers, TeacherSalary, UserBooks, Users, StaffSalary, StaffSalaries, \
    TeacherBlackSalary, Locations, Roles, contains_eager, desc, or_, GroupReason
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import uuid
from datetime import datetime

api = '/api'


def today():
    get_today = datetime.today()
    return get_today


def new_year():
    get_year = datetime.strftime(today(), "%Y")
    get_year = datetime.strptime(get_year, "%Y")
    return get_year


def new_today():
    current_day = datetime.strftime(today(), "%Y-%m-%d")
    current_day = datetime.strptime(current_day, "%Y-%m-%d")
    return current_day


def new_month():
    get_month = datetime.strftime(today(), "%Y-%m")
    get_month = datetime.strptime(get_month, "%Y-%m")
    return get_month


def refreshdatas(location_id=0):
    """
    update datas by current day , month and year
    :param location_id:
    :return:
    """
    calendar_year = CalendarYear.query.filter(CalendarYear.date == new_year()).first()
    if not calendar_year:
        calendar_year = CalendarYear(date=new_year())
        db.session.add(calendar_year)
        db.session.commit()

    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == new_month(),
                                                CalendarMonth.year_id == calendar_year.id).first()

    if not calendar_month:
        calendar_month = CalendarMonth(date=new_month(), year_id=calendar_year.id)
        db.session.add(calendar_month)
        db.session.commit()

    calendar_day = CalendarDay.query.filter(CalendarDay.date == new_today(),
                                            CalendarDay.month_id == calendar_month.id).first()

    if not calendar_day:
        calendar_day = CalendarDay(date=new_today(), month_id=calendar_month.id)
        db.session.add(calendar_day)
        db.session.commit()
    update_all_datas()
    update_period(location_id)
    account_period = AccountingPeriod.query.order_by(desc(AccountingPeriod.id)).first()
    CalendarDay.query.filter(CalendarDay.id == calendar_day.id).update({'account_period_id': account_period.id})
    db.session.commit()


def update_period(location_id):
    """
    update datas in AccountingPeriod by datetime
    :param location_id: Locations primary key
    :return:
    """
    calendar_year = CalendarYear.query.filter(CalendarYear.date == new_year()).first()

    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == new_month(),
                                                CalendarMonth.year_id == calendar_year.id).first()
    calendar_day = CalendarDay.query.filter(CalendarDay.date == new_today(),
                                            CalendarDay.month_id == calendar_month.id).first()
    new_from_date = "2022" + "-" + "08" + "-" + "11"
    new_to_date = "2022" + "-" + "09" + "-" + "10"
    new_from_date = datetime.strptime(new_from_date, "%Y-%m-%d")
    new_to_date = datetime.strptime(new_to_date, "%Y-%m-%d")
    accounting_period = AccountingPeriod.query.filter(AccountingPeriod.from_date == new_from_date,
                                                      AccountingPeriod.to_date == new_to_date).first()
    if not accounting_period:
        accounting_period = AccountingPeriod(from_date=new_from_date, to_date=new_to_date,
                                             month_id=calendar_month.id,
                                             year_id=calendar_year.id)
        db.session.add(accounting_period)
        db.session.commit()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    if accounting_period and accounting_period.from_date and accounting_period.to_date:
        old_from_day = datetime.strftime(accounting_period.from_date, "%d")
        old_to_day = datetime.strftime(accounting_period.to_date, "%d")

        old_from_date = datetime.strftime(accounting_period.from_date, "%m")
        old_from_year = datetime.strftime(accounting_period.from_date, "%Y")

        old_to_date = datetime.strftime(accounting_period.to_date, "%m")
        old_to_year = datetime.strftime(accounting_period.to_date, "%Y")

        old_from_date = int(old_from_date) + 1
        old_to_date = int(old_to_date) + 1
        if old_from_date == 13:
            old_from_date = "01"
            old_from_year = int(old_from_year) + 1
        if old_to_date == 13:
            old_to_date = "01"
            old_to_year = int(old_to_year) + 1

        if len(str(old_from_date)) == 1:
            old_from_date = "0" + str(old_from_date)
        if len(str(old_to_date)) == 1:
            old_to_date = "0" + str(old_to_date)

        new_from_date = str(old_from_year) + "-" + str(old_from_date) + "-" + str(old_from_day)
        new_from_date = datetime.strptime(new_from_date, "%Y-%m-%d")
        new_to_date = str(old_to_year) + "-" + str(old_to_date) + "-" + str(old_to_day)
        new_to_date = datetime.strptime(new_to_date, "%Y-%m-%d")
        if calendar_day:
            if calendar_day.date > accounting_period.to_date:
                accounting_period = AccountingPeriod.query.filter(AccountingPeriod.from_date == new_from_date,
                                                                  AccountingPeriod.to_date == new_to_date).first()
                if not accounting_period:
                    accounting_period = AccountingPeriod(from_date=new_from_date, to_date=new_to_date,
                                                         month_id=calendar_month.id,
                                                         year_id=calendar_year.id)
                    db.session.add(accounting_period)
                    db.session.commit()


def update_all_datas():
    new_month = datetime.strftime(today(), "%Y-%m")
    new_month = datetime.strptime(new_month, "%Y-%m")
    calendar_year = CalendarYear.query.filter(CalendarYear.date == new_year()).first()

    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == new_month,
                                                CalendarMonth.year_id == calendar_year.id).first()
    calendar_day = CalendarDay.query.filter(CalendarDay.date == new_today(),
                                            CalendarDay.month_id == calendar_month.id).first()
    current_month = datetime.strftime(today(), "%Y-%m")

    new_month = datetime.strptime(current_month, "%Y-%m")
    old_month = new_month - relativedelta(month=1)

    location1 = "Xo'jakent"
    location2 = "Gazalkent"
    location3 = "Chirchiq"
    location4 = "Sergeli"
    location5 = "Nurafshon"
    location_1 = Locations.query.filter(Locations.name == location1).first()
    if not location_1:
        location_1 = Locations(name=location1, calendar_day=calendar_day.id, calendar_year=calendar_year.id,
                               calendar_month=calendar_month.id)
        db.session.add(location_1)
        db.session.commit()
    location_2 = Locations.query.filter(Locations.name == location2).first()
    if not location_2:
        location_2 = Locations(name=location2, calendar_day=calendar_day.id, calendar_year=calendar_year.id,
                               calendar_month=calendar_month.id)
        db.session.add(location_2)
        db.session.commit()

    location_3 = Locations.query.filter(Locations.name == location3).first()
    if not location_3:
        location_3 = Locations(name=location3, calendar_day=calendar_day.id, calendar_year=calendar_year.id,
                               calendar_month=calendar_month.id)
        db.session.add(location_3)
        db.session.commit()
    location_4 = Locations.query.filter(Locations.name == location4).first()
    if not location_4:
        location_4 = Locations(name=location4, calendar_day=calendar_day.id, calendar_year=calendar_year.id,
                               calendar_month=calendar_month.id)
        db.session.add(location_4)
        db.session.commit()

    location_5 = Locations.query.filter(Locations.name == location5).first()
    if not location_5:
        location_5 = Locations(name=location5, calendar_day=calendar_day.id, calendar_year=calendar_year.id,
                               calendar_month=calendar_month.id)
        db.session.add(location_5)
        db.session.commit()

    click = "click"
    cash = "cash"
    bank = "bank"

    cash_get = PaymentTypes.query.filter(PaymentTypes.name == cash).first()
    if not cash_get:
        cash_get = PaymentTypes(name=cash)
        db.session.add(cash_get)
        db.session.commit()
    click_get = PaymentTypes.query.filter(PaymentTypes.name == click).first()
    if not click_get:
        click_get = PaymentTypes(name=click)
        db.session.add(click_get)
        db.session.commit()

    bank_get = PaymentTypes.query.filter(PaymentTypes.name == bank).first()
    if not bank_get:
        bank_get = PaymentTypes(name=bank)
        db.session.add(bank_get)
        db.session.commit()

    methodist = Professions.query.filter(Professions.name == "Methodist").first()
    if not methodist:
        methodist = Professions(name="Methodist")
        methodist.add()

    methodist = Roles.query.filter(Roles.type_role == "methodist", Roles.role == "d32q69n53").first()
    if not methodist:
        methodist = Roles(type_role="methodist", role="d32q69n53")
        methodist.add()

    editor = Professions.query.filter(Professions.name == "Muxarir").first()
    if not editor:
        editor = Professions(name="Muxarir")
        editor.add()

    editor = Roles.query.filter(Roles.type_role == "muxarir", Roles.role == "n41c88z45").first()
    if not editor:
        editor = Roles(type_role="muxarir", role="n41c88z45")
        editor.add()

    add_reason = GroupReason.query.filter(GroupReason.reason == "O'qituvchi yoqmadi").first()
    if not add_reason:
        add_reason = GroupReason(reason="O'qituvchi yoqmadi")
        add_reason.add()

    add_reason = GroupReason.query.filter(GroupReason.reason == "Pul oilaviy sharoit").first()
    if not add_reason:
        add_reason = GroupReason(reason="Pul oilaviy sharoit")
        add_reason.add()
    add_reason = GroupReason.query.filter(GroupReason.reason == "O'quvchi o'qishni eplolmadi").first()
    if not add_reason:
        add_reason = GroupReason(reason="O'quvchi o'qishni eplolmadi")
        add_reason.add()

    add_reason = GroupReason.query.filter(GroupReason.reason == "Boshqa").first()
    if not add_reason:
        add_reason = GroupReason(reason="Boshqa")
        add_reason.add()

    add_reason = GroupReason.query.filter(GroupReason.reason == "Kursni tamomladi").first()
    if not add_reason:
        add_reason = GroupReason(reason="Kursni tamomladi")
        add_reason.add()


def find_calendar_date(date_day=None, date_month=None, date_year=None):
    """Find or parse calendar date entities."""
    if date_day:
        day = CalendarDay.query.filter(CalendarDay.date == date_day).first()
        month = CalendarMonth.query.filter(CalendarMonth.date == date_month).first()
        year = CalendarYear.query.filter(CalendarYear.date == date_year).first()
        if not year:
            year = CalendarYear(date=new_year())
            db.session.add(year)
            db.session.commit()
        if not month:
            month = CalendarMonth(date=new_month(), year_id=year.id)
            db.session.add(month)
            db.session.commit()
        if not day:
            day = CalendarDay(date=new_today(), month_id=month.id)
            db.session.add(day)
            db.session.commit()
        return year, month, day
    else:
        day = CalendarDay.query.filter(CalendarDay.date == new_today()).first()
        month = CalendarMonth.query.filter(CalendarMonth.date == new_month()).first()
        year = CalendarYear.query.filter(CalendarYear.date == new_year()).first()
        if not year:
            year = CalendarYear(date=new_year())
            db.session.add(year)
            db.session.commit()
        if not month:
            month = CalendarMonth(date=new_month(), year_id=year.id)
            db.session.add(month)
            db.session.commit()
        if not day:
            day = CalendarDay(date=new_today(), month_id=month.id)
            db.session.add(day)
            db.session.commit()

        year = CalendarYear.query.filter_by(date=new_year()).first()
        month = CalendarMonth.query.filter_by(date=new_month(), year_id=year.id).first()
        day = CalendarDay.query.filter_by(date=new_today(), month_id=month.id).first()
        return year, month, day


def get_json_field(field_name):
    """Safely get a field from the JSON request body."""
    return request.get_json().get(field_name)


def iterate_models(model, relationship=None, entire=False):
    list_items = []
    for subject in model:
        list_items.append(subject.convert_json(entire=entire))
    return list_items


def hour2():
    hour = datetime.strftime(today(), "%Y/%m/%d/%H/%M")
    hour2 = datetime.strptime(hour, "%Y/%m/%d/%H/%M")
    return hour2


def number_of_days_in_month(year, month):
    if month == 0:
        month = 1
    return monthrange(year, month)[1]


def update_account(account_id):
    refreshdatas()
    accounting_info = AccountingInfo.query.filter(AccountingInfo.id == account_id).first()
    old_cash = 0
    old_account_period = AccountingPeriod.query.filter(
        AccountingPeriod.id < accounting_info.account_period_id).order_by(desc(
        AccountingPeriod.id)).first()

    if old_account_period:

        old_accounting_info = AccountingInfo.query.filter(AccountingInfo.account_period_id == old_account_period.id,
                                                          AccountingInfo.payment_type_id == accounting_info.payment_type_id,
                                                          AccountingInfo.location_id == accounting_info.location_id).first()
        if old_accounting_info and old_accounting_info.current_cash:
            old_cash = old_accounting_info.current_cash

    all_payments = 0
    teachers_salaries = 0
    all_staff_salaries = 0
    all_overhead = 0
    all_capital = 0
    if accounting_info.all_payments:
        all_payments = accounting_info.all_payments
    if accounting_info.all_teacher_salaries:
        teachers_salaries = accounting_info.all_teacher_salaries
    if accounting_info.all_staff_salaries:
        all_staff_salaries = accounting_info.all_staff_salaries
    if accounting_info.all_overhead:
        all_overhead = accounting_info.all_overhead
    if accounting_info.all_capital:
        all_capital = accounting_info.all_capital
    result = (all_payments + old_cash) - (teachers_salaries + all_staff_salaries + all_overhead + all_capital)

    AccountingInfo.query.filter(AccountingInfo.id == accounting_info.id).update(
        {'current_cash': result, "old_cash": old_cash})
    db.session.commit()


def update_salary(teacher_id):
    refreshdatas()
    teacher = Teachers.query.filter(Teachers.user_id == teacher_id).first()
    attendance_history = TeacherSalary.query.filter(TeacherSalary.teacher_id == teacher.id).filter(
        or_(TeacherSalary.status == False, TeacherSalary.status == None)).all()
    black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.teacher_id == teacher.id).filter(
        or_(TeacherBlackSalary.status == False, TeacherBlackSalary.status == None)).all()
    black_salary = 0
    for salary in black_salaries:
        black_salary += salary.total_salary
    taken_money = 0
    total_salary = 0
    for attendance in attendance_history:

        if attendance.total_salary:
            total_salary += attendance.total_salary
        if attendance.taken_money:
            taken_money += attendance.taken_money
    result = total_salary - (taken_money + black_salary)
    Users.query.filter(Users.id == teacher.user_id).update({'balance': result})
    db.session.commit()


def update_staff_salary_id(salary_id):
    staff_salary = StaffSalary.query.filter(StaffSalary.id == salary_id).first()
    salaries = StaffSalaries.query.filter(StaffSalaries.salary_id == salary_id).all()
    user_books = UserBooks.query.filter(UserBooks.salary_id == salary_id).all()
    salary = 0
    for salary_get in salaries:
        salary += salary_get.payment_sum
    for book_payment_get in user_books:
        salary += book_payment_get.payment_sum
    staff_salary.remaining_salary = staff_salary.total_salary - salary
    staff_salary.taken_money = salary
    db.session.commit()


def update_teacher_salary_id(salary_id):
    teacher_salary = TeacherSalary.query.filter(TeacherSalary.id == salary_id).first()
    salaries = TeacherSalaries.query.filter(TeacherSalaries.salary_location_id == salary_id).all()
    user_books = UserBooks.query.filter(UserBooks.salary_location_id == salary_id).all()
    black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.teacher_id == teacher_salary.teacher_id,
                                                     TeacherBlackSalary.status == False,
                                                     TeacherBlackSalary.salary_id == salary_id).all()
    black_salary = 0
    for salary in black_salaries:
        black_salary += salary.total_salary
    salary = 0
    for salary_get in salaries:
        salary += salary_get.payment_sum
    for book_payment_get in user_books:
        salary += book_payment_get.payment_sum
    teacher_salary.remaining_salary = teacher_salary.total_salary - (salary + black_salary)
    teacher_salary.taken_money = salary
    db.session.commit()


def refresh_age(user_id):
    user = Users.query.filter(Users.id == user_id).first()
    birth_year = user.born_year
    age = datetime.now().year - birth_year
    Users.query.filter(Users.id == user_id).update({"age": age})
    db.session.commit()


def update_week(location_id):
    monday = "Dushanba"
    tuesday = "Seshanba"
    wednesday = "Chorshanba"
    thursday = "Payshanba"
    friday = "Juma"
    saturday = "Shanba"
    sunday = "Yakshanba"

    monday_date = Week.query.filter(Week.name == monday, Week.location_id == location_id).first()
    if not monday_date:
        monday_date = Week(name=monday, location_id=location_id)
        db.session.add(monday_date)
        db.session.commit()
    else:
        Week.query.filter(Week.name == monday, Week.location_id == location_id).update({
            "eng_name": "Monday",
            "order": 1
        })
        db.session.commit()
    tuesday_date = Week.query.filter(Week.name == tuesday, Week.location_id == location_id).first()
    if not tuesday_date:
        tuesday_date = Week(name=tuesday, location_id=location_id)
        db.session.add(tuesday_date)
        db.session.commit()
    Week.query.filter(Week.name == tuesday, Week.location_id == location_id).update({
        "eng_name": "Tuesday",
        "order": 2
    })
    db.session.commit()
    wednesday_date = Week.query.filter(Week.name == wednesday, Week.location_id == location_id).first()
    if not wednesday_date:
        wednesday_date = Week(name=wednesday, location_id=location_id)
        db.session.add(wednesday_date)
        db.session.commit()
    Week.query.filter(Week.name == wednesday, Week.location_id == location_id).update({
        "eng_name": "Wednesday",
        "order": 3
    })
    db.session.commit()
    thursday_date = Week.query.filter(Week.name == thursday, Week.location_id == location_id).first()
    if not thursday_date:
        thursday_date = Week(name=thursday, location_id=location_id)
        db.session.add(thursday_date)
        db.session.commit()
    Week.query.filter(Week.name == thursday, Week.location_id == location_id).update({
        "eng_name": "Thursday",
        "order": 4
    })
    db.session.commit()
    friday_date = Week.query.filter(Week.name == friday, Week.location_id == location_id).first()
    if not friday_date:
        friday_date = Week(name=friday, location_id=location_id)
        db.session.add(friday_date)
        db.session.commit()
    Week.query.filter(Week.name == friday, Week.location_id == location_id).update({
        "eng_name": "Friday",
        "order": 5
    })
    db.session.commit()
    saturday_date = Week.query.filter(Week.name == saturday, Week.location_id == location_id).first()
    if not saturday_date:
        saturday_date = Week(name=saturday, location_id=location_id)
        db.session.add(saturday_date)
        db.session.commit()
    Week.query.filter(Week.name == saturday, Week.location_id == location_id).update({
        "eng_name": "Saturday",
        "order": 6
    })
    db.session.commit()
    sunday_date = Week.query.filter(Week.name == sunday, Week.location_id == location_id).first()
    if not sunday_date:
        sunday_date = Week(name=sunday, location_id=location_id)
        db.session.add(sunday_date)
        db.session.commit()
    Week.query.filter(Week.name == sunday, Week.location_id == location_id).update({
        "eng_name": "Sunday",
        "order": 7
    })
    db.session.commit()


def remove_duplicates_by_key(obj_list, key):
    """Removes duplicates from a list of objects/dictionaries based on a specific key.

    Args:
    obj_list (list): The list of objects/dictionaries from which duplicates need to be removed.
    key: The key based on which duplicates will be identified and removed.

    Returns:
    list: A new list with duplicates removed.
    """
    seen = set()
    result = []
    for obj in obj_list:
        val = obj[key] if isinstance(obj, dict) else getattr(obj, key, None)
        if val not in seen:
            seen.add(val)
            result.append(obj)
    return result


def remove_items_create_group(list_block):
    filtered_teachers = []

    for teacher in list_block:
        added_to_existing = False
        for merged in filtered_teachers:
            if merged['id'] == teacher['id']:
                if teacher['shift']:
                    merged['error'] = True
                    merged['color'] = 'red'
                    merged['shift'] += f" {teacher['shift']} " + " \n"

                added_to_existing = True
            if added_to_existing:
                break
        if not added_to_existing:
            filtered_teachers.append(teacher)

    return filtered_teachers


def check_exist_id():
    id = uuid.uuid1()
    user_id = id.hex[0:35]
    exist_user = Users.query.filter(Users.user_id == user_id).first()
    while exist_user:
        id = uuid.uuid1()
        user_id = id.hex[0:35]
        exist_user = Users.query.filter(Users.user_id == user_id).first()
    return user_id


def send_user_info(user):
    requests.post(f"{classroom_server}/api/update_user_info", json={
        "user": user.convert_json(),
    })
