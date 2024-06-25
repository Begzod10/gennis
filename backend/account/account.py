from app import app, db, desc, request, contains_eager, and_, jsonify, func
from flask_jwt_extended import jwt_required
from backend.models.models import AccountingPeriod, CalendarMonth, PaymentTypes, StudentPayments, Students, CalendarDay, \
    StaffSalaries, TeacherSalaries, CenterBalanceOverhead, Overhead, CalendarYear, BranchPayment, \
    AccountingInfo, DeletedStudentPayments, DeletedOverhead, DeletedTeacherSalaries, \
    DeletedStaffSalaries, Users, Teachers, CenterBalance, BookPayments, Capital
from backend.models.settings import sum_money
from pprint import pprint
from backend.functions.utils import get_json_field, api, find_calendar_date
from backend.functions.filters import old_current_dates
from datetime import datetime


@app.route(f'{api}/account_info/', defaults={"type_filter": None}, methods=["POST"])
@app.route(f'{api}/account_info/<type_filter>', methods=["POST"])
@jwt_required()
def account_info(type_filter):
    """
    function to show all account data
    :return: filtered account data list
    """
    type_account = get_json_field('type')
    location = get_json_field('locationId')
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    accounting_period = AccountingPeriod.query.join(CalendarMonth).order_by(desc(CalendarMonth.id)).first().id
    payments_list = []
    final_list = []
    if type_account == "payments":
        if not type_filter:
            payments = StudentPayments.query.filter(StudentPayments.location_id == location,
                                                    StudentPayments.payment == True,
                                                    StudentPayments.account_period_id == accounting_period,
                                                    ).order_by(
                desc(StudentPayments.id)).all()
        else:
            payments = StudentPayments.query.filter(StudentPayments.location_id == location,
                                                    StudentPayments.payment == True,
                                                    ).order_by(
                desc(StudentPayments.id)).all()
        type_account = "user"
        payments_list = [
            {
                "id": payment.id,
                "name": payment.student.user.name.title(),
                "surname": payment.student.user.surname.title(),
                "payment": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.student.user_id
            } for payment in payments
        ]
    if type_account == "book_payments":
        type_account = "studentBookPayment"

        if not type_filter:
            branch_payments = BranchPayment.query.filter(BranchPayment.location_id == location,
                                                         BranchPayment.account_period_id == accounting_period).order_by(
                BranchPayment.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.account_period_id == accounting_period,
                                                                         CenterBalanceOverhead.deleted == False).order_by(
                CenterBalanceOverhead.id).all()
        else:
            branch_payments = BranchPayment.query.filter(BranchPayment.location_id == location.BranchPayment).order_by(
                BranchPayment.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.deleted == False,
                                                                         ).order_by(
                CenterBalanceOverhead.id).all()
        book_payments = [
            {
                "id": payment.id,
                "name": "Kitobchiga pul",
                "price": int(payment.order.book.own_price) if payment.order.book else 0,
                "typePayment": payment.payment_type.name,
                "date": payment.order.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "reason": "",
                "type": "book",
            } for payment in branch_payments
        ]
        book_overheads = [
            {
                "id": balance_overhead.id,
                "name": "Kitob pulidan",
                "price": int(balance_overhead.payment_sum),
                "typePayment": balance_overhead.payment_type.name,
                "date": balance_overhead.day.date.strftime("%Y-%m-%d"),
                "day": str(balance_overhead.calendar_day),
                "month": str(balance_overhead.calendar_month),
                "year": str(balance_overhead.calendar_year),
                "reason": "",
                "type": "book",
            } for balance_overhead in center_balance_overhead
        ]
        payments_list = {
            "book_overheads": book_overheads,
            "book_payments": book_payments,
        }

    if type_account == "teacher_salary":
        if not type_filter:
            teacher_salaries = TeacherSalaries.query.filter(TeacherSalaries.location_id == location,
                                                            TeacherSalaries.account_period_id == accounting_period,
                                                            ).order_by(
                desc(TeacherSalaries.id)).all()
        else:
            teacher_salaries = TeacherSalaries.query.filter(TeacherSalaries.location_id == location,
                                                            ).order_by(
                desc(TeacherSalaries.id)).all()
        type_account = "user"

        payments_list = [
            {
                "id": payment.id,
                "name": payment.teacher.user.name.title(),
                "surname": payment.teacher.user.surname.title(),
                "salary": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.teacher.user_id
            } for payment in teacher_salaries
        ]
    if type_account == "staff_salary":
        if not type_filter:
            staff_salaries = StaffSalaries.query.filter(StaffSalaries.location_id == location,
                                                        StaffSalaries.account_period_id == accounting_period,
                                                        ).order_by(
                desc(StaffSalaries.id)).all()
        else:
            staff_salaries = StaffSalaries.query.filter(StaffSalaries.location_id == location,

                                                        ).order_by(
                desc(StaffSalaries.id)).all()
        type_account = "user"
        payments_list = [
            {
                "id": payment.id,
                "name": payment.staff.user.name.title(),
                "surname": payment.staff.user.surname.title(),
                "salary": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.staff.user_id,
                "job": payment.profession.name
            } for payment in staff_salaries
        ]
    if type_account == "discounts":
        if not type_filter:
            payments = StudentPayments.query.filter(StudentPayments.location_id == location,
                                                    StudentPayments.payment == False,
                                                    StudentPayments.account_period_id == accounting_period,
                                                    ).order_by(
                desc(StudentPayments.id)).all()
        else:
            payments = StudentPayments.query.filter(StudentPayments.location_id == location,
                                                    StudentPayments.payment == False,
                                                    ).order_by(
                desc(StudentPayments.id)).all()
        type_account = "user"

        payments_list = [
            {
                "id": payment.id,
                "name": payment.student.user.name.title(),
                "surname": payment.student.user.surname.title(),
                "payment": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.student.user_id
            } for payment in payments
        ]
    if type_account == "debts":
        type_account = "user"
        students = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
            Users.balance < 0, Users.location_id == location).order_by(Users.balance).all()
        payments_list = []
        for student in students:
            info = {
                "id": student.user.id,
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "moneyType": ["green", "yellow", "red", "navy", "black"][student.debtor],
                "phone": student.user.phone[0].phone,
                "balance": student.user.balance,
                "status": "Guruh" if student.group else "Guruhsiz",
                "teacher": [],
                "reason": "",
                "payment_reason": "tel qilinmaganlar",
                "reason_days": ""
            }
            if student.group:
                for gr in student.group:

                    teacher = Teachers.query.filter(Teachers.id == gr.teacher_id).first()
                    if teacher:
                        info['teacher'].append(str(teacher.user_id))
            if student.reasons_list:
                for reason in student.reasons_list:
                    if not reason.to_date:
                        if reason.added_date == calendar_day.date:
                            info['reason_days'] = reason.added_date.strftime("%Y-%m-%d")
                            info['payment_reason'] = "tel ko'tarmadi"
                    else:
                        if reason.to_date >= calendar_day.date:
                            info['reason'] = reason.reason
                            info['reason_days'] = reason.to_date.strftime("%Y-%m-%d")
                            info['payment_reason'] = "tel ko'tardi"
            payments_list.append(info)
    if type_account == "overhead":
        type_account = ''
        if not type_filter:
            overhead = Overhead.query.filter(Overhead.location_id == location,
                                             Overhead.account_period_id == accounting_period,
                                             ).order_by(desc(Overhead.id))

        else:
            overhead = Overhead.query.filter(Overhead.location_id == location,
                                             ).order_by(desc(Overhead.id))

        payments_list = [
            {
                "id": over.id,
                "name": over.item_name,
                "price": int(over.item_sum),
                "typePayment": over.payment_type.name,
                "date": over.day.date.strftime("%Y-%m-%d"),
                "day": str(over.calendar_day),
                "month": str(over.calendar_month),
                "year": str(over.calendar_year),
                "reason": "",
                "type": "overhead",
            } for over in overhead
        ]
    if type_account == "capital":

        type_account = ''
        if not type_filter:
            capital = Capital.query.filter(Capital.location_id == location,
                                           Capital.account_period_id == accounting_period,
                                           ).order_by(
                desc(Capital.id)).all()
        else:
            capital = Capital.query.filter(Capital.location_id == location,
                                           ).order_by(
                desc(Capital.id)).all()

        payments_list = [{
            "id": over.id,
            "name": over.name,
            "price": over.price,
            "typePayment": over.payment_type.name,
            "date": over.day.date.strftime("%Y-%m-%d"),
            "day": str(over.calendar_day),
            "month": str(over.calendar_month),
            "year": str(over.calendar_year)
        } for over in capital]
    return jsonify({
        "data": {
            "typeOfMoney": type_account,
            "data": payments_list,
            "overhead_tools": old_current_dates(observation=True),
            "capital_tools": old_current_dates(observation=True),
            "teacher_list": final_list,
            "location": location

        }
    })


