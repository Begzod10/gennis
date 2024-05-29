from app import app, db, jsonify, contains_eager, request, desc, or_
from backend.functions.utils import api, find_calendar_date, get_json_field, update_staff_salary_id, \
    update_teacher_salary_id, update_salary
from backend.models.models import Teachers, TeacherSalary, StaffSalary, Staff, PaymentTypes, DeletedStaffSalaries, \
    UserBooks, StaffSalaries, TeacherSalaries, DeletedTeacherSalaries, AccountingPeriod, CalendarMonth, StudentPayments, \
    Users, CalendarYear, Locations, TeacherBlackSalary
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.functions.debt_salary_update import staff_salary_update
from backend.functions.utils import iterate_models
from pprint import pprint


@app.route(f'{api}/salary_info/<user_id>')
@jwt_required()
def salary_info(user_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    platform_user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    user = Users.query.filter(Users.id == user_id).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    staff = Staff.query.filter(Staff.user_id == user.id).first()

    location = Locations.query.filter(Locations.id == user.location_id).first()
    locations = Locations.query.order_by(Locations.id).all()

    if teacher:
        salary = TeacherSalary.query.filter(TeacherSalary.teacher_id == teacher.id).all()
        years = CalendarYear.query.filter(CalendarYear.id.in_([year.calendar_year for year in salary]))
    elif staff:
        salary = StaffSalary.query.filter(StaffSalary.staff_id == staff.id).all()
        years = CalendarYear.query.filter(CalendarYear.id.in_([year.calendar_year for year in salary]))

    if teacher or platform_user.director:
        if teacher:
            locations_list = [location.convert_json() for location in teacher.locations]
        else:
            locations_list = [location.convert_json() for location in locations]
    elif staff:
        locations_list = [location.convert_json()]
    else:
        locations_list = [location.convert_json()]

    return jsonify({
        "locations": locations_list,
        "years": iterate_models(years),
        "current_year": calendar_year.id
    })


@app.route(f'{api}/block_salary/<int:user_id>/<int:location_id>/<year_id>')
def block_salary(user_id, location_id, year_id):
    staff_salary_update()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()
    teacher_salary_list = []
    if teacher:
        teacher_salaries = TeacherSalary.query.filter(TeacherSalary.teacher_id == teacher.id,
                                                      TeacherSalary.location_id == location_id,
                                                      TeacherSalary.calendar_year == year_id).order_by(
            desc(TeacherSalary.id)).all()
        for salary in teacher_salaries:
            teacher_black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.salary_id == salary.id,
                                                                     TeacherBlackSalary.teacher_id == teacher.id,
                                                                     TeacherBlackSalary.status == False).all()
            black_salary = 0
            for black in teacher_black_salaries:
                black_salary += black.total_salary
            if salary.remaining_salary:
                residue = salary.remaining_salary
            elif salary.taken_money == salary.total_salary:
                residue = 0
            else:
                residue = salary.total_salary
            info = {
                "id": salary.id,
                "salary": salary.total_salary,
                "residue": residue,
                "taken_salary": salary.taken_money,
                "black_salary": black_salary,
                "date": salary.month.date.strftime("%Y-%m")
            }
            teacher_salary_list.append(info)
    else:
        staff_salaries = StaffSalary.query.filter(StaffSalary.staff_id == staff.id,
                                                  StaffSalary.location_id == location_id,
                                                  StaffSalary.calendar_year == year_id).order_by(
            desc(StaffSalary.id)).all()
        for salary in staff_salaries:
            if salary.remaining_salary:
                residue = salary.remaining_salary
            elif salary.taken_money == salary.total_salary:
                residue = 0
            else:
                residue = salary.total_salary
            info = {
                "id": salary.id,
                "salary": salary.total_salary,
                "residue": residue,
                "taken_salary": salary.taken_money,
                "date": salary.month.date.strftime("%Y-%m")
            }
            teacher_salary_list.append(info)

    return jsonify({
        "data": teacher_salary_list
    })


