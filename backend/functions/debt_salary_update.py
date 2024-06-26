from app import *
from backend.models.models import *


def salary_debt(student_id, group_id, attendance_id, status_attendance,
                type_attendance):
    """
    update Student balance and Teacher balance
    :param student_id: Students primary key
    :param group_id: Groups primary key
    :param attendance_id: AttendanceDays primary key
    :param status_attendance: to separate new data and deleted data of AttendanceDays
    :param type_attendance: payment status or making attendace status
    :return:
    """
    group = Groups.query.filter(Groups.id == group_id).first()
    subject = Subjects.query.filter(Subjects.id == group.subject_id).first()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    attendancedays = AttendanceDays.query.filter(AttendanceDays.id == attendance_id).first()
    attendance = Attendance.query.filter(Attendance.id == attendancedays.attendance_id).first()
    months = int(attendance.month.date.strftime('%m'))
    current_year = int(attendance.year.date.strftime('%Y'))
    if status_attendance == True:
        db.session.delete(attendancedays)
        db.session.commit()
    attendance_history_student = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.calendar_month == attendance.calendar_month,
        AttendanceHistoryStudent.calendar_year == attendance.calendar_year,
        AttendanceHistoryStudent.student_id == student_id,
        AttendanceHistoryStudent.group_id == group_id,
        AttendanceHistoryStudent.subject_id == subject.id,
        AttendanceHistoryStudent.location_id == group.location_id,
        AttendanceHistoryStudent.calendar_year == attendance.calendar_year).first()
    attendance_student_balance = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.student_id == student_id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.location_id == group.location_id).all()

    total_balance = 0
    total_discount = 0
    for balance in attendance_student_balance:
        if not balance.discount:

            total_balance += balance.balance_per_day
        else:
            total_balance += balance.balance_with_discount
        if balance.discount_per_day:
            total_discount = balance.discount_per_day

    if attendance_history_student and attendance_history_student.payment:
        remaining_debt = total_balance - attendance_history_student.payment

        AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.id == attendance_history_student.id
                                              ).update({'remaining_debt': -remaining_debt})
        db.session.commit()
        student = Students.query.filter(Students.id == student_id).first()
        if type_attendance == "add":
            if student.extra_payment:
                payment = student.extra_payment + attendance_history_student.remaining_debt
                if payment > 0:
                    AttendanceHistoryStudent.query.filter(
                        AttendanceHistoryStudent.id == attendance_history_student.id).update({
                        "payment": total_balance, "remaining_debt": 0
                    })
                    Students.query.filter(Students.id == student_id).update({"extra_payment": payment})
                    db.session.commit()
                else:

                    residue_payment = attendance_history_student.payment + student.extra_payment
                    remaining_debt = total_balance - residue_payment
                    AttendanceHistoryStudent.query.filter(
                        AttendanceHistoryStudent.id == attendance_history_student.id).update({
                        "payment": residue_payment, "remaining_debt": remaining_debt
                    })
                    Students.query.filter(Students.id == student_id).update({"extra_payment": 0})
                    db.session.commit()
        else:
            if attendance_history_student.payment:
                if attendance_history_student.payment > total_balance:
                    extra_payment = attendance_history_student.payment - total_balance

                    if extra_payment > 0:
                        Students.query.filter(Students.id == student_id).update({"extra_payment": extra_payment})
                        db.session.commit()
                        AttendanceHistoryStudent.query.filter(
                            AttendanceHistoryStudent.id == attendance_history_student.id).update({
                            "payment": total_balance, "remaining_debt": 0
                        })
                        db.session.commit()
    attendance_student_present = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.student_id == student_id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.status == 1,
                                    AttendanceDays.location_id == group.location_id).count()
    attendance_student_absent = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.student_id == student_id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.status == 0,
                                    AttendanceDays.location_id == group.location_id).count()

    attendance_student_balls = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.student_id == student_id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.status == 2,
                                    AttendanceDays.location_id == group.location_id).all()
    scored_days = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.student_id == student_id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.status == 2,
                                    AttendanceDays.location_id == group.location_id).count()
    total_average = 0
    for ball in attendance_student_balls:
        total_average += ball.average_ball
    if len(attendance_student_balls) != 0:
        total_average = round(total_average / len(attendance_student_balls))
    if not attendance_history_student:
        add = AttendanceHistoryStudent(student_id=student_id, subject_id=subject.id, group_id=group_id,
                                       total_debt=-total_balance, present_days=attendance_student_present,
                                       absent_days=attendance_student_absent, average_ball=total_average,
                                       location_id=group.location_id, calendar_month=attendance.calendar_month,
                                       calendar_year=attendance.calendar_year, total_discount=total_discount,
                                       scored_days=scored_days)
        db.session.add(add)
        db.session.commit()
    else:
        AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.calendar_month == attendance.calendar_month,
                                              AttendanceHistoryStudent.calendar_year == attendance.calendar_year,
                                              AttendanceHistoryStudent.student_id == student_id,
                                              AttendanceHistoryStudent.group_id == group_id,
                                              AttendanceHistoryStudent.subject_id == subject.id,
                                              AttendanceHistoryStudent.location_id == group.location_id
                                              ).update(
            {"total_debt": -total_balance, "present_days": attendance_student_present,
             "absent_days": attendance_student_absent, "average_ball": total_average, 'total_discount': total_discount,
             "scored_days": scored_days
             })
        db.session.commit()
    attendance_history_student = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.calendar_month == attendance.calendar_month,
        AttendanceHistoryStudent.calendar_year == attendance.calendar_year,
        AttendanceHistoryStudent.student_id == student_id,
        AttendanceHistoryStudent.group_id == group_id,
        AttendanceHistoryStudent.subject_id == subject.id,
        AttendanceHistoryStudent.location_id == group.location_id).first()

    if attendance_history_student.payment and attendance_history_student.payment >= abs(
            attendance_history_student.total_debt):
        AttendanceHistoryStudent.query.filter(
            AttendanceHistoryStudent.calendar_month == attendance_history_student.calendar_month,
            AttendanceHistoryStudent.calendar_year == attendance_history_student.calendar_year,
            AttendanceHistoryStudent.student_id == student_id,
            AttendanceHistoryStudent.group_id == group_id,
            AttendanceHistoryStudent.subject_id == subject.id,
            AttendanceHistoryStudent.location_id == group.location_id).update({'status': True})
        db.session.commit()
    else:
        AttendanceHistoryStudent.query.filter(
            AttendanceHistoryStudent.calendar_month == attendance_history_student.calendar_month,
            AttendanceHistoryStudent.calendar_year == attendance_history_student.calendar_year,
            AttendanceHistoryStudent.student_id == student_id,
            AttendanceHistoryStudent.group_id == group_id,
            AttendanceHistoryStudent.subject_id == subject.id,
            AttendanceHistoryStudent.location_id == group.location_id).update({'status': False})
        db.session.commit()

    debts = 0
    payments = 0
    debt_list = AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.student_id == student_id,
                                                      AttendanceHistoryStudent.calendar_month == attendance.calendar_month,
                                                      AttendanceHistoryStudent.calendar_year == attendance.calendar_year).all()
    for debt in debt_list:
        if debt.total_debt:
            debts += debt.total_debt
        if debt.payment:
            payments += debt.payment

    attendance_teacher = AttendanceHistoryTeacher.query.filter(
        AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
        AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
        AttendanceHistoryTeacher.teacher_id == teacher.id,
        AttendanceHistoryTeacher.group_id == group_id,
        AttendanceHistoryTeacher.subject_id == subject.id,
        AttendanceHistoryTeacher.location_id == group.location_id).first()
    attendance_teacher_salary = db.session.query(AttendanceDays).join(AttendanceDays.day).options(contains_eager(
        AttendanceDays.day)).filter(extract("year", CalendarDay.date) == current_year,
                                    extract("month", CalendarDay.date) == months,
                                    AttendanceDays.teacher_id == teacher.id, AttendanceDays.group_id == group_id,
                                    AttendanceDays.location_id == group.location_id).all()
    total_salary = 0
    for salary in attendance_teacher_salary:
        total_salary += salary.salary_per_day
    if not attendance_teacher:
        attendance_teacher = AttendanceHistoryTeacher(teacher_id=teacher.id, group_id=group_id,
                                                      subject_id=subject.id, total_salary=total_salary,
                                                      location_id=group.location_id,
                                                      calendar_month=attendance.calendar_month,
                                                      calendar_year=attendance.calendar_year)
        db.session.add(attendance_teacher)
        db.session.commit()
    else:
        AttendanceHistoryTeacher.query.filter(AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
                                              AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
                                              AttendanceHistoryTeacher.teacher_id == teacher.id,
                                              AttendanceHistoryTeacher.group_id == group_id,
                                              AttendanceHistoryTeacher.subject_id == subject.id,
                                              AttendanceHistoryTeacher.location_id == group.location_id).update(
            {"total_salary": total_salary, 'status': False})
        db.session.commit()
    attendance_teacher = AttendanceHistoryTeacher.query.filter(
        AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
        AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
        AttendanceHistoryTeacher.teacher_id == teacher.id,
        AttendanceHistoryTeacher.group_id == group_id,
        AttendanceHistoryTeacher.subject_id == subject.id,
        AttendanceHistoryTeacher.location_id == group.location_id).first()
    if attendance_teacher.taken_money:
        remaining_salary = attendance_teacher.total_salary - attendance_teacher.taken_money
        AttendanceHistoryTeacher.query.filter(
            AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
            AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
            AttendanceHistoryTeacher.teacher_id == teacher.id,
            AttendanceHistoryTeacher.group_id == group_id,
            AttendanceHistoryTeacher.subject_id == subject.id,
            AttendanceHistoryTeacher.location_id == group.location_id).update({'remaining_salary': remaining_salary})
        db.session.commit()
    status = False
    if attendance_teacher and attendance_teacher.taken_money:
        if attendance_teacher.taken_money >= attendance_teacher.total_salary:
            status = True
        else:
            status = False
    AttendanceHistoryTeacher.query.filter(
        AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
        AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
        AttendanceHistoryTeacher.teacher_id == teacher.id,
        AttendanceHistoryTeacher.group_id == group_id,
        AttendanceHistoryTeacher.subject_id == subject.id,
        AttendanceHistoryTeacher.location_id == group.location_id).update({"status": status})
    db.session.commit()
    salary_history = AttendanceHistoryTeacher.query.filter(
        AttendanceHistoryTeacher.calendar_month == attendance.calendar_month,
        AttendanceHistoryTeacher.calendar_year == attendance.calendar_year,
        AttendanceHistoryTeacher.teacher_id == teacher.id, AttendanceHistoryTeacher.location_id == group.location_id,
    ).all()

    salary_location_total = 0
    for salary in salary_history:
        salary_location_total += salary.total_salary
    salary_location = TeacherSalary.query.filter(TeacherSalary.location_id == group.location_id,
                                                 TeacherSalary.teacher_id == teacher.id,
                                                 TeacherSalary.calendar_year == attendance.calendar_year,
                                                 TeacherSalary.calendar_month == attendance.calendar_month).first()
    if not salary_location:

        salary_location = TeacherSalary(location_id=group.location_id,
                                        teacher_id=teacher.id,
                                        calendar_month=attendance.calendar_month,
                                        calendar_year=attendance.calendar_year,
                                        total_salary=salary_location_total)
        db.session.add(salary_location)
        db.session.commit()
    else:
        TeacherSalary.query.filter(TeacherSalary.location_id == group.location_id,
                                   TeacherSalary.teacher_id == teacher.id,
                                   TeacherSalary.calendar_year == attendance.calendar_year,
                                   TeacherSalary.calendar_month == attendance.calendar_month,
                                   ).update({"total_salary": salary_location_total, 'status': False})
        db.session.commit()
    salary_location = TeacherSalary.query.filter(TeacherSalary.location_id == group.location_id,
                                                 TeacherSalary.teacher_id == teacher.id,
                                                 TeacherSalary.calendar_year == attendance.calendar_year,
                                                 TeacherSalary.calendar_month == attendance.calendar_month).first()
    black_salaries = TeacherBlackSalary.query.filter(TeacherBlackSalary.teacher_id == teacher.id).filter(
        or_(TeacherBlackSalary.status == False, TeacherBlackSalary.status == None,
            TeacherBlackSalary.salary_id == salary_location.id)).all()
    black_salary = 0
    for salary in black_salaries:
        black_salary += salary.total_salary

    if salary_location.taken_money:
        remaining_salary = salary_location.total_salary - (salary_location.taken_money + black_salary)
        TeacherSalary.query.filter(TeacherSalary.location_id == group.location_id,
                                   TeacherSalary.teacher_id == teacher.id,
                                   TeacherSalary.calendar_year == attendance.calendar_year,
                                   TeacherSalary.calendar_month == attendance.calendar_month).update(
            {'remaining_salary': remaining_salary})
        db.session.commit()
    if salary_location and salary_location.taken_money:
        if salary_location.taken_money >= salary_location.total_salary:
            salary_location.status = True
        else:
            salary_location.status = False

    return salary_location


def staff_salary_update():
    """
    create salary data in StaffSalary table
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    staff = Staff.query.order_by(Staff.id).all()
    for item in staff:
        if item.salary:
            staff_salary_info = StaffSalary.query.filter(StaffSalary.calendar_month == calendar_month.id,
                                                         StaffSalary.calendar_year == calendar_year.id,
                                                         StaffSalary.staff_id == item.id).first()
            if not staff_salary_info:
                staff_salary_info = StaffSalary(calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                                total_salary=item.salary, staff_id=item.id,
                                                location_id=item.user.location_id)
                db.session.add(staff_salary_info)
                db.session.commit()