@app.route(f'{api}/account_info_deleted/', defaults={"type_filter": None}, methods=["POST"])
@app.route(f'{api}/account_info_deleted/<type_filter>', methods=["POST"])
@jwt_required()
def account_info_deleted(type_filter):
    """
    function to show all deleted account data
    :return: deleted account data list
    """
    type_account = get_json_field('type')
    location = get_json_field('locationId')
    accounting_period = AccountingPeriod.query.join(CalendarMonth).order_by(desc(CalendarMonth.id)).first().id
    payments_list = []
    if type_account == "payments":
        if not type_filter:
            payments = DeletedStudentPayments.query.filter(DeletedStudentPayments.location_id == location,
                                                           DeletedStudentPayments.payment == True,
                                                           DeletedStudentPayments.account_period_id == accounting_period,
                                                           ).order_by(
                DeletedStudentPayments.id).all()
        else:
            payments = DeletedStudentPayments.query.filter(DeletedStudentPayments.location_id == location,
                                                           DeletedStudentPayments.payment == True,
                                                           ).order_by(
                DeletedStudentPayments.id).all()

        type_account = "user"

        payments_list = [
            {
                "id": payment.id,
                "name": payment.student.user.name.title(),
                "surname": payment.student.user.surname.title(),
                "payment": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.student.user_id,
                "reason": payment.reason
            } for payment in payments]
    if type_account == "book_payments":
        type_account = "studentBookPayment"
        book_overheads = []
        book_payments = []
        if not type_filter:
            branch_payments = BranchPayment.query.filter(BranchPayment.location_id == location,
                                                         BranchPayment.account_period_id == accounting_period).order_by(
                BranchPayment.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.account_period_id == accounting_period,
                                                                         CenterBalanceOverhead.deleted == True).order_by(
                CenterBalanceOverhead.id).all()

        else:

            branch_payments = BranchPayment.query.filter(BranchPayment.location_id == location.BranchPayment).order_by(
                BranchPayment.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.deleted == True,
                                                                         ).order_by(
                CenterBalanceOverhead.id).all()

        book_payments = [
            {
                "id": payment.id,
                "name": "Kitobchiga pul",
                "price": int(payment.order.book.own_price),
                "typePayment": payment.payment_type.name,
                "date": payment.order.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "reason": "",
                "type": "book",
            } for payment in branch_payments]

        book_overheads = [
            {
                "id": balance_overhead.id,
                "name": "Kitob pulidan",
                "price": int(balance_overhead.payment_sum),
                "typePayment": balance_overhead.payment_type.name,
                "date": balance_overhead.day.date.strftime("%Y-%m-%d"),
                "day": str(balance_overhead.calendar_day),
                "month": str(balance_overhead.calendar_month),
                "year": str(balance_overhead.calendar_year),
                "reason": "",
                "type": "book",
            } for balance_overhead in center_balance_overhead]
        payments_list = {
            "book_overheads": book_overheads,
            "book_payments": book_payments,
        }
    if type_account == "teacher_salary":
        if not type_filter:
            teacher_salaries = DeletedTeacherSalaries.query.filter(DeletedTeacherSalaries.location_id == location,
                                                                   DeletedTeacherSalaries == accounting_period,
                                                                   ).order_by(
                DeletedTeacherSalaries.id).all()
        else:
            teacher_salaries = DeletedTeacherSalaries.query.filter(DeletedTeacherSalaries.location_id == location,

                                                                   ).order_by(
                DeletedTeacherSalaries.id).all()
        type_account = "user"

        payments_list = [
            {
                "id": payment.id,
                "name": payment.teacher.user.name.title(),
                "surname": payment.teacher.user.surname.title(),
                "salary": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.teacher.user_id,
                "reason": payment.reason_deleted
            } for payment in teacher_salaries
        ]
    if type_account == "staff_salary":
        if not type_filter:
            staff_salaries = DeletedStaffSalaries.query.filter(DeletedStaffSalaries.location_id == location,
                                                               DeletedStaffSalaries.account_period_id == accounting_period,
                                                               ).order_by(
                DeletedStaffSalaries.id).all()
        else:
            staff_salaries = DeletedStaffSalaries.query.filter(DeletedStaffSalaries.location_id == location,
                                                               ).order_by(
                DeletedStaffSalaries.id).all()
        type_account = "user"
        payments_list = [
            {
                "id": payment.id,
                "name": payment.staff.user.name.title(),
                "surname": payment.staff.user.surname.title(),
                "salary": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.staff.user_id,
                "job": payment.profession.name,
                "reason": payment.reason_deleted
            } for payment in staff_salaries]

    if type_account == "discounts":
        if not type_filter:
            payments = DeletedStudentPayments.query.filter(DeletedStudentPayments.location_id == location,
                                                           DeletedStudentPayments.payment == False,
                                                           DeletedStudentPayments.account_period_id == accounting_period,
                                                           ).order_by(
                DeletedStudentPayments.id).all()
        else:

            payments = DeletedStudentPayments.query.filter(DeletedStudentPayments.location_id == location,
                                                           DeletedStudentPayments.payment == False,
                                                           ).order_by(
                DeletedStudentPayments.id).all()
        type_account = "user"
        payments_list = [
            {
                "id": payment.id,
                "name": payment.student.user.name.title(),
                "surname": payment.student.user.surname.title(),
                "payment": payment.payment_sum,
                "typePayment": payment.payment_type.name,
                "date": payment.day.date.strftime("%Y-%m-%d"),
                "day": str(payment.calendar_day),
                "month": str(payment.calendar_month),
                "year": str(payment.calendar_year),
                "user_id": payment.student.user_id,
                "reason": payment.reason
            } for payment in payments]
    if type_account == "overhead":
        type_account = ''
        if not type_filter:
            overhead = DeletedOverhead.query.filter(DeletedOverhead.location_id == location,
                                                    DeletedOverhead.account_period_id == accounting_period,
                                                    ).order_by(
                DeletedOverhead.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.account_period_id == accounting_period,
                                                                         CenterBalanceOverhead.deleted == True).order_by(
                CenterBalanceOverhead.id).all()

        else:
            overhead = DeletedOverhead.query.filter(DeletedOverhead.location_id == location).order_by(
                DeletedOverhead.id).all()
            center_balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.location_id == location,
                                                                         CenterBalanceOverhead.deleted == True,
                                                                         ).order_by(
                CenterBalanceOverhead.id).all()

        payments_list = [
            {
                "id": over.id,
                "name": over.item_name,
                "price": int(over.item_sum),
                "typePayment": over.payment_type.name,
                "date": over.day.date.strftime("%Y-%m-%d"),
                "day": str(over.calendar_day),
                "month": str(over.calendar_month),
                "year": str(over.calendar_year),
                "reason": over.reason,
                "type": "overhead",
            } for over in overhead
        ]
        payments_list += [
            {
                "id": balance_overhead.id,
                "name": "Kitob pulidan",
                "price": int(balance_overhead.payment_sum),
                "typePayment": balance_overhead.payment_type.name,
                "date": balance_overhead.day.date.strftime("%Y-%m-%d"),
                "day": str(balance_overhead.calendar_day),
                "month": str(balance_overhead.calendar_month),
                "year": str(balance_overhead.calendar_year),
                "reason": "",
                "type": "book",
            } for balance_overhead in center_balance_overhead
        ]
    if type_account == "capital":
        type_account = ''
        if not type_filter:
            capital = Capital.query.filter(Capital.location_id == location,
                                           Capital.account_period_id == accounting_period,
                                           Capital.deleted == True
                                           ).order_by(
                Capital.id).all()
        else:
            capital = Capital.query.filter(Capital.location_id == location,
                                           Capital.deleted == True
                                           ).order_by(
                Capital.id).all()

        payments_list = [
            {
                "id": over.id,
                "name": over.item_name,
                "price": over.item_sum,
                "typePayment": over.payment_type.name,
                "date": over.day.date.strftime("%Y-%m-%d"),
                "day": str(over.calendar_day),
                "month": str(over.calendar_month),
                "year": str(over.calendar_year),
                "reason": over.reason
            }
            for over in capital
        ]
    return jsonify({
        "data": {
            "typeOfMoney": type_account,
            "data": payments_list,
            "overhead_tools": old_current_dates(),
            "capital_tools": old_current_dates(),
            "location": location
        }
    })