@app.route(f'{api}/teacher_salary/<int:user_id>/<int:location_id>')
@jwt_required()
def teacher_salary(user_id, location_id):
    """

    :param user_id: User table primary key
    :param location_id: Location table primary key
    :return: TeacherSalary table and StaffSalary table data
    """
    staff_salary_update()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()
    teacher_salary_list = []
    if teacher:
        teacher_salaries = TeacherSalary.query.filter(TeacherSalary.teacher_id == teacher.id,
                                                      TeacherSalary.location_id == location_id,
                                                      ).order_by(
            desc(TeacherSalary.id)).all()

        for salary in teacher_salaries:
            teacher_black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.salary_id == salary.id,
                                                                     TeacherBlackSalary.teacher_id == teacher.id,
                                                                     TeacherBlackSalary.status == False).all()
            black_salary = 0
            for black in teacher_black_salaries:
                black_salary += black.total_salary

            if salary.remaining_salary:
                residue = salary.remaining_salary
            elif salary.taken_money == salary.total_salary:
                residue = 0
            else:
                residue = salary.total_salary

            info = {
                "id": salary.id,
                "salary": salary.total_salary,
                "residue": residue,
                "taken_salary": salary.taken_money,
                "black_salary": black_salary,
                "date": salary.month.date.strftime("%Y-%m")
            }
            teacher_salary_list.append(info)

    else:
        staff_salaries = StaffSalary.query.filter(StaffSalary.staff_id == staff.id,
                                                  StaffSalary.location_id == location_id).order_by(
            desc(StaffSalary.id)).all()

        for salary in staff_salaries:
            if salary.remaining_salary:
                residue = salary.remaining_salary
            elif salary.taken_money == salary.total_salary:
                residue = 0
            else:
                residue = salary.total_salary
            info = {
                "id": salary.id,
                "salary": salary.total_salary,
                "residue": residue,
                "taken_salary": salary.taken_money,
                "date": salary.month.date.strftime("%Y-%m")
            }
            teacher_salary_list.append(info)

    return jsonify({
        "data": teacher_salary_list
    })


@app.route(f'{api}/teacher_salary_inside/<int:salary_id>/<int:user_id>')
@jwt_required()
def teacher_salary_inside(salary_id, user_id):
    """

    :param salary_id: TeacherSalary and StaffSalary primary key
    :param user_id: User table primary key
    :return: TeacherSalaries table and StaffSalaries table data
    """
    staff_salary_update()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()

    result = 0
    black_salary = 0
    if teacher:
        teacher_black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.salary_id == salary_id,
                                                                 TeacherBlackSalary.teacher_id == teacher.id,
                                                                 TeacherBlackSalary.status == False).all()

        for black in teacher_black_salaries:
            black_salary += black.total_salary
        salary = TeacherSalary.query.filter(TeacherSalary.id == salary_id).first()

        salaries = TeacherSalaries.query.filter(TeacherSalaries.salary_location_id == salary_id).order_by(
            TeacherSalaries.id).all()
        user_books = UserBooks.query.filter(UserBooks.user_id == user_id,
                                            UserBooks.salary_location_id == salary_id).order_by(UserBooks.id).all()
        book_payments = 0
        for pay in user_books:
            book_payments += pay.payment_sum
        all_salaries = 0
        for sal in salaries:
            all_salaries += sal.payment_sum

        result = salary.total_salary - (all_salaries + black_salary + book_payments)
        TeacherSalary.query.filter(TeacherSalary.id == salary_id).update({
            "remaining_salary": result,
            "taken_money": all_salaries,
        })
        db.session.commit()
        update_teacher_salary_id(salary_id)

    else:
        salary = StaffSalary.query.filter(StaffSalary.id == salary_id).first()
        user_books = UserBooks.query.filter(UserBooks.user_id == user_id,
                                            UserBooks.salary_id == salary_id).order_by(UserBooks.id).all()
        update_staff_salary_id(salary_id)
        salaries = StaffSalaries.query.filter(StaffSalaries.salary_id == salary_id).order_by(
            StaffSalaries.id).all()
    list_salaries = [{
        "id": sal.id,
        "salary": sal.payment_sum,
        "reason": sal.reason,
        "payment_type": sal.payment_type.name,
        "date": sal.day.date.strftime("%Y-%m-%d"),
        "status": False
    } for sal in salaries]

    for book in user_books:
        list_salaries.append(book.convert_json())

    if salary.remaining_salary:
        exist_money = salary.remaining_salary
    else:
        exist_money = salary.total_salary
    return jsonify({
        "data": {
            "salary": salary.total_salary,
            "residue": salary.remaining_salary,
            "taken_salary": salary.taken_money,
            "exist_salary": exist_money,
            "month": salary.month.date.strftime("%Y-%m"),
            "data": list_salaries,
            "black_salary": black_salary
        }
    })


