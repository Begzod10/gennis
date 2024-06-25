from app import app, db, desc, contains_eager, request, jsonify

from backend.models.models import AccountingPeriod, StudentPayments, Students, AttendanceHistoryStudent, PaymentTypes, \
    CalendarMonth, Groups, DeletedBookPayments, StudentCharity, DeletedStudentPayments, BookPayments, \
    TeacherBlackSalary, Teachers
from flask_jwt_extended import jwt_required
from datetime import timedelta
from backend.student.class_model import Student_Functions
from datetime import datetime
from backend.functions.utils import get_json_field, find_calendar_date, api, update_salary


@app.route(f'{api}/delete_payment/<int:payment_id>', methods=['POST'])
@jwt_required()
def delete_payment(payment_id):
    """
    delete data from StudentPayments table
    :param payment_id: StudentPayments table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    reason = get_json_field('otherReason')
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    type = get_json_field('type')
    if type == "bookPayment":
        book_payment = BookPayments.query.filter(BookPayments.id == payment_id).first()
        student = Students.query.filter(Students.id == book_payment.student_id).first()
        add = DeletedBookPayments(student_id=student.id, location_id=book_payment.location_id,
                                  calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                  calendar_year=calendar_year.id, payment_sum=book_payment.payment_sum,
                                  account_period_id=accounting_period.id)
        db.session.add(add)
        db.session.commit()
        db.session.delete(book_payment)
        db.session.commit()
        st_functions = Student_Functions(student_id=student.id)
        st_functions.update_debt()
        st_functions.update_balance()
        return jsonify({
            "success": True,
            "msg": "Kitob to'lovi o'chirildi"
        })
    else:

        payment = StudentPayments.query.filter(StudentPayments.id == payment_id).first()

        deleted_payment = DeletedStudentPayments(student_id=payment.student_id, reason=reason,
                                                 location_id=payment.location_id,
                                                 calendar_day=payment.calendar_day,
                                                 calendar_month=payment.calendar_month,
                                                 calendar_year=payment.calendar_year,
                                                 payment_type_id=payment.payment_type_id,
                                                 payment_sum=payment.payment_sum, deleted_date=calendar_day.date,
                                                 account_period_id=accounting_period.id,
                                                 payment=payment.payment)
        db.session.add(deleted_payment)
        db.session.commit()
        all_payments = payment.payment_sum

        student = Students.query.filter(Students.id == payment.student_id).first()
        attendance_history = AttendanceHistoryStudent.query.filter(
            AttendanceHistoryStudent.student_id == payment.student_id,
            AttendanceHistoryStudent.payment != None, AttendanceHistoryStudent.payment != 0).order_by(
            AttendanceHistoryStudent.id).order_by(desc(AttendanceHistoryStudent.id)).all()
        if attendance_history:
            for attendance in attendance_history:
                if student.extra_payment:
                    extra_payment = student.extra_payment - all_payments
                    if extra_payment > 0:
                        Students.query.filter(Students.id == student.id).update({"extra_payment": extra_payment})
                        all_payments = 0
                    else:
                        Students.query.filter(Students.id == student.id).update({"extra_payment": 0})
                        all_payments = abs(extra_payment)
                    db.session.commit()

                if attendance:
                    result = all_payments - attendance.payment
                    if result >= 0:
                        AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.id == attendance.id).update({
                            "status": False,
                            "payment": 0
                        })
                        db.session.commit()

                        AttendanceHistoryStudent.query.filter(
                            AttendanceHistoryStudent.id == attendance.id).update({
                            "remaining_debt": 0
                        })
                        db.session.commit()
                        all_payments = abs(result)
                        continue
                    elif result < 0:
                        AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.id == attendance.id).update({
                            "status": False,
                            "payment": abs(result)
                        })
                        db.session.commit()

                        remaining_debt = attendance.total_debt + attendance.payment
                        AttendanceHistoryStudent.query.filter(
                            AttendanceHistoryStudent.id == attendance.id).update({
                            "remaining_debt": remaining_debt
                        })
                        db.session.commit()
                        break
        else:
            if student.extra_payment:
                extra_payment = student.extra_payment - all_payments
                if extra_payment > 0:
                    Students.query.filter(Students.id == student.id).update({"extra_payment": extra_payment})
                else:
                    Students.query.filter(Students.id == student.id).update({"extra_payment": 0})
                db.session.commit()

        black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.student_id == student.id,
                                                         TeacherBlackSalary.payment_id == payment_id).all()
        for salary in black_salaries:
            salary.status = False
            salary.payment_id = None
            db.session.commit()
            teacher = Teachers.query.filter(Teachers.id == salary.teacher_id).first()
            update_salary(teacher.user_id)
        db.session.delete(payment)
        db.session.commit()
        st_functions = Student_Functions(student_id=student.id)
        st_functions.update_debt()
        st_functions.update_balance()

        return jsonify({
            "success": True,
            "msg": "To'lov o'chirildi"
        })


@app.route(f'{api}/get_payment/<int:user_id>', methods=['POST', 'GET'])
@jwt_required()
def get_payment(user_id):
    """
    add data to StudentPayments table
    :param user_id: User table primary key
    :return:
    """
    student = Students.query.filter(Students.user_id == user_id).first()
    if request.method == "POST":
        status = get_json_field('type')
        type_payment = get_json_field('typePayment')
        payment_sum = int(get_json_field('payment'))
        if status == "payment":
            status = True
        else:
            status = False

        calendar_year, calendar_month, calendar_day = find_calendar_date()

        accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
            contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()

        attendance_history = AttendanceHistoryStudent.query.filter(
            AttendanceHistoryStudent.student_id == student.id, AttendanceHistoryStudent.status == False).order_by(
            AttendanceHistoryStudent.id).first()
        if type_payment:
            payment_type = PaymentTypes.query.filter(PaymentTypes.id == type_payment).first()
        else:
            payment_type = PaymentTypes.query.first()

        today = datetime.utcnow()
        hour = datetime.strftime(today, "%Y/%m/%d/%H/%M")
        hour2 = datetime.strptime(hour, "%Y/%m/%d/%H/%M")
        ball_time = hour2 + timedelta(minutes=2)
        exist_payment = StudentPayments.query.filter(StudentPayments.student_id == student.id).order_by(
            desc(StudentPayments.id)).first()
        if exist_payment:
            if exist_payment.payment_data:
                if hour2 >= exist_payment.payment_data:
                    exist_payment = StudentPayments(student_id=student.id, location_id=student.user.location_id,
                                                    calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                                    calendar_year=calendar_year.id, payment_type_id=payment_type.id,
                                                    payment_sum=payment_sum, account_period_id=accounting_period.id,
                                                    payment=status,
                                                    payment_data=ball_time)
                    db.session.add(exist_payment)
                    db.session.commit()
            else:
                exist_payment = StudentPayments(student_id=student.id, location_id=student.user.location_id,
                                                calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                                calendar_year=calendar_year.id, payment_type_id=payment_type.id,
                                                payment_sum=payment_sum, account_period_id=accounting_period.id,
                                                payment=status,
                                                payment_data=ball_time)
                db.session.add(exist_payment)
                db.session.commit()
        else:
            exist_payment = StudentPayments(student_id=student.id, location_id=student.user.location_id,
                                            calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                            calendar_year=calendar_year.id, payment_type_id=payment_type.id,
                                            payment_sum=payment_sum, account_period_id=accounting_period.id,
                                            payment=status,
                                            payment_data=ball_time)
            db.session.add(exist_payment)
            db.session.commit()

        all_payments = payment_sum
        if not attendance_history:
            if student.extra_payment:
                extra_payment = student.extra_payment + all_payments
            else:
                extra_payment = all_payments
            Students.query.filter(Students.id == student.id).update({"extra_payment": extra_payment})
            db.session.commit()
            st_functions = Student_Functions(student_id=student.id)
            st_functions.update_debt()
            st_functions.update_balance()
            return jsonify({
                "success": True,
                "msg": "To'lov qabul qilindi"
            })
        else:
            while all_payments > 0:
                attendance_history = AttendanceHistoryStudent.query.filter(
                    AttendanceHistoryStudent.student_id == student.id,
                    AttendanceHistoryStudent.status == False).order_by(AttendanceHistoryStudent.id).first()
                if not attendance_history:

                    if student.extra_payment:
                        extra_payment = student.extra_payment + all_payments
                    else:
                        extra_payment = all_payments

                    Students.query.filter(Students.id == student.id).update({"extra_payment": extra_payment})
                    db.session.commit()
                    break

                student_debt = abs(attendance_history.total_debt)
                if not attendance_history.remaining_debt:

                    result = all_payments + attendance_history.total_debt
                else:
                    result = all_payments + attendance_history.remaining_debt
                all_payments = result

                if all_payments < 0:
                    AttendanceHistoryStudent.query.filter(
                        AttendanceHistoryStudent.id == attendance_history.id).update(
                        {'remaining_debt': all_payments})
                    db.session.commit()
                    student_debt = abs(attendance_history.total_debt)
                    remaining_debt = abs(attendance_history.remaining_debt)
                    payment = student_debt - remaining_debt

                    AttendanceHistoryStudent.query.filter(
                        AttendanceHistoryStudent.id == attendance_history.id).update(
                        {'remaining_debt': all_payments, 'payment': payment})
                    db.session.commit()

                else:
                    AttendanceHistoryStudent.query.filter(
                        AttendanceHistoryStudent.id == attendance_history.id).update(
                        {'status': True, 'remaining_debt': 0, 'payment': student_debt})
                    db.session.commit()

                all_payments = result

        st_functions = Student_Functions(student_id=student.id)
        st_functions.update_debt()
        st_functions.update_balance()
        student = Students.query.filter(Students.id == student.id).first()
        if student.debtor == 0 or student.user.balance <= -50000:
            black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.student_id == student.id,
                                                             TeacherBlackSalary.status == False).all()
            for salary in black_salaries:
                salary.status = True
                salary.payment_id = exist_payment.id
                db.session.commit()
                teacher = Teachers.query.filter(Teachers.id == salary.teacher_id).first()
                update_salary(teacher.user_id)
        return jsonify({
            "success": True,
            "msg": "To'lov qabul qilindi"
        })
    else:
        group_list = []
        group_id_charity = []
        group_id = []
        groups = []
        for group in student.group:
            group_id.append(group.id)
        charity = db.session.query(Groups).join(Groups.charity).options(
            contains_eager(Groups.charity)).filter(Groups.id.in_([gr for gr in group_id]),
                                                   StudentCharity.student_id == student.id).all()
        for char in charity:
            group_id_charity.append(char.id)
            info = {
                "id": char.id,
                "name": char.name.title()
            }
            for st_char in char.charity:
                info['charity'] = st_char.discount
            group_list.append(info)

        for group in student.group:
            if group.id not in group_id_charity:
                groups.append(group.id)
        student_groups = db.session.query(Groups).join(Groups.student).options(contains_eager(Groups.student)).filter(
            Students.id == student.id, Groups.id.in_([gr for gr in groups])).all()
        for group in student_groups:
            info = {
                "id": group.id,
                "name": group.name.title(),

            }
            group_list.append(info)
        return jsonify({
            "payment": {
                "groups": group_list
            }
        })


@app.route(f'{api}/charity/<int:student_id>', methods=['POST'])
@jwt_required()
def charity(student_id):
    """
    add data to StudentCharity table
    :param student_id: Student table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    student = Students.query.filter(Students.user_id == student_id).first()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()

    group_id = int(get_json_field('group_id'))
    discount_amount = int(get_json_field('discount'))
    charity = StudentCharity.query.filter(StudentCharity.student_id == student.id,
                                          StudentCharity.group_id == group_id).first()
    if not charity:
        add = StudentCharity(student_id=student.id, discount=discount_amount, group_id=group_id,
                             calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                             calendar_year=calendar_year.id, account_period_id=accounting_period.id,
                             location_id=student.user.location_id)
        db.session.add(add)
        db.session.commit()
    else:
        StudentCharity.query.filter(StudentCharity.student_id == student.id,
                                    StudentCharity.group_id == group_id).update({
            "discount": discount_amount
        })
        db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Pul qabul qilindi"
    })


@app.route(f'{api}/book_payment/<int:user_id>', methods=['POST'])
def book_payment(user_id):
    """
    add data to BookPayments table
    :param user_id: User table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    student = Students.query.filter(Students.user_id == user_id).first()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    payment = get_json_field('bookPayment')
    add = BookPayments(location_id=student.user.location_id, calendar_day=calendar_day.id, student_id=student.id,
                       calendar_month=calendar_month.id, calendar_year=calendar_year.id, payment_sum=payment,
                       account_period_id=accounting_period.id)
    db.session.add(add)
    db.session.commit()
    st_functions = Student_Functions(student_id=student.id)
    st_functions.update_debt()
    st_functions.update_balance()
    return jsonify({
        'msg': 'Kitobga pul olindi',
        'success': True
    })