@app.route(f'{api}/account_details/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def account_details(location_id):
    """
    function to get account data
    :param location_id: Location table primary key
    :return: account datas  filtering them by date and location_id
    """
    if request.method == "POST":
        ot = request.get_json()['ot']
        do = request.get_json()['do']
        ot = datetime.strptime(ot, "%Y-%m-%d")
        do = datetime.strptime(do, "%Y-%m-%d")
        activeFilter = request.get_json()['activeFilter']
        payment_type = PaymentTypes.query.filter(PaymentTypes.name == activeFilter).first()
        student_payments = db.session.query(StudentPayments).join(StudentPayments.day).options(
            contains_eager(StudentPayments.day)).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, StudentPayments.location_id == location_id,
                 StudentPayments.payment_type_id == payment_type.id, StudentPayments.payment == True,
                 )).order_by(
            desc(StudentPayments.id)).all()

        all_payment = db.session.query(
            func.sum(StudentPayments.payment_sum)).join(CalendarDay,
                                                        CalendarDay.id == StudentPayments.calendar_day).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, StudentPayments.location_id == location_id,
                 StudentPayments.payment_type_id == payment_type.id, StudentPayments.payment == True,
                 )).first()[0] if student_payments else 0

        teacher_salaries = db.session.query(TeacherSalaries).join(TeacherSalaries.day).options(
            contains_eager(TeacherSalaries.day)).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, TeacherSalaries.location_id == location_id,
                 TeacherSalaries.payment_type_id == payment_type.id
                 )).order_by(
            desc(TeacherSalaries.id)).all()

        all_teacher = db.session.query(func.sum(TeacherSalaries.payment_sum)) \
            .join(CalendarDay, CalendarDay.id == TeacherSalaries.calendar_day) \
            .filter(
            and_(
                CalendarDay.date >= ot,
                CalendarDay.date <= do,
                TeacherSalaries.location_id == location_id,
                TeacherSalaries.payment_type_id == payment_type.id
            )
        ).first()[0] if teacher_salaries else 0

        staff_salaries = db.session.query(StaffSalaries).join(StaffSalaries.day).options(
            contains_eager(StaffSalaries.day)).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, StaffSalaries.location_id == location_id,
                 StaffSalaries.payment_type_id == payment_type.id
                 )).order_by(
            StaffSalaries.id).all()

        all_staff = db.session.query(func.sum(StaffSalaries.payment_sum)) \
            .join(CalendarDay, CalendarDay.id == StaffSalaries.calendar_day) \
            .filter(
            and_(
                CalendarDay.date >= ot,
                CalendarDay.date <= do,
                StaffSalaries.location_id == location_id,
                StaffSalaries.payment_type_id == payment_type.id
            )
        ).first()[0] if staff_salaries else 0
        overhead = db.session.query(Overhead).join(Overhead.day).options(
            contains_eager(Overhead.day)).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, Overhead.location_id == location_id,
                 Overhead.payment_type_id == payment_type.id
                 )).order_by(
            desc(Overhead.id)).all()

        all_overhead = db.session.query(func.sum(Overhead.item_sum)) \
            .join(CalendarDay, CalendarDay.id == Overhead.calendar_day) \
            .filter(
            and_(
                CalendarDay.date >= ot,
                CalendarDay.date <= do,
                Overhead.location_id == location_id,
                Overhead.payment_type_id == payment_type.id
            )
        ).first()[0] if overhead else 0

        branch_payments = BranchPayment.query.join(CalendarDay).filter(BranchPayment.location_id == location_id,
                                                                       ).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, BranchPayment.location_id == location_id,
                 BranchPayment.payment_type_id == payment_type.id
                 )).order_by(
            BranchPayment.id).all()

        branch_payments_all = db.session.query(
            func.sum(BranchPayment.payment_sum
                     )).join(CalendarDay, CalendarDay.id == BranchPayment.calendar_day).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, BranchPayment.location_id == location_id,
                 BranchPayment.payment_type_id == payment_type.id
                 )).first()[0] if branch_payments else 0

        center_balance_overhead = db.session.query(CenterBalanceOverhead).join(CenterBalanceOverhead.day).options(
            contains_eager(CenterBalanceOverhead.day)).filter(CenterBalanceOverhead.location_id == location_id,
                                                              CenterBalanceOverhead.deleted == False).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do,
                 CenterBalanceOverhead.payment_type_id == payment_type.id
                 )).order_by(
            CenterBalanceOverhead.id).all()

        center_balance_all = db.session.query(
            func.sum(CenterBalanceOverhead.payment_sum
                     )).join(CalendarDay, CalendarDay.id == CenterBalanceOverhead.calendar_day).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, CenterBalanceOverhead.location_id == location_id,
                 CenterBalanceOverhead.payment_type_id == payment_type.id
                 )).first()[0] if center_balance_overhead else 0

        capitals = db.session.query(Capital).join(Capital.day).options(
            contains_eager(Capital.day)).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, Capital.location_id == location_id,
                 Capital.payment_type_id == payment_type.id
                 )).order_by(
            desc(Capital.id)).all()

        all_capital = db.session.query(
            func.sum(Capital.price
                     )).join(CalendarDay, CalendarDay.id == Capital.calendar_day).filter(
            and_(CalendarDay.date >= ot, CalendarDay.date <= do, Capital.location_id == location_id,
                 Capital.payment_type_id == payment_type.id
                 )).first()[0] if capitals else 0

        payments_list = [{
            "id": payment.id,
            "name": payment.student.user.name.title(),
            "surname": payment.student.user.surname.title(),
            "payment": payment.payment_sum,
            "date": payment.day.date.strftime('%Y-%m-%d'),
            "user_id": payment.student.user_id
        } for payment in student_payments]

        teacher_salary = [{
            "id": salary.id,
            "name": salary.teacher.user.name.title(),
            "surname": salary.teacher.user.surname.title(),
            "salary": salary.payment_sum,
            "reason": salary.reason,
            "month": salary.salary.month.date.strftime("%Y-%m") if salary.salary else None,
            "date": salary.day.date.strftime('%Y-%m-%d'),
            "user_id": salary.teacher.user_id
        } for salary in teacher_salaries]
        staff_salary = [{
            "id": salary.id,
            "name": salary.staff.user.name.title() if salary.staff else None,
            "surname": salary.staff.user.surname if salary.staff else None,
            "payment": salary.payment_sum,
            "month": salary.month.date.strftime("%Y-%m"),
            "date": salary.day.date.strftime('%Y-%m-%d'),
            "user_id": salary.staff.user_id if salary.staff else None
        } for salary in staff_salaries]

        overhead_list = [{
            "id": salary.id,
            "name": salary.item_name,
            "payment": salary.item_sum,
            "date": salary.day.date.strftime('%Y-%m-%d')
        } for salary in overhead]
        overhead_list += [
            {
                "id": branch_payment.id,
                "name": "Kitobchiga pul ",
                "payment": branch_payment.payment_sum,
                "date": branch_payment.day.date.strftime('%Y-%m-%d')
            } for branch_payment in branch_payments
        ]

        overhead_list += [
            {
                "id": branch_payment.id,
                "name": "Kitob pulidan",
                "payment": branch_payment.payment_sum,
                "date": branch_payment.day.date.strftime('%Y-%m-%d')
            } for branch_payment in center_balance_overhead
        ]
        capital_list = [{
            "id": salary.id,
            "name": salary.name,
            "payment": salary.price,
            "date": salary.day.date.strftime('%Y-%m-%d')
        } for salary in capitals]

        result = all_payment - (
                all_overhead + all_teacher + all_staff + all_capital + center_balance_all + branch_payments_all)
        return jsonify({
            "data": {
                "data": {
                    "studentPayment": {
                        "list": payments_list,
                        "value": all_payment
                    },
                    "teacherSalary": {
                        "list": teacher_salary,
                        "value": all_teacher
                    },
                    "employeeSalary": {
                        "list": staff_salary,
                        "value": all_staff
                    },
                    "overheads": {
                        "list": overhead_list,
                        "value": all_overhead
                    },
                    "capitals": {
                        "list": capital_list,
                        "value": all_capital
                    },
                    "result": result
                },
            }
        })