@app.route(f'{api}/black_salary/<teacher_id>')
@jwt_required()
def black_salary(teacher_id):
    teacher = Teachers.query.filter(Teachers.user_id == teacher_id).first()
    black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.teacher_id == teacher.id,
                                                     ).filter(
        or_(TeacherBlackSalary.status == False, TeacherBlackSalary.status == None)).order_by(
        TeacherBlackSalary.id).all()
    group_names = []
    for gr in teacher.group:
        if gr.deleted != True and gr.status == True:
            group_names.append(gr.name)
    return jsonify({
        "groups": group_names,
        "students": iterate_models(black_salaries)
    })


@app.route(f'{api}/teacher_salary_deleted_inside/<int:salary_id>/<int:user_id>')
@jwt_required()
def teacher_salary_deleted_inside(salary_id, user_id):
    """

    :param salary_id: TeacherSalary and StaffSalary primary key
    :param user_id: User table primary key
    :return: DeletedTeacherSalaries table and DeletedStaffSalaries table data
    """
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    list_salaries = []
    if teacher:
        salary = TeacherSalary.query.filter(TeacherSalary.id == salary_id).first()

        salaries = DeletedTeacherSalaries.query.filter(
            DeletedTeacherSalaries.salary_location_id == salary_id).order_by(
            DeletedTeacherSalaries.id).all()
    else:
        salary = StaffSalary.query.filter(StaffSalary.id == salary_id).first()

        salaries = DeletedStaffSalaries.query.filter(DeletedStaffSalaries.salary_id == salary_id).order_by(
            DeletedStaffSalaries.id).all()

    list_salaries.append(
        {
            "id": sal.id,
            "salary": sal.payment_sum,
            "reason": sal.reason_deleted,
            "payment_type": sal.payment_type.name,
            "date": sal.day.date.strftime("%Y-%m-%d")
        } for sal in salaries
    )
    return jsonify({
        "data": {
            "salary": salary.total_salary,
            "residue": salary.remaining_salary,
            "taken_salary": salary.taken_money,
            "month": salary.month.date.strftime("%Y-%m"),
            "data": list_salaries
        }
    })


