from app import db, contains_eager, desc, extract

from backend.models.models import CalendarDay, Attendance, AttendanceDays, CalendarMonth, CalendarYear, StudentExcuses, \
    Students, StudentPayments, BookPayments, Users, AttendanceHistoryStudent, LessonPlan, Groups
from datetime import datetime

from backend.functions.utils import find_calendar_date, refreshdatas


class Group_Functions:
    def __init__(self, group_id):
        self.group_id = group_id

    def update_list_balance(self):
        refreshdatas()
        calendar_year, calendar_month, calendar_day = find_calendar_date()
        students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
            Groups.id == self.group_id).order_by('id').all()
        for student in students:
            student_get = Students.query.filter_by(id=student.id).first()
            attendance_history = AttendanceHistoryStudent.query.filter(
                AttendanceHistoryStudent.student_id == student_get.id,
            ).all()
            payments = StudentPayments.query.filter(StudentPayments.student_id == student_get.id).all()
            book_payments = BookPayments.query.filter(BookPayments.student_id == student_get.id).all()
            bk_payments = 0
            for book in book_payments:
                bk_payments += book.payment_sum
            all_payment = 0
            all_debt = 0
            old_money = 0
            old_debt = 0
            if student.old_debt:
                old_debt = student.old_debt
            if student.old_money:
                old_money = student.old_money
            for attendance in attendance_history:

                if attendance.total_debt:
                    all_debt += attendance.total_debt

            for pay in payments:
                all_payment += pay.payment_sum
            result = (all_payment + old_money) - (abs(all_debt) + abs(old_debt) + abs(bk_payments))

            # if result == 0:
            #     result = student.extra_payment
            student_excuse = StudentExcuses.query.filter(StudentExcuses.student_id == student_get.id,
                                                         StudentExcuses.to_date > calendar_day.date).order_by(
                desc(StudentExcuses.id)).first()
            if result == None:
                result = 0
            Users.query.filter(Users.id == student.user_id).update({'balance': result})

            db.session.commit()
            user = Users.query.filter(Users.id == student.user_id).first()
            if student.debtor != 4:
                if not student_excuse:
                    if user.balance >= 0:
                        Students.query.filter_by(id=student_get.id).update({"debtor": 0})
                    if user.balance < 0:
                        Students.query.filter_by(id=student_get.id).update({"debtor": 1})
                    if student.combined_debt:
                        if -user.balance >= -student.combined_debt:
                            Students.query.filter_by(id=student_get.id).update({"debtor": 2})
                else:
                    Students.query.filter_by(id=student_get.id).update({"debtor": 3})
                db.session.commit()

    def attendance_filter(self, month, year):
        date = str(year) + "-" + str(month)
        year = datetime.strptime(str(year), "%Y")
        date = datetime.strptime(date, "%Y-%m")

        calendar_year = CalendarYear.query.filter(CalendarYear.date == year).first()
        calendar_month = CalendarMonth.query.filter(CalendarMonth.year_id == calendar_year.id,
                                                    CalendarMonth.date == date).first()

        attendances = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
            contains_eager(AttendanceDays.attendance)).filter(Attendance.calendar_month == calendar_month.id,
                                                              Attendance.calendar_year == calendar_year.id,
                                                              Attendance.group_id == self.group_id).join(
            AttendanceDays.day).options(
            contains_eager(AttendanceDays.day)).order_by(CalendarDay.date).all()
        student_id = []
        for st in attendances:
            student_id.append(st.student_id)
        student_id = list(dict.fromkeys(student_id))
        students = Students.query.filter(Students.id.in_([st_id for st_id in student_id])).order_by(Students.id).all()
        students_num = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
            Groups.id == self.group_id).order_by(Students.id).count()
        attendances_list = []
        mixed_dates = []
        for_filter = []
        for att in attendances:
            mixed_dates.append(att.day.date.strftime("%d"))
            for_filter.append(att.day.date.strftime("%Y-%m-%d"))
        sorted_dates = list(dict.fromkeys(mixed_dates))
        sorted_dates.sort()
        for_filter = list(dict.fromkeys(for_filter))
        for_filter.sort()
        for student in students:
            student_att = {
                'student_name': student.user.name,
                'student_surname': student.user.surname,
                "student_id": student.user_id,
                'absent': [],
                'present': [],
                'len_days': 0,
                'dates': []
            }
            days = []
            for date in for_filter:
                day = datetime.strptime(date, "%Y-%m-%d")
                day = CalendarDay.query.filter(CalendarDay.date == day).first()
                attendance = AttendanceDays.query.filter(AttendanceDays.group_id == self.group_id,
                                                         AttendanceDays.student_id == student.id,
                                                         AttendanceDays.calendar_day == day.id).first()

                day_id = ""
                status = ""
                reason = ""
                if attendance:
                    day_id = attendance.calendar_day
                    if attendance.status == 1 or attendance.status == 2:
                        status = True
                    else:
                        status = False

                    if attendance.reason:
                        reason = attendance.reason
                homework = 0
                activeness = 0
                dictionary = 0
                average_ball = 0
                if attendance:
                    if attendance.homework:
                        homework = attendance.homework
                    if attendance.dictionary:
                        dictionary = attendance.dictionary
                    if attendance.activeness:
                        activeness = attendance.activeness
                    if attendance.average_ball:
                        average_ball = attendance.average_ball
                info = {
                    "day_id": day_id,
                    "day": date,
                    "reason": reason,
                    "status": status,
                    "ball": {}
                }
                if attendance:
                    if attendance.dictionary:
                        info['ball'] = {
                            "homework": homework,
                            "activeness": activeness,
                            "dictionary": dictionary,
                            "average_ball": average_ball
                        }
                    else:
                        info['ball'] = {
                            "homework": homework,
                            "activeness": activeness,
                            "average_ball": average_ball
                        }
                days.append(info)
                student_att['dates'] = days
            attendances_list.append(student_att)
        filtered_attendances = []
        for student in attendances_list:
            added_to_existing = False
            for merged in filtered_attendances:
                if merged['student_id'] == student['student_id']:
                    added_to_existing = True
                if added_to_existing:
                    break
            if not added_to_existing:
                filtered_attendances.append(student)

        data = {
            "attendances": filtered_attendances,
            "dates": sorted_dates,
            "students_num": students_num
        }

        return data

    def attendance_filter_android(self, month, year):
        date = str(year) + "-" + str(month)
        year = datetime.strptime(str(year), "%Y")
        date = datetime.strptime(date, "%Y-%m")

        calendar_year = CalendarYear.query.filter(CalendarYear.date == year).first()
        calendar_month = CalendarMonth.query.filter(CalendarMonth.year_id == calendar_year.id,
                                                    CalendarMonth.date == date).first()

        attendances = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
            contains_eager(AttendanceDays.attendance)).filter(Attendance.calendar_month == calendar_month.id,
                                                              Attendance.calendar_year == calendar_year.id,
                                                              Attendance.group_id == self.group_id).join(
            AttendanceDays.day).options(
            contains_eager(AttendanceDays.day)).order_by(CalendarDay.date).all()
        student_id = []
        for st in attendances:
            student_id.append(st.student_id)
        student_id = list(dict.fromkeys(student_id))
        students = Students.query.filter(Students.id.in_([st_id for st_id in student_id])).all()
        attendances_list = []
        mixed_dates = []
        for_filter = []
        for att in attendances:
            mixed_dates.append(att.day.date.strftime("%d"))
            for_filter.append(att.day.date.strftime("%Y-%m-%d"))
        sorted_dates = list(dict.fromkeys(mixed_dates))
        sorted_dates.sort()
        planned_days = []
        # exist_day = UsersMessages.query.filter(
        #     extract('day', UsersMessages.date) == int(message_get.date.strftime("%d")),
        #     extract('month', UsersMessages.date) == int(message_get.date.strftime("%m")),
        #     extract('year', UsersMessages.date) == int(message_get.date.strftime("%Y")),
        #     UsersMessages.id != message_get.id).first()
        calendar_year, calendar_month, calendar_day = find_calendar_date()
        for day in sorted_dates:
            blocked = False
            get_lesson_plan = LessonPlan.query.filter(LessonPlan.group_id == self.group_id,
                                                      extract('day', LessonPlan.date) == day,
                                                      extract('month', LessonPlan.date) == int(
                                                          calendar_month.date.strftime("%m")),
                                                      extract('year', LessonPlan.date) == int(
                                                          calendar_year.date.strftime("%Y"))).first()
            if int(calendar_day.date.strftime("%d")) > int(day):
                blocked = True
            if get_lesson_plan:
                info = {
                    "date": day,
                    "lesson_plan": get_lesson_plan.convert_json(),
                    "blocked": blocked
                }
            else:
                info = {
                    "date": day,
                    "lesson_plan": None,
                    "blocked": blocked
                }
            planned_days.append(info)
        for_filter = list(dict.fromkeys(for_filter))
        for_filter.sort()
        for student in students:
            student_att = {
                'student_name': student.user.name,
                'student_surname': student.user.surname,
                "student_id": student.user_id,
                'absent': [],
                'present': [],
                'len_days': 0,
                'dates': []
            }

            days = []
            for date in for_filter:
                day = datetime.strptime(date, "%Y-%m-%d")
                day = CalendarDay.query.filter(CalendarDay.date == day).first()
                attendance = AttendanceDays.query.filter(AttendanceDays.group_id == self.group_id,
                                                         AttendanceDays.student_id == student.id,
                                                         AttendanceDays.calendar_day == day.id).first()

                day_id = ""
                status = ""
                reason = ""
                if attendance:
                    day_id = attendance.calendar_day
                    if attendance.status == 1 or attendance.status == 2:
                        status = True
                    else:
                        status = False

                    if attendance.reason:
                        reason = attendance.reason
                homework = 0
                activeness = 0
                dictionary = 0
                average_ball = 0
                if attendance:
                    if attendance.homework:
                        homework = attendance.homework
                    if attendance.dictionary:
                        dictionary = attendance.dictionary
                    if attendance.activeness:
                        activeness = attendance.activeness
                    if attendance.average_ball:
                        average_ball = attendance.average_ball
                info = {
                    "day_id": day_id,
                    "day": date,
                    "reason": reason,
                    "status": status,
                    "ball": {}
                }
                if attendance:
                    if attendance.dictionary:
                        info['ball'] = {
                            "homework": homework,
                            "activeness": activeness,
                            "dictionary": dictionary,
                            "average_ball": average_ball
                        }
                    else:
                        info['ball'] = {
                            "homework": homework,
                            "activeness": activeness,
                            "average_ball": average_ball
                        }
                days.append(info)
                student_att['dates'] = days
            attendances_list.append(student_att)
        filtered_attendances = []
        for student in attendances_list:
            added_to_existing = False
            for merged in filtered_attendances:
                if merged['student_id'] == student['student_id']:
                    added_to_existing = True
                if added_to_existing:
                    break
            if not added_to_existing:
                filtered_attendances.append(student)

        data = {
            "attendances": filtered_attendances,
            "dates": planned_days
        }

        return data