@app.route(f'{api}/get_location_money/<int:location_id>')
def get_location_money(location_id):
    """

    :param location_id: Location table primary key
    :return:
    """

    accounting_period = AccountingPeriod.query.join(CalendarMonth).order_by(desc(CalendarMonth.id)).first()
    # accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
    #     contains_eager(AccountingPeriod.month)).filter(AccountingPeriod.id == 11).order_by(
    #     desc(CalendarMonth.id)).first()

    # periods = AccountingPeriod.query.order_by(
    #     AccountingPeriod.id).all()
    # print(periods)
    # payments = StudentPayments.query.filter(StudentPayments.location_id == 1).order_by(StudentPayments.id).all()
    # payments = TeacherSalaries.query.order_by(TeacherSalaries.id).all()
    # payments = StaffSalaries.query.order_by(StaffSalaries.id).all()
    # payments = Overhead.query.order_by(Overhead.id).all()
    # payments = CapitalExpenditure.query.order_by(CapitalExpenditure.id).all()
    # payments = StudentCharity.query.order_by(StudentCharity.id).all()
    # #
    # print(len(payments))
    # counter = 0
    # for payment in payments:
    #
    #     for period in periods:
    #         if payment.day.date >= period.from_date and payment.day.date <= period.to_date:
    #             # counter += 1
    #             if payment.account_period_id != period.id:
    #                 payment.account_period_id = period.id
    #                 db.session.commit()
    # print("tugadi")
    # print(periods)
    # for period in periods:
    #     # from_month_year = period.from_date.strftime("%Y-%m") + "-11"
    #     # to_month_year = period.to_date.strftime("%Y-%m") + "-10"
    #     # from_month_year = datetime.strptime(from_month_year, "%Y-%m-%d")
    #     # to_month_year = datetime.strptime(to_month_year, "%Y-%m-%d")
    #     # AccountingPeriod.query.filter(AccountingPeriod.id == period.id).update({
    #     #     "from_date": from_month_year,
    #     #     "to_date": to_month_year
    #     # })
    #     # db.session.commit()
    #     month_period = period.from_date.strftime("%Y-%m")
    #     month_period = datetime.strptime(month_period, "%Y-%m")
    #     month = CalendarMonth.query.filter(CalendarMonth.date == month_period).first()
    #     # print(month.id)
    #     print("bosh", period.from_date, period.to_date, period.month.id)
    #     period.month_id = month.id
    #     db.session.commit()
    #     print(period.id)

    payment_types = PaymentTypes.query.order_by(PaymentTypes.id).all()

    account_list = []
    for payment_type in payment_types:
        student_payments = sum_money(StudentPayments.payment_sum, StudentPayments.account_period_id,
                                     accounting_period.id, StudentPayments.location_id, location_id,
                                     StudentPayments.payment_type_id, payment_type.id, type_payment="payment",
                                     status_payment=True)
        student_discounts = sum_money(StudentPayments.payment_sum, StudentPayments.account_period_id,
                                      accounting_period.id, StudentPayments.location_id, location_id,
                                      StudentPayments.payment_type_id, payment_type.id, type_payment="payment",
                                      status_payment=False)
        # book_payments = sum_money(BookPayments.payment_sum, BookPayments.account_period_id, accounting_period.id,
        #                           BookPayments.location_id, location_id, BookPayments)
        teacher_salaries = sum_money(TeacherSalaries.payment_sum, TeacherSalaries.account_period_id,
                                     accounting_period.id, TeacherSalaries.location_id, location_id,
                                     TeacherSalaries.payment_type_id, payment_type.id)
        staff_salaries = sum_money(StaffSalaries.payment_sum, StaffSalaries.account_period_id,
                                   accounting_period.id, StaffSalaries.location_id, location_id,
                                   StaffSalaries.payment_type_id, payment_type.id)
        overhead = sum_money(Overhead.item_sum, Overhead.account_period_id,
                             accounting_period.id, Overhead.location_id, location_id,
                             Overhead.payment_type_id, payment_type.id)
        # center_balance = CenterBalance.query.filter(CenterBalance.location_id == location_id,
        #                                             CenterBalance.account_period_id == accounting_period).first()

        # center_balance_sum =

        branch_payments = db.session.query(func.sum(BranchPayment.payment_sum)).filter(
            BranchPayment.location_id == location_id,
            BranchPayment.account_period_id == accounting_period.id,
            BranchPayment.payment_type_id == payment_type.id
        ).first()
        center_balance_overhead = db.session.query(func.sum(CenterBalanceOverhead.payment_sum)).filter(
            CenterBalanceOverhead.location_id == location_id,
            CenterBalanceOverhead.account_period_id == accounting_period.id,
            CenterBalanceOverhead.deleted == False,
            CenterBalanceOverhead.payment_type_id == payment_type.id).first()
        capital = sum_money(Capital.price, Capital.account_period_id,
                            accounting_period.id, Capital.location_id, location_id,
                            Capital.payment_type_id, payment_type.id,
                            )
        if branch_payments[0]:
            branch_payments = branch_payments[0]
        else:
            branch_payments = 0

        if center_balance_overhead[0]:
            center_balance_overhead = center_balance_overhead[0]
        else:
            center_balance_overhead = 0

        current_cash = student_payments - (
                teacher_salaries + staff_salaries + overhead + capital + center_balance_overhead + branch_payments)

        account_list += [{
            "value": current_cash,
            "type": payment_type.name,
            "student_payments": student_payments,
            "teacher_salaries": teacher_salaries,
            "staff_salaries": staff_salaries,
            "overhead": overhead + branch_payments + center_balance_overhead,
            "capital": capital
        }]

        account_get = AccountingInfo.query.filter(AccountingInfo.account_period_id == accounting_period.id,
                                                  AccountingInfo.location_id == location_id,
                                                  AccountingInfo.payment_type_id == payment_type.id,
                                                  AccountingInfo.calendar_year == accounting_period.year_id).first()

        if not account_get:
            add = AccountingInfo(account_period_id=accounting_period.id, all_payments=student_payments,
                                 location_id=location_id, all_teacher_salaries=teacher_salaries,
                                 payment_type_id=payment_type.id, all_staff_salaries=staff_salaries,
                                 all_overhead=overhead + branch_payments + center_balance_overhead, all_capital=capital,
                                 all_charity=student_discounts,
                                 calendar_year=accounting_period.year_id)
            add.add()
        else:
            account_get.all_payments = student_payments
            account_get.all_teacher_salaries = teacher_salaries
            account_get.all_staff_salaries = staff_salaries
            account_get.all_overhead = overhead + branch_payments + center_balance_overhead
            account_get.all_capital = capital
            account_get.all_charity = student_discounts
            account_get.current_cash = current_cash
            db.session.commit()

    return jsonify({
        "data": account_list
    })