@app.route(f'{api}/salary_give_teacher/<int:salary_id>/<int:user_id>', methods=['POST'])
@jwt_required()
def salary_give_teacher(salary_id, user_id):
    """
    add  data to TeacherSalaries and StaffSalaries
    :param salary_id: TeacherSalary and StaffSalary primary key
    :param user_id: User table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()
    get_salary = int(get_json_field('payment'))
    reason = get_json_field('reason')
    payment_type = int(get_json_field('typePayment'))
    payment_type_id = PaymentTypes.query.filter(PaymentTypes.id == payment_type).first()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    if teacher:
        teacher_cash = TeacherSalary.query.filter(TeacherSalary.id == salary_id).first()
        if teacher_cash.remaining_salary:
            total_salary = teacher_cash.remaining_salary
        else:
            total_salary = teacher_cash.total_salary
        if get_salary > total_salary:
            return jsonify({
                "success": False,
                "msg": "Kiritilgan summa miqdori umumiy oylik miqdoridan kop"
            })
        else:
            add = TeacherSalaries(payment_sum=get_salary, reason=reason, payment_type_id=payment_type_id.id,
                                  teacher_id=teacher_cash.teacher_id, location_id=teacher_cash.location_id,
                                  calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                  calendar_year=calendar_year.id, account_period_id=accounting_period.id,
                                  salary_location_id=teacher_cash.id)
            db.session.add(add)
            db.session.commit()

            update_teacher_salary_id(salary_id)
    else:
        staff_cash = StaffSalary.query.filter(StaffSalary.id == salary_id).first()
        if staff_cash.remaining_salary:
            total_salary = staff_cash.remaining_salary
        else:
            total_salary = staff_cash.total_salary
        if get_salary > total_salary:
            return jsonify({
                "success": False,
                "msg": "Kiritilgan summa miqdori umumiy oylik miqdoridan kop"
            })
        else:
            add = StaffSalaries(payment_sum=get_salary, reason=reason, payment_type_id=payment_type_id.id,
                                staff_id=staff_cash.staff_id, location_id=staff_cash.location_id,
                                calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                                calendar_year=calendar_year.id, account_period_id=accounting_period.id,
                                salary_id=staff_cash.id, profession_id=staff.profession_id)
            db.session.add(add)
            db.session.commit()
            update_staff_salary_id(salary_id)

    return jsonify({
        "success": True,
        "msg": "Oylik berildi"
    })


@app.route(f'{api}/delete_salary_teacher/<int:salary_id>/<int:user_id>', methods=['POST'])
@jwt_required()
def delete_salary_teacher(salary_id, user_id):
    """
    add data to DeletedTeacherSalaries and DeletedStaffSalaries
    delete data from TeacherSalaries and DeletedStaffSalaries
    :param salary_id: TeacherSalary and StaffSalary primary key
    :param user_id: User table primary key
    :return:
    """
    reason = get_json_field('otherReason')
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    if teacher:

        teacher_salary = TeacherSalaries.query.filter(TeacherSalaries.id == salary_id).first()
        teacher = Teachers.query.filter(Teachers.id == teacher_salary.teacher_id).first()
        teacher_cash = TeacherSalary.query.filter(TeacherSalary.id == teacher_salary.salary_location_id,
                                                  TeacherSalary.teacher_id == teacher.id,
                                                  TeacherSalary.location_id == teacher_salary.location_id,
                                                  TeacherSalary.taken_money != None).first()
        result = teacher_cash.taken_money - teacher_salary.payment_sum

        remaining_salary = teacher_cash.total_salary - result
        if remaining_salary == teacher_cash.total_salary:
            remaining_salary = 0

        TeacherSalary.query.filter(TeacherSalary.id == teacher_cash.id).update(
            {"taken_money": result, "remaining_salary": remaining_salary, "status": False})
        db.session.commit()

        deleted_salary = DeletedTeacherSalaries(payment_sum=teacher_salary.payment_sum, reason=teacher_salary.reason,
                                                payment_type_id=teacher_salary.payment_type_id,
                                                teacher_id=teacher_cash.teacher_id, reason_deleted=reason,
                                                location_id=teacher_cash.location_id,
                                                calendar_month=teacher_salary.calendar_month,
                                                calendar_day=teacher_salary.calendar_day,
                                                calendar_year=teacher_salary.calendar_year,
                                                account_period_id=teacher_salary.account_period_id,
                                                salary_location_id=teacher_salary.salary_location_id,
                                                deleted_date=calendar_day.date)
        db.session.add(deleted_salary)
        db.session.commit()
        db.session.delete(teacher_salary)
        db.session.commit()
        update_salary(teacher_id=teacher.user_id)
    else:
        staff_salary = StaffSalaries.query.filter(StaffSalaries.id == salary_id).first()
        staff_cash = StaffSalary.query.filter(StaffSalary.id == staff_salary.salary_id,
                                              StaffSalary.staff_id == staff.id,
                                              StaffSalary.location_id == staff_salary.location_id,
                                              StaffSalary.taken_money != None).first()
        result = staff_cash.taken_money - staff_salary.payment_sum

        remaining_salary = staff_cash.total_salary - result
        if remaining_salary == staff_cash.total_salary:
            remaining_salary = 0

        StaffSalary.query.filter(StaffSalary.id == staff_cash.id).update(
            {"taken_money": result, "remaining_salary": remaining_salary, "status": False})
        db.session.commit()
        deleted_salary = DeletedStaffSalaries(payment_sum=staff_salary.payment_sum, reason=staff_salary.reason,
                                              payment_type_id=staff_salary.payment_type_id,
                                              staff_id=staff_salary.staff_id, reason_deleted=reason,
                                              location_id=staff_salary.location_id,
                                              calendar_month=staff_salary.calendar_month,
                                              calendar_day=staff_salary.calendar_day,
                                              calendar_year=staff_salary.calendar_year,
                                              account_period_id=staff_salary.account_period_id,
                                              salary_id=staff_cash.id,
                                              deleted_date=calendar_day.date,
                                              profession_id=staff_salary.profession_id)
        db.session.add(deleted_salary)
        db.session.commit()
        db.session.delete(staff_salary)
        db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Oylik o'chirildi"
    })


@app.route(f'{api}/change_teacher_salary/<int:salary_id>/<type_id>/<int:user_id>')
@jwt_required()
def change_teacher_salary(salary_id, type_id, user_id):
    """
     change payment_type_id in TeacherSalaries, StaffSalaries and StudentPayments
    :param salary_id: TeacherSalary and StaffSalary primary key
    :param user_id: User table primary key
    :param type_id: PaymentType table primary key

    :return:
    """
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()
    payment_type = PaymentTypes.query.filter(PaymentTypes.name == type_id).first()
    if teacher:
        TeacherSalaries.query.filter(TeacherSalaries.id == salary_id).update({
            "payment_type_id": payment_type.id
        })
        db.session.commit()

    elif staff:
        StaffSalaries.query.filter(StaffSalaries.id == salary_id).update({
            "payment_type_id": payment_type.id
        })
        db.session.commit()

    else:

        StudentPayments.query.filter(StudentPayments.id == salary_id).update({
            "payment_type_id": payment_type.id
        })
        db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Oylik qiymat turi o'zgartirildi"
    })


@app.route(f'{api}/set_salary/<int:user_id>', methods=['POST'])
@jwt_required()
def set_salary(user_id):
    """
    update data in Staff table
    :param user_id: User table primary key
    :return:
    """
    salary = int(request.get_json()['salary'])
    Staff.query.filter(Staff.user_id == user_id).update({
        "salary": salary
    })
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Oylik belgilandi"
    })


@app.route(f'{api}/employees/<int:location_id>', defaults={"status": None})
@app.route(f'{api}/employees/<int:location_id>/<status>')
@jwt_required()
def employees(location_id, status):
    """

    :param location_id: Location table primary key
    :return: Staff data
    """
    user_id = get_jwt_identity()
    staff_salary_update()
    user = Users.query.filter(Users.user_id == user_id).first()
    if not status:
        staffs = db.session.query(Staff).join(Staff.user).options(contains_eager(Staff.user)).filter(
            Users.location_id == location_id).filter(or_(Staff.deleted == False, Staff.deleted == None)).order_by(
            Users.id).all()
    else:
        staffs = db.session.query(Staff).join(Staff.user).options(contains_eager(Staff.user)).filter(
            Users.location_id == location_id, Staff.deleted == True).order_by(
            Users.id).all()
    list_staff = [{
        "id": staff.user.id,
        "name": staff.user.name.title(),
        "surname": staff.user.surname.title(),
        "username": staff.user.username,
        "language": staff.user.language.name,
        "age": staff.user.age,
        "reg_date": staff.user.day.date.strftime("%Y-%m-%d"),
        "job": staff.profession.name,
        "role": staff.user.role_info.role,
        "status": False if user.id == staff.user.id or status else True
    } for staff in staffs]

    return jsonify({
        "data": list_staff
    })


@app.route(f'{api}/delete_staff/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(user_id):
    Staff.query.filter(Staff.user_id == user_id).update({
        "deleted": True,
        "deleted_comment": request.get_json()['otherReason']
    })
    db.session.commit()
    return jsonify({
        "msg": "O'chirildi",
        "status": True
    })