@app.route(f'{api}/account_history/<int:location_id>', methods=['POST'])
def account_history(location_id):
    """
    function to get account data year and payment type
    :param location_id: Location table primary key
    :return:
    """

    if request.method == "POST":
        year = get_json_field('year')
        payment_type = get_json_field('activeFilter')

        year = datetime.strptime(year, '%Y')
        year = CalendarYear.query.filter(CalendarYear.date == year).first()
        payment_type = PaymentTypes.query.filter(PaymentTypes.name == payment_type).first()

        account_infos = AccountingInfo.query.filter(AccountingInfo.location_id == location_id,
                                                    AccountingInfo.payment_type_id == payment_type.id,
                                                    AccountingInfo.calendar_year == year.id).order_by(desc(
            AccountingInfo.id)).all()
        account_list = [{
            "id": account.id,
            "month": account.period.month.date.strftime("%h"),
            "type": account.payment_type.name,
            "payment": account.all_payments,
            "teacherSalary": account.all_teacher_salaries,
            "employeesSalary": account.all_staff_salaries,
            "overheads": account.all_overhead,
            "capitalExpenditures": account.all_capital,
            "current_cash": account.current_cash,
            "old_cash": account.old_cash,
            "period_id": account.account_period_id,
            "discount": account.all_charity
        } for account in account_infos]

        return jsonify({
            "data": account_list,
        })


@app.route(f'{api}/account_years/<int:location_id>')
def account_years(location_id):
    """

    :param location_id: Location table primary key
    :return: year list
    """

    # for data in account_datas:
    #     db.session.delete(data)
    #     db.session.commit()

    # account_period = AccountingPeriod.query.filter(AccountingPeriod.student_payments != None).order_by(
    #     AccountingPeriod.id).all()
    # payment_types = PaymentTypes.query.order_by(PaymentTypes.id).all()
    # for period in account_period:
    #     print(f"{period.from_date}   {period.to_date}")
    #     for payment_type in payment_types:
    #         student_payments = sum_money(StudentPayments.payment_sum, StudentPayments.account_period_id,
    #                                      period.id, StudentPayments.location_id, location_id,
    #                                      StudentPayments.payment_type_id, payment_type.id, type_payment="payment",
    #                                      status_payment=True)
    #         student_discounts = sum_money(StudentPayments.payment_sum, StudentPayments.account_period_id,
    #                                       period.id, StudentPayments.location_id, location_id,
    #                                       StudentPayments.payment_type_id, payment_type.id, type_payment="payment",
    #                                       status_payment=False)
    #         teacher_salaries = sum_money(TeacherSalaries.payment_sum, TeacherSalaries.account_period_id,
    #                                      period.id, TeacherSalaries.location_id, location_id,
    #                                      TeacherSalaries.payment_type_id, payment_type.id)
    #         staff_salaries = sum_money(StaffSalaries.payment_sum, StaffSalaries.account_period_id,
    #                                    period.id, StaffSalaries.location_id, location_id,
    #                                    StaffSalaries.payment_type_id, payment_type.id)
    #         overhead = sum_money(Overhead.item_sum, Overhead.account_period_id,
    #                              period.id, Overhead.location_id, location_id,
    #                              Overhead.payment_type_id, payment_type.id)
    #         capital = sum_money(CapitalExpenditure.item_sum, CapitalExpenditure.account_period_id,
    #                             period.id, CapitalExpenditure.location_id, location_id,
    #                             CapitalExpenditure.payment_type_id, payment_type.id,
    #                             )
    #         current_cash = student_payments - (teacher_salaries + staff_salaries + overhead + capital)
    #         account_get = AccountingInfo.query.filter(AccountingInfo.account_period_id == period.id,
    #                                                   AccountingInfo.location_id == location_id,
    #                                                   AccountingInfo.payment_type_id == payment_type.id,
    #                                                   AccountingInfo.calendar_year == period.year_id).first()
    #
    #         if not account_get:
    #             add = AccountingInfo(account_period_id=period.id, all_payments=student_payments,
    #                                  location_id=location_id, all_teacher_salaries=teacher_salaries,
    #                                  payment_type_id=payment_type.id, all_staff_salaries=staff_salaries,
    #                                  all_overhead=overhead, all_capital=capital, all_charity=student_discounts,
    #                                  calendar_year=period.year_id)
    #             add.add()
    #         else:
    #             account_get.all_payments = student_payments
    #             account_get.all_teacher_salaries = teacher_salaries
    #             account_get.all_staff_salaries = staff_salaries
    #             account_get.all_overhead = overhead
    #             account_get.all_capital = capital
    #             account_get.all_charity = student_discounts
    #             account_get.current_cash = current_cash
    #             db.session.commit()

    year_list = []
    account_datas = AccountingInfo.query.order_by(AccountingInfo.location_id == location_id).all()
    for data in account_datas:
        year_list.append(data.year.date.strftime("%Y"))
    year_list = list(dict.fromkeys(year_list))
    return jsonify({
        "years": year_list
    })
