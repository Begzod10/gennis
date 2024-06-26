from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from backend.functions.utils import api
import uuid
from backend.models.models import Roles
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import jwt_required
import requests
from backend.student.class_model import Student_Functions


@app.route(f'{api}/get_api')
def get_api():
    response = requests.get("http://176.96.243.55/api/transfer")

    # teacher_salaries = db.session.query(StudentPayments).join(StudentPayments.day).options(
    #     contains_eager(StudentPayments.day)).filter(
    #     CalendarDay.date < datetime.strptime("2023-04-02", "%Y-%m-%d")).order_by(StudentPayments.id).all()
    # print(len(teacher_salaries))
    # subjects = response.json()['subjects_list']
    # for subject in subjects:
    #     subject_add = Subjects.query.filter(Subjects.name == subject['name'],
    #                                         Subjects.ball_number == subject['ball_number']).first()
    #     if not subject_add:
    #         subject_add = Subjects(name=subject['name'], ball_number=subject['ball_number'], old_id=subject['old_id'])
    #         db.session.add(subject_add)
    #         db.session.commit()
    roles_list = response.json()['roles_list']
    for role in roles_list:
        type_role = ''
        if role['admin']:
            type_role = 'admin'
        elif role['student']:
            type_role = 'student'
        elif role['user']:
            type_role = 'user'
        elif role['teacher']:
            type_role = 'teacher'
        elif role['smm']:
            type_role = 'smm'
        elif role['programmer']:
            type_role = 'programmer'
        elif role['director']:
            type_role = 'director'

        role_add = Roles.query.filter(Roles.type_role == type_role, Roles.role == role['role']).first()
        if not role_add:
            role_add = Roles(type_role=type_role, role=role['role'], old_id=role['old_id'])
            db.session.add(role_add)
            db.session.commit()
    # professions_list = response.json()['professions_list']
    # for profession in professions_list:
    #     profession_add = Professions.query.filter(Professions.name == profession['name']).first()
    #     if not profession_add:
    #         profession_add = Professions(name=profession['name'], old_id=profession['old_id'])
    #         db.session.add(profession_add)
    #         db.session.commit()
    # education_languages_list = response.json()['education_languages_list']
    # for language in education_languages_list:
    #     language_add = EducationLanguage.query.filter(EducationLanguage.name == language['name']).first()
    #     if not language_add:
    #         language_add = EducationLanguage(name=language['name'], old_id=language['old_id'])
    #         db.session.add(language_add)
    #         db.session.commit()
    #
    # course_types_list = response.json()['course_types_list']
    # for course in course_types_list:
    #     course_add = CourseTypes.query.filter(CourseTypes.name == course['name']).first()
    #     if not course_add:
    #         course_add = CourseTypes(name=course['name'], old_id=course['old_id'])
    #         db.session.add(course_add)
    #         db.session.commit()
    # payment_type_list = response.json()['payment_type_list']
    # for payment_type in payment_type_list:
    #     payment_type_add = PaymentTypes.query.filter(PaymentTypes.name == payment_type['name']).first()
    #     if not payment_type_add:
    #         payment_type_add = PaymentTypes(name=payment_type['name'], old_id=payment_type['old_id'])
    #         db.session.add(payment_type_add)
    #         db.session.commit()
    #
    # years_list = response.json()['years_list']
    # for year in years_list:
    #     year_add = CalendarYear.query.filter(CalendarYear.date == datetime.strptime(year['date'], "%Y")).first()
    #     if not year_add:
    #         year_add = CalendarYear(date=datetime.strptime(year['date'], "%Y"))
    #         db.session.add(year_add)
    #         db.session.commit()
    # months_list = response.json()['months_list']
    # for month in months_list:
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == month['year_id']).first()
    #     month_add = CalendarMonth.query.filter(CalendarMonth.date == datetime.strptime(month['date'], "%Y-%m"),
    #                                            CalendarMonth.year_id == calendar_year.id).first()
    #     if not month_add:
    #         month_add = CalendarMonth(date=datetime.strptime(month['date'], "%Y-%m"), year_id=calendar_year.id,
    #                                   old_id=month['old_id'])
    #         db.session.add(month_add)
    #         db.session.commit()
    #
    # accounting_periods_list = response.json()['accounting_periods_list']
    # for period in accounting_periods_list:
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == period['year_id']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.id == period['month_id']).first()
    #     period_add = AccountingPeriod.query.filter(
    #         AccountingPeriod.from_date == datetime.strptime(period['from_date'], "%Y-%m-%d"),
    #         AccountingPeriod.to_date == datetime.strptime(period['to_date'], "%Y-%m-%d"),
    #         AccountingPeriod.year_id == calendar_year.id, AccountingPeriod.month_id == calendar_month.id).first()
    #     if not period_add:
    #         period_add = AccountingPeriod(from_date=datetime.strptime(period['from_date'], "%Y-%m-%d"),
    #                                       to_date=datetime.strptime(period['to_date'], "%Y-%m-%d"),
    #                                       year_id=calendar_year.id, month_id=calendar_month.id, old_id=period['old_id'])
    #         db.session.add(period_add)
    #         db.session.commit()
    # days_list = response.json()['days_list']
    # for day in days_list:
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.id == day['month_id']).first()
    #     if day['account_period_id']:
    #
    #         account_period = AccountingPeriod.query.filter(AccountingPeriod.id == day['account_period_id']).first()
    #         day_add = CalendarDay.query.filter(CalendarDay.date == datetime.strptime(day['date'], "%Y-%m-%d"),
    #                                            CalendarDay.month_id == calendar_month.id,
    #                                            CalendarDay.account_period_id == account_period.id).first()
    #         if not day_add:
    #             day_add = CalendarDay(date=datetime.strptime(day['date'], "%Y-%m-%d"),
    #                                   month_id=calendar_month.id, old_id=day['old_id'],
    #                                   account_period_id=account_period.id)
    #             db.session.add(day_add)
    #             db.session.commit()
    #     else:
    #         day_add = CalendarDay.query.filter(CalendarDay.date == datetime.strptime(day['date'], "%Y-%m-%d"),
    #                                            CalendarDay.month_id == calendar_month.id,
    #                                            ).first()
    #         if not day_add:
    #             day_add = CalendarDay(date=datetime.strptime(day['date'], "%Y-%m-%d"),
    #                                   month_id=calendar_month.id, old_id=day['old_id'],
    #                                   )
    #             db.session.add(day_add)
    #             db.session.commit()
    #
    # locations_list = response.json()['locations_list']
    # for location in locations_list:
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == location['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == location['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == location['calendar_year']).first()
    #
    #     add_location = Locations.query.filter(Locations.name == location['name'],
    #                                           Locations.calendar_year == calendar_year.id,
    #                                           Locations.calendar_month == calendar_month.id,
    #                                           Locations.calendar_day == calendar_day.id).first()
    #     if not add_location:
    #         add_location = Locations(name=location['name'],
    #                                  calendar_year=calendar_year.id,
    #                                  calendar_month=calendar_month.id,
    #                                  calendar_day=calendar_day.id, old_id=location['old_id'])
    #         db.session.add(add_location)
    #         db.session.commit()
    #
    # rooms_list = response.json()['rooms_list']
    # for room in rooms_list:
    #     location = Locations.query.filter(Locations.old_id == room['location_id']).first()
    #     room_add = Rooms.query.filter(Rooms.name == room['name'], Rooms.location_id == location.id).first()
    #     if not room_add:
    #         room_add = Rooms(name=room['name'], location_id=location.id, seats_number=room['seats_number'],
    #                          electronic_board=room['electronic_board'], old_id=room['old_id'])
    #         db.session.add(room_add)
    #         db.session.commit()
    #         for subject in room['subjects']:
    #             subject_get = Subjects.query.filter(Subjects.old_id == subject['id']).first()
    #             room_add.subject.append(subject_get)
    #             db.session.commit()
    #
    # week_list = response.json()['week_list']
    # for week in week_list:
    #     location = Locations.query.filter(Locations.old_id == week['location_id']).first()
    #     week_add = Week.query.filter(Week.name == week['name'], Week.location_id == location.id).first()
    #     if not week_add:
    #         week_add = Week(name=week['name'], location_id=location.id, eng_name=week['eng_name'],
    #                         order=week['order'], old_id=week['old_id'])
    #         db.session.add(week_add)
    #         db.session.commit()

    # users_list = response.json()['users_list']
    # for user in users_list:
    #     location = Locations.query.filter(Locations.old_id == user['location_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == user['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == user['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == user['calendar_year']).first()
    #     education_language = EducationLanguage.query.filter(
    #         EducationLanguage.old_id == user['education_language']).first()
    #     role = Roles.query.filter(Roles.old_id == user['role_id']).first()
    #     add_user = Users.query.filter(Users.name == user['name'], Users.username == user['username'],
    #                                   Users.surname == user['surname'], Users.location_id == location.id).first()
    #     if not add_user:
    #         add_user = Users(name=user['name'], username=user['username'],
    #                          surname=user['surname'], location_id=location.id,
    #                          education_language=education_language.id, role_id=role.id, calendar_year=calendar_year.id,
    #                          calendar_month=calendar_month.id, calendar_day=calendar_day.id, old_id=user['old_id'],
    #                          password=user['password'], father_name=user['father_name'], director=user['director'],
    #                          comment=user['comment'], born_year=user['born_year'], born_month=user['born_month'],
    #                          born_day=user['born_day'], balance=user['balance'], age=user['age'],
    #                          photo_profile=user['photo_profile'], user_id=user['user_id'])
    #         db.session.add(add_user)
    #         db.session.commit()
    #         for phone in user['phone_list']:
    #             phone_add = PhoneList(other=phone['other'], parent=phone['parent'], personal=phone['personal'],
    #                                   phone=phone['phone'], user_id=add_user.id)
    #             db.session.add(phone_add)
    #             db.session.commit()
    # users = Users.query.all()
    # print(len(users))

    # staff_list = response.json()['staff_list']
    # for staff in staff_list:
    #     user = Users.query.filter(Users.old_id == staff['user_id']).first()
    #     profession = Professions.query.filter(Professions.old_id == staff['profession_id']).first()
    #     add_staff = Staff.query.filter(Staff.profession_id == profession.id, Staff.user_id == user.id).first()
    #     if not add_staff:
    #         add_staff = Staff(profession_id=profession.id, user_id=user.id, salary=staff['salary'], old_id=staff['id'])
    #         db.session.add(add_staff)
    #         db.session.commit()
    # staffs = Staff.query.all()
    # print(len(staffs))
    #
    # students_list = response.json()['students_list']
    # for student in students_list:
    #     user = Users.query.filter(Users.old_id == student['user_id']).first()
    #     student_add = Students.query.filter(Students.user_id == user.id).first()
    #     if not student_add:
    #         student_add = Students(ball_time=student['ball_time'], combined_debt=student['combined_debt'],
    #                                contract_pdf_url=student['contract_pdf_url'], old_id=student['old_id'],
    #                                contract_word_url=student['contract_word_url'], debtor=student['debtor'],
    #                                extra_payment=student['extra_payment'], morning_shift=student['morning_shift'],
    #                                night_shift=student['night_shift'], old_debt=student['old_debt'],
    #                                old_money=student['old_money'], representative_name=student['representative_name'],
    #                                representative_surname=student['representative_surname'], user_id=user.id)
    #         db.session.add(student_add)
    #         db.session.commit()
    #         for sub in student['subjects']:
    #             subject_get = Subjects.query.filter(Subjects.old_id == sub['id']).first()
    #             student_add.subject.append(subject_get)
    #             db.session.commit()
    #         for group in student['groups']:
    #             location = Locations.query.filter(Locations.old_id == group['location_id']).first()
    #             calendar_day = CalendarDay.query.filter(CalendarDay.old_id == group['calendar_day']).first()
    #             calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == group['calendar_month']).first()
    #             calendar_year = CalendarYear.query.filter(CalendarYear.id == group['calendar_year']).first()
    #             education_language = EducationLanguage.query.filter(
    #                 EducationLanguage.old_id == group['education_language']).first()
    #             course_type = CourseTypes.query.filter(CourseTypes.old_id == group['course_type_id']).first()
    #             subject = Subjects.query.filter(Subjects.old_id == group['subject_id']).first()
    #             teacher = group['teacher']
    #             user_teacher = Users.query.filter(Users.old_id == teacher['user_id']).first()
    #             teacher_add = Teachers.query.filter(Teachers.old_id == teacher['id'],
    #                                                 Teachers.user_id == user_teacher.id).first()
    #             if not teacher_add:
    #                 teacher_add = Teachers(old_id=teacher['id'], user_id=user_teacher.id,
    #                                        table_color=teacher['table_color'])
    #                 db.session.add(teacher_add)
    #                 db.session.commit()
    #
    #             group_add = Groups.query.filter(Groups.name == group['name'],
    #                                             Groups.teacher_id == teacher_add.id).first()
    #             if not group_add:
    #                 group_add = Groups(name=group['name'], teacher_id=teacher_add.id, calendar_day=calendar_day.id,
    #                                    calendar_month=calendar_month.id, calendar_year=calendar_year.id,
    #                                    course_type_id=course_type.id, deleted=group['deleted'],
    #                                    education_language=education_language.id, location_id=location.id,
    #                                    old_id=group['old_id'], price=group['price'], status=group['status'],
    #                                    subject_id=subject.id, teacher_salary=group['teacher_salary'])
    #                 db.session.add(group_add)
    #                 db.session.commit()
    #             if group_add not in student_add.group:
    #                 student_add.group.append(group_add)
    #                 db.session.commit()
    #             if group_add not in teacher_add.group:
    #                 teacher_add.group.append(group_add)
    #                 db.session.commit()
    #             if subject not in teacher_add.subject:
    #                 teacher_add.subject.append(subject)
    #                 db.session.commit()
    # students = Students.query.all()
    # print(len(students))

    # attendance_history_students_list = response.json()['attendance_history_students_list']
    # print(len(attendance_history_students_list))
    # for attendance in attendance_history_students_list:
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == attendance['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == attendance['calendar_year']).first()
    #     group_id = Groups.query.filter(Groups.old_id == attendance['group_id']).first()
    #     location_id = Locations.query.filter(Locations.old_id == attendance['location_id']).first()
    #     student_id = Students.query.filter(Students.old_id == attendance['student_id']).first()
    #     subject_id = Subjects.query.filter(Subjects.old_id == attendance['subject_id']).first()
    #     gr_id = None
    #     if group_id:
    #         gr_id = group_id.id
    #     attendance_add = AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.student_id == student_id.id,
    #                                                            AttendanceHistoryStudent.location_id == location_id.id,
    #                                                            AttendanceHistoryStudent.subject_id == subject_id.id,
    #                                                            AttendanceHistoryStudent.calendar_month == calendar_month.id,
    #                                                            AttendanceHistoryStudent.calendar_year == calendar_year.id,
    #                                                            AttendanceHistoryStudent.group_id == gr_id,
    #                                                            AttendanceHistoryStudent.total_debt == attendance[
    #                                                                'total_debt'],
    #                                                            AttendanceHistoryStudent.average_ball == attendance[
    #                                                                'average_ball'],
    #                                                            AttendanceHistoryStudent.absent_days == attendance[
    #                                                                'absent_days'],
    #                                                            AttendanceHistoryStudent.payment == attendance[
    #                                                                'payment'],
    #                                                            AttendanceHistoryStudent.scored_days == attendance[
    #                                                                'scored_days'],
    #                                                            AttendanceHistoryStudent.total_discount == attendance[
    #                                                                'total_discount'],
    #                                                            AttendanceHistoryStudent.remaining_debt == attendance[
    #                                                                'remaining_debt'],
    #                                                            AttendanceHistoryStudent.present_days == attendance[
    #                                                                'present_days'],
    #
    #                                                            ).first()
    #     if not attendance_add:
    #         attendance_add = AttendanceHistoryStudent(student_id=student_id.id,
    #                                                   absent_days=attendance['absent_days'],
    #                                                   location_id=location_id.id, old_id=attendance['old_id'],
    #                                                   average_ball=attendance['average_ball'],
    #                                                   subject_id=subject_id.id, payment=attendance['payment'],
    #                                                   calendar_month=calendar_month.id, status=attendance['status'],
    #                                                   scored_days=attendance['scored_days'],
    #                                                   total_debt=attendance['total_debt'],
    #                                                   total_discount=attendance['total_discount'],
    #                                                   remaining_debt=attendance['remaining_debt'],
    #                                                   present_days=attendance['present_days'],
    #                                                   calendar_year=calendar_year.id,
    #                                                   group_id=gr_id)
    #         db.session.add(attendance_add)
    #         db.session.commit()
    #
    # attendances = AttendanceHistoryStudent.query.all()
    # print(len(attendances))

    # attendance_history_teachers_list = response.json()['attendance_history_teachers_list']
    # for attendance in attendance_history_teachers_list:
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == attendance['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == attendance['calendar_year']).first()
    #     group_id = Groups.query.filter(Groups.old_id == attendance['group_id']).first()
    #     location_id = Locations.query.filter(Locations.old_id == attendance['location_id']).first()
    #     teacher_id = Teachers.query.filter(Teachers.old_id == attendance['teacher_id']).first()
    #     subject_id = Subjects.query.filter(Subjects.old_id == attendance['subject_id']).first()
    #
    #     gr_id = None
    #     if group_id:
    #         gr_id = group_id.id
    #     teach_id = None
    #     if teacher_id:
    #         teach_id = teacher_id.id
    #     attendance_add = AttendanceHistoryTeacher.query.filter(AttendanceHistoryTeacher.teacher_id == teach_id,
    #                                                            AttendanceHistoryTeacher.location_id == location_id.id,
    #                                                            AttendanceHistoryTeacher.subject_id == subject_id.id,
    #                                                            AttendanceHistoryTeacher.calendar_month == calendar_month.id,
    #                                                            AttendanceHistoryTeacher.calendar_year == calendar_year.id,
    #                                                            AttendanceHistoryTeacher.group_id == gr_id,
    #                                                            AttendanceHistoryTeacher.status == attendance['status'],
    #                                                            AttendanceHistoryTeacher.taken_money == attendance[
    #                                                                'taken_money'],
    #                                                            AttendanceHistoryTeacher.remaining_salary == attendance[
    #                                                                'remaining_salary'],
    #                                                            AttendanceHistoryTeacher.total_salary == attendance[
    #                                                                'total_salary'],
    #                                                            ).first()
    #     if not attendance_add:
    #         attendance_add = AttendanceHistoryTeacher(teacher_id=teach_id, old_id=attendance['old_id'],
    #                                                   location_id=location_id.id, status=attendance['status'],
    #                                                   remaining_salary=attendance['remaining_salary'],
    #                                                   subject_id=subject_id.id, taken_money=attendance['taken_money'],
    #                                                   calendar_month=calendar_month.id,
    #                                                   calendar_year=calendar_year.id,
    #                                                   total_salary=attendance['total_salary'],
    #                                                   group_id=gr_id)
    #         db.session.add(attendance_add)
    #         db.session.commit()
    # attendances = AttendanceHistoryTeacher.query.order_by(AttendanceHistoryTeacher.id).all()
    # print(len(attendances))

    # attendance_list = response.json()['attendance_list']
    # for attendance in attendance_list:
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == attendance['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == attendance['calendar_year']).first()
    #     group_id = Groups.query.filter(Groups.old_id == attendance['group_id']).first()
    #     location_id = Locations.query.filter(Locations.old_id == attendance['location_id']).first()
    #     teacher_id = Teachers.query.filter(Teachers.old_id == attendance['teacher_id']).first()
    #     subject_id = Subjects.query.filter(Subjects.old_id == attendance['subject_id']).first()
    #     course_id = CourseTypes.query.filter(CourseTypes.old_id == attendance['course_id']).first()
    #     student_id = Students.query.filter(Students.old_id == attendance['student_id']).first()
    #     gr_id = None
    #     teach_id = None
    #     if group_id:
    #         gr_id = group_id.id
    #     if teacher_id:
    #         teach_id = teacher_id.id
    #
    #     attendance_add = Attendance.query.filter(Attendance.teacher_id == teach_id,
    #                                              Attendance.location_id == location_id.id,
    #                                              Attendance.subject_id == subject_id.id,
    #                                              Attendance.calendar_month == calendar_month.id,
    #                                              Attendance.calendar_year == calendar_year.id,
    #                                              Attendance.group_id == gr_id,
    #                                              Attendance.student_id == student_id.id,
    #                                              Attendance.course_id == course_id.id).first()
    #     if not attendance_add:
    #         attendance_add = Attendance(teacher_id=teach_id,
    #                                     location_id=location_id.id,
    #                                     subject_id=subject_id.id,
    #                                     calendar_month=calendar_month.id,
    #                                     calendar_year=calendar_year.id,
    #                                     group_id=gr_id, old_id=attendance['old_id'],
    #                                     student_id=student_id.id,
    #                                     course_id=course_id.id)
    #         db.session.add(attendance_add)
    #         db.session.commit()
    # all_attendances = Attendance.query.all()
    # print(len(all_attendances))

    # attendance_days_list = response.json()['attendance_days_list']
    # for attendance in attendance_days_list:
    #     attendance_id = Attendance.query.filter(Attendance.old_id == attendance['attendance_id']).first()
    #     group_id = Groups.query.filter(Groups.old_id == attendance['group_id']).first()
    #     location_id = Locations.query.filter(Locations.old_id == attendance['location_id']).first()
    #     teacher_id = Teachers.query.filter(Teachers.old_id == attendance['teacher_id']).first()
    #     student_id = Students.query.filter(Students.old_id == attendance['student_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == attendance['calendar_day']).first()
    #     gr_id = None
    #     if group_id:
    #         gr_id = group_id.id
    #     att_id = None
    #     if attendance_id:
    #         att_id = attendance_id.id
    #     day = None
    #     if calendar_day:
    #         day = calendar_day.id
    #     teach_id = None
    #
    #     if teacher_id:
    #         teach_id = teacher_id.id
    #     attendance_add = AttendanceDays.query.filter(AttendanceDays.group_id == gr_id,
    #                                                  AttendanceDays.location_id == location_id.id,
    #                                                  AttendanceDays.attendance_id == att_id,
    #                                                  AttendanceDays.teacher_id == teach_id,
    #                                                  AttendanceDays.student_id == student_id.id,
    #                                                  AttendanceDays.calendar_day == day).first()
    #     if not attendance_add:
    #         attendance_add = AttendanceDays(group_id=gr_id, activeness=attendance['activeness'],
    #                                         average_ball=attendance['average_ball'],
    #                                         balance_per_day=attendance['balance_per_day'],
    #                                         balance_with_discount=attendance['balance_with_discount'],
    #                                         dictionary=attendance['dictionary'], discount=attendance['discount'],
    #                                         location_id=location_id.id, calendar_day=day,
    #                                         discount_per_day=attendance['discount_per_day'],
    #                                         attendance_id=att_id, homework=attendance['homework'],
    #                                         reason=attendance['reason'],
    #                                         salary_per_day=attendance['salary_per_day'],
    #                                         teacher_id=teach_id, status=attendance['status'],
    #                                         student_id=student_id.id)
    #         db.session.add(attendance_add)
    #         db.session.commit()
    # all_attendances = AttendanceDays.query.all()
    # print(len(all_attendances))

    # student_payments_list = response.json()['student_payments_list']
    # for payment in student_payments_list:
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == payment['account_period_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == payment['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == payment['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == payment['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == payment['location_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == payment['payment_type_id']).first()
    #     student_id = Students.query.filter(Students.old_id == payment['student_id']).first()
    #
    #     if calendar_day:
    #         payment_add = StudentPayments.query.filter(StudentPayments.student_id == student_id.id,
    #                                                    StudentPayments.location_id == location_id.id,
    #                                                    StudentPayments.calendar_day == calendar_day.id,
    #                                                    StudentPayments.calendar_month == calendar_month.id,
    #                                                    StudentPayments.account_period_id == account_period_id.id,
    #                                                    StudentPayments.payment_type_id == payment_type_id.id,
    #                                                    StudentPayments.calendar_year == calendar_year.id,
    #                                                    StudentPayments.payment_sum == payment['payment_sum'],
    #                                                    StudentPayments.old_id == payment['old_id'],
    #                                                    ).first()
    #         if not payment_add:
    #             payment_add = StudentPayments(student_id=student_id.id, payment_sum=payment['payment_sum'],
    #                                           location_id=location_id.id, payment=payment['payment'],
    #                                           calendar_day=calendar_day.id, old_id=payment['old_id'],
    #                                           calendar_month=calendar_month.id,
    #                                           account_period_id=account_period_id.id,
    #                                           payment_type_id=payment_type_id.id,
    #                                           calendar_year=calendar_year.id)
    #             db.session.add(payment_add)
    #             db.session.commit()
    #
    # all_attendances = StudentPayments.query.all()
    # print(len(all_attendances))

    # deleted_student_payments_list = response.json()['deleted_student_payments_list']
    # for payment in deleted_student_payments_list:
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == payment['account_period_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == payment['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == payment['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == payment['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == payment['location_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == payment['payment_type_id']).first()
    #     student_id = Students.query.filter(Students.old_id == payment['student_id']).first()
    #     if calendar_day:
    #         payment_add = DeletedStudentPayments.query.filter(DeletedStudentPayments.student_id == student_id.id,
    #                                                           DeletedStudentPayments.location_id == location_id.id,
    #                                                           DeletedStudentPayments.calendar_day == calendar_day.id,
    #                                                           DeletedStudentPayments.calendar_month == calendar_month.id,
    #                                                           DeletedStudentPayments.account_period_id == account_period_id.id,
    #                                                           DeletedStudentPayments.payment_type_id == payment_type_id.id,
    #                                                           DeletedStudentPayments.calendar_year == calendar_year.id).first()
    #         if not payment_add:
    #             payment_add = DeletedStudentPayments(student_id=student_id.id, payment_sum=payment['payment_sum'],
    #                                                  location_id=location_id.id, payment=payment['payment'],
    #                                                  calendar_day=calendar_day.id, reason=payment['reason'],
    #                                                  calendar_month=calendar_month.id,
    #                                                  account_period_id=account_period_id.id,
    #                                                  payment_type_id=payment_type_id.id,
    #                                                  calendar_year=calendar_year.id)
    #             db.session.add(payment_add)
    #             db.session.commit()
    #
    # all_attendances = DeletedStudentPayments.query.all()
    # print(len(all_attendances))

    # student_charity_list = response.json()['student_charity_list']
    # for payment in student_charity_list:
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == payment['account_period_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == payment['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == payment['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == payment['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == payment['location_id']).first()
    #     student_id = Students.query.filter(Students.old_id == payment['student_id']).first()
    #     group_id = Groups.query.filter(Groups.old_id == payment['group_id']).first()
    #     if group_id:
    #         charity_add = StudentCharity.query.filter(StudentCharity.student_id == student_id.id,
    #                                                   StudentCharity.calendar_day == calendar_day.id,
    #                                                   StudentCharity.calendar_month == calendar_month.id,
    #                                                   StudentCharity.account_period_id == account_period_id.id,
    #                                                   StudentCharity.location_id == location_id.id,
    #                                                   StudentCharity.group_id == group_id.id,
    #                                                   StudentCharity.calendar_year == calendar_year.id,
    #                                                   StudentCharity.old_id == payment['old_id']).first()
    #         if not charity_add:
    #             charity_add = StudentCharity(student_id=student_id.id,
    #                                          calendar_day=calendar_day.id,
    #                                          calendar_month=calendar_month.id,
    #                                          account_period_id=account_period_id.id,
    #                                          location_id=location_id.id, old_id=payment['old_id'],
    #                                          group_id=group_id.id, discount=payment['discount'],
    #                                          calendar_year=calendar_year.id)
    #             db.session.add(charity_add)
    #             db.session.commit()
    # all_attendances = StudentCharity.query.all()
    # print(len(all_attendances))

    # student_history_groups_list = response.json()['student_history_groups_list']
    # for student in student_history_groups_list:
    #     student_id = Students.query.filter(Students.old_id == student['student_id']).first()
    #     teacher_id = Teachers.query.filter(Teachers.old_id == student['teacher_id']).first()
    #     group_id = Groups.query.filter(Groups.old_id == student['group_id']).first()
    #     if group_id and teacher_id:
    #         student_add = StudentHistoryGroups.query.filter(StudentHistoryGroups.student_id == student_id.id,
    #                                                         StudentHistoryGroups.group_id == group_id.id,
    #                                                         StudentHistoryGroups.teacher_id == teacher_id.id,
    #                                                         StudentHistoryGroups.old_id == student['old_id']).first()
    #         if not student_add:
    #             student_add = StudentHistoryGroups(student_id=student_id.id, left_day=student['left_day'],
    #                                                group_id=group_id.id, joined_day=student['joined_day'],
    #                                                teacher_id=teacher_id.id, reason=student['reason'],
    #                                                old_id=student['old_id'])
    #             db.session.add(student_add)
    #             db.session.commit()
    # all_attendances = StudentHistoryGroups.query.all()
    # print(len(all_attendances))

    # student_excuses_list = response.json()['student_excuses_list']
    # for student in student_excuses_list:
    #     student_id = Students.query.filter(Students.old_id == student['student_id']).first()
    #     excuse_add = StudentExcuses.query.filter(StudentExcuses.student_id == student_id.id,
    #                                              StudentExcuses.to_date == student['to_date'],
    #                                              StudentExcuses.old_id == student['old_id']).first()
    #     if not excuse_add:
    #         excuse_add = StudentExcuses(student_id=student_id.id, old_id=student['old_id'],
    #                                     to_date=student['to_date'], reason=student['reason'])
    #         db.session.add(excuse_add)
    #         db.session.commit()
    #
    # all_attendances = StudentExcuses.query.all()
    # print(len(all_attendances))
    #
    # contract_students_list = response.json()['contract_students_list']
    # for contract in contract_students_list:
    #     student_id = Students.query.filter(Students.old_id == contract['student_id']).first()
    #     add_contract = Contract_Students.query.filter(Contract_Students.student_id == student_id.id).first()
    #     if not add_contract:
    #         add_contract = Contract_Students(student_id=student_id.id,
    #                                          created_date=contract['created_date'],
    #                                          expire_date=contract['expire_date'],
    #                                          father_name=contract['father_name'], given_place=contract['given_place'],
    #                                          given_time=contract['given_time'],
    #                                          passport_series=contract['passport_series'], place=contract['place'])
    #         db.session.add(add_contract)
    #         db.session.commit()
    # all_attendances = Contract_Students.query.all()
    # print(len(all_attendances))
    #
    # deleted_students_list = response.json()['deleted_students_list']
    # for student in deleted_students_list:
    #     student_id = Students.query.filter(Students.old_id == student['student_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == student['calendar_day']).first()
    #     teacher_id = Teachers.query.filter(Teachers.old_id == student['teacher_id']).first()
    #     group_id = Groups.query.filter(Groups.old_id == student['group_id']).first()
    #     if teacher_id and group_id and calendar_day:
    #         student_add = DeletedStudents.query.filter(DeletedStudents.student_id == student_id.id,
    #                                                    DeletedStudents.calendar_day == calendar_day.id,
    #                                                    DeletedStudents.teacher_id == teacher_id.id,
    #                                                    DeletedStudents.group_id == group_id.id).first()
    #         if not student_add:
    #             student_add = DeletedStudents(student_id=student_id.id, reason=student['reason'],
    #                                           calendar_day=calendar_day.id,
    #                                           teacher_id=teacher_id.id,
    #                                           group_id=group_id.id)
    #             db.session.add(student_add)
    #             db.session.commit()
    #
    # registered_deleted = response.json()['registered_deleted_list']
    # for student in registered_deleted:
    #     student_id = Students.query.filter(Students.old_id == student['student_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == student['calendar_day']).first()
    #     student_add = RegisterDeletedStudents.query.filter(RegisterDeletedStudents.student_id == student_id.id,
    #                                                        RegisterDeletedStudents.calendar_day == calendar_day.id).first()
    #     if not student_add:
    #         student_add = RegisterDeletedStudents(student_id=student_id.id, reason=student['reason'],
    #                                               calendar_day=calendar_day.id)
    #         db.session.add(student_add)
    #         db.session.commit()

    # book_payments_list = response.json()['book_payments_list']
    # for payment in book_payments_list:
    #     student_id = Students.query.filter(Students.old_id == payment['student_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == payment['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == payment['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == payment['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == payment['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == payment['account_period_id']).first()
    #     payment_add = BookPayments.query.filter(BookPayments.student_id == student_id.id,
    #                                             BookPayments.calendar_day == calendar_day.id,
    #                                             BookPayments.calendar_year == calendar_year.id,
    #                                             BookPayments.calendar_month == calendar_month.id,
    #                                             BookPayments.account_period_id == account_period_id.id,
    #                                             BookPayments.location_id == location_id.id).first()
    #     if not payment_add:
    #         payment_add = BookPayments(student_id=student_id.id, payment_sum=payment['payment_sum'],
    #                                    calendar_day=calendar_day.id,
    #                                    calendar_year=calendar_year.id,
    #                                    calendar_month=calendar_month.id,
    #                                    account_period_id=account_period_id.id,
    #                                    location_id=location_id.id)
    #         db.session.add(payment_add)
    #         db.session.commit()
    # deleted_book_payments_list = response.json()['deleted_book_payments_list']
    # for payment in deleted_book_payments_list:
    #     student_id = Students.query.filter(Students.old_id == payment['student_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == payment['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == payment['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == payment['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == payment['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == payment['account_period_id']).first()
    #     if account_period_id:
    #         payment_add = DeletedBookPayments.query.filter(DeletedBookPayments.student_id == student_id.id,
    #                                                        DeletedBookPayments.calendar_day == calendar_day.id,
    #                                                        DeletedBookPayments.calendar_year == calendar_year.id,
    #                                                        DeletedBookPayments.calendar_month == calendar_month.id,
    #                                                        DeletedBookPayments.account_period_id == account_period_id.id,
    #                                                        DeletedBookPayments.location_id == location_id.id).first()
    #         if not payment_add:
    #             payment_add = DeletedBookPayments(student_id=student_id.id, payment_sum=payment['payment_sum'],
    #                                               calendar_day=calendar_day.id,
    #                                               calendar_year=calendar_year.id,
    #                                               calendar_month=calendar_month.id,
    #                                               account_period_id=account_period_id.id,
    #                                               location_id=location_id.id)
    #             db.session.add(payment_add)
    #             db.session.commit()

    # teacher_salaries_list = response.json()['teacher_salaries_list']
    # for salary in teacher_salaries_list:
    #     teacher_id = Teachers.query.filter(Teachers.old_id == salary['teacher_id']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #     if teacher_id:
    #         salary_add = TeacherSalary.query.filter(TeacherSalary.teacher_id == teacher_id.id,
    #                                                 TeacherSalary.calendar_month == calendar_month.id,
    #                                                 TeacherSalary.calendar_year == calendar_year.id,
    #                                                 TeacherSalary.location_id == location_id.id).first()
    #         if not salary_add:
    #             salary_add = TeacherSalary(teacher_id=teacher_id.id, total_salary=salary['total_salary'],
    #                                        calendar_month=calendar_month.id, remaining_salary=salary['remaining_salary'],
    #                                        calendar_year=calendar_year.id, status=salary['status'],
    #                                        location_id=location_id.id, taken_money=salary['taken_money'],
    #                                        old_id=salary['old_id'])
    #             db.session.add(salary_add)
    #             db.session.commit()

    # teachers_list = response.json()['teachers_list']
    # for teacher in teachers_list:
    #     user = Users.query.filter(Users.old_id == teacher['user_id']).first()
    #     teacher_get = Teachers.query.filter(Teachers.old_id == teacher['old_id']).first()
    #     if not teacher_get:
    #         teacher_add = Teachers(user_id=user.id, old_id=teacher['old_id'])
    #         db.session.add(teacher_add)
    #         db.session.commit()
    #         print(False)
    # deleted_teachers_list = response.json()['deleted_teachers_list']
    # for teacher in deleted_teachers_list:
    #     teacher_id = Teachers.query.filter(Teachers.old_id == teacher['teacher_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == teacher['calendar_day']).first()
    #     add_teacher = DeletedTeachers.query.filter(DeletedTeachers.calendar_day == calendar_day.id,
    #                                                DeletedTeachers.teacher_id == teacher_id.id).first()
    #     if not add_teacher:
    #         add_teacher = DeletedTeachers(calendar_day=calendar_day.id, reason=teacher['reason'],
    #                                       teacher_id=teacher_id.id)
    #         db.session.add(add_teacher)
    #         db.session.commit()
    # teacher_salaries_day_list = response.json()['teacher_salaries_day_list']
    # for salary in teacher_salaries_day_list:
    #     teacher_id = Teachers.query.filter(Teachers.old_id == salary['teacher_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == salary['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #     salary_location_id = TeacherSalary.query.filter(TeacherSalary.old_id == salary['salary_location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == salary['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == salary['payment_type_id']).first()
    #     by_who = Users.query.filter(Users.old_id == salary['by_who']).first()
    #     user_id = None
    #     if by_who:
    #         user_id = by_who.id
    #
    #     salary_location_id_2 = None
    #     if salary_location_id:
    #         salary_location_id_2 = salary_location_id.id
    #     salary_add = TeacherSalaries.query.filter(TeacherSalaries.teacher_id == teacher_id.id,
    #                                               TeacherSalaries.calendar_day == calendar_day.id,
    #                                               TeacherSalaries.calendar_month == calendar_month.id,
    #                                               TeacherSalaries.calendar_year == calendar_year.id,
    #                                               TeacherSalaries.location_id == location_id.id,
    #                                               TeacherSalaries.salary_location_id == salary_location_id_2,
    #                                               TeacherSalaries.account_period_id == account_period_id.id,
    #                                               TeacherSalaries.payment_type_id == payment_type_id.id,
    #                                               TeacherSalaries.old_id == salary['old_id']).first()
    #     if not salary_add:
    #         salary_add = TeacherSalaries(teacher_id=teacher_id.id, by_who=user_id,
    #                                      calendar_day=calendar_day.id, reason=salary['reason'],
    #                                      calendar_month=calendar_month.id, payment_sum=salary['payment_sum'],
    #                                      calendar_year=calendar_year.id,
    #                                      location_id=location_id.id, old_id=salary['old_id'],
    #                                      salary_location_id=salary_location_id_2,
    #                                      account_period_id=account_period_id.id,
    #                                      payment_type_id=payment_type_id.id)
    #         db.session.add(salary_add)
    #         db.session.commit()
    # teacher_salaries = db.session.query(TeacherSalaries).join(TeacherSalaries.day).options(
    #     contains_eager(TeacherSalaries.day)).filter(
    #     CalendarDay.date < datetime.strptime("2023-04-02", "%Y-%m-%d")).order_by(TeacherSalaries.id).all()
    #
    # print(len(teacher_salaries))
    # deleted_teacher_salaries_day_list = response.json()['deleted_teacher_salaries_day_list']
    # for salary in deleted_teacher_salaries_day_list:
    #     teacher_id = Teachers.query.filter(Teachers.old_id == salary['teacher_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == salary['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #     salary_location_id = TeacherSalary.query.filter(TeacherSalary.old_id == salary['salary_location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == salary['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == salary['payment_type_id']).first()
    #     group_id = Groups.query.filter(Groups.old_id == salary['group_id']).first()
    #     gr_id = None
    #     if group_id:
    #         gr_id = group_id.id
    #     if salary_location_id:
    #         salary_add = DeletedTeacherSalaries.query.filter(DeletedTeacherSalaries.teacher_id == teacher_id.id,
    #                                                          DeletedTeacherSalaries.calendar_day == calendar_day.id,
    #                                                          DeletedTeacherSalaries.calendar_month == calendar_month.id,
    #                                                          DeletedTeacherSalaries.calendar_year == calendar_year.id,
    #                                                          DeletedTeacherSalaries.location_id == location_id.id,
    #                                                          DeletedTeacherSalaries.salary_location_id == salary_location_id.id,
    #                                                          DeletedTeacherSalaries.account_period_id == account_period_id.id,
    #                                                          DeletedTeacherSalaries.payment_type_id == payment_type_id.id).first()
    #         if not salary_add:
    #             salary_add = DeletedTeacherSalaries(teacher_id=teacher_id.id,
    #                                                 calendar_day=calendar_day.id, reason=salary['reason'],
    #                                                 calendar_month=calendar_month.id, payment_sum=salary['payment_sum'],
    #                                                 calendar_year=calendar_year.id,
    #                                                 reason_deleted=salary['reason_deleted'],
    #                                                 location_id=location_id.id, deleted_date=salary['deleted_date'],
    #                                                 salary_location_id=salary_location_id.id, group_id=gr_id,
    #                                                 account_period_id=account_period_id.id,
    #                                                 payment_type_id=payment_type_id.id)
    #             db.session.add(salary_add)
    #             db.session.commit()
    # staff_salaries_list = response.json()['staff_salaries_list']
    # for salary in staff_salaries_list:
    #     staff_id = Staff.query.filter(Staff.old_id == salary['staff_id']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #
    #     salary_add = StaffSalary.query.filter(StaffSalary.staff_id == staff_id.id,
    #                                           StaffSalary.calendar_month == calendar_month.id,
    #                                           StaffSalary.calendar_year == calendar_year.id,
    #                                           StaffSalary.location_id == location_id.id).first()
    #     if not salary_add:
    #         salary_add = StaffSalary(staff_id=staff_id.id, total_salary=salary['total_salary'],
    #                                  calendar_month=calendar_month.id,
    #                                  remaining_salary=salary['remaining_salary'],
    #                                  calendar_year=calendar_year.id, status=salary['status'],
    #                                  location_id=location_id.id, taken_money=salary['taken_money'],
    #                                  old_id=salary['old_id'])
    #         db.session.add(salary_add)
    #         db.session.commit()

    # staff_salaries_day_list = response.json()['staff_salaries_day_list']
    # for salary in staff_salaries_day_list:
    #     staff_id = Staff.query.filter(Staff.old_id == salary['staff_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == salary['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #     salary_id = StaffSalary.query.filter(StaffSalary.old_id == salary['salary_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == salary['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == salary['payment_type_id']).first()
    #     by_who = Users.query.filter(Users.old_id == salary['by_who']).first()
    #     profession_id = Professions.query.filter(Professions.old_id == salary['profession_id']).first()
    #     user_id = None
    #     if by_who:
    #         user_id = by_who.id
    #     if salary_id:
    #         salary_add = StaffSalaries.query.filter(StaffSalaries.staff_id == staff_id.id,
    #                                                 StaffSalaries.calendar_day == calendar_day.id,
    #                                                 StaffSalaries.calendar_month == calendar_month.id,
    #                                                 StaffSalaries.calendar_year == calendar_year.id,
    #                                                 StaffSalaries.location_id == location_id.id,
    #                                                 StaffSalaries.salary_id == salary_id.id,
    #                                                 StaffSalaries.account_period_id == account_period_id.id,
    #                                                 StaffSalaries.payment_type_id == payment_type_id.id,
    #                                                 StaffSalaries.old_id == salary['old_id']).first()
    #         if not salary_add:
    #             salary_add = StaffSalaries(staff_id=staff_id.id, by_who=user_id,
    #                                        calendar_day=calendar_day.id, reason=salary['reason'],
    #                                        calendar_month=calendar_month.id, payment_sum=salary['payment_sum'],
    #                                        calendar_year=calendar_year.id, profession_id=profession_id.id,
    #                                        location_id=location_id.id, old_id=salary['old_id'],
    #                                        salary_id=salary_id.id,
    #                                        account_period_id=account_period_id.id,
    #                                        payment_type_id=payment_type_id.id)
    #             db.session.add(salary_add)
    #             db.session.commit()
    # overheads = StaffSalaries.query.all()
    # print(len(overheads))
    # deleted_staff_salaries_day_list = response.json()['deleted_staff_salaries_day_list']
    # for salary in deleted_staff_salaries_day_list:
    #     staff_id = Staff.query.filter(Staff.old_id == salary['staff_id']).first()
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == salary['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == salary['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == salary['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == salary['location_id']).first()
    #     salary_id = StaffSalary.query.filter(StaffSalary.old_id == salary['salary_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == salary['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == salary['payment_type_id']).first()
    #     profession_id = Professions.query.filter(Professions.old_id == salary['profession_id']).first()
    #     salary_add = DeletedStaffSalaries.query.filter(DeletedStaffSalaries.staff_id == staff_id.id,
    #                                                    DeletedStaffSalaries.calendar_day == calendar_day.id,
    #                                                    DeletedStaffSalaries.calendar_month == calendar_month.id,
    #                                                    DeletedStaffSalaries.calendar_year == calendar_year.id,
    #                                                    DeletedStaffSalaries.location_id == location_id.id,
    #                                                    DeletedStaffSalaries.salary_id == salary_id.id,
    #                                                    DeletedStaffSalaries.account_period_id == account_period_id.id,
    #                                                    DeletedStaffSalaries.payment_type_id == payment_type_id.id).first()
    #     if not salary_add:
    #         salary_add = DeletedStaffSalaries(staff_id=staff_id.id,
    #                                           calendar_day=calendar_day.id, reason=salary['reason'],
    #                                           calendar_month=calendar_month.id, payment_sum=salary['payment_sum'],
    #                                           calendar_year=calendar_year.id, profession_id=profession_id.id,
    #                                           location_id=location_id.id, deleted_date=salary['deleted_date'],
    #                                           salary_id=salary_id.id, reason_deleted=salary['reason_deleted'],
    #                                           account_period_id=account_period_id.id,
    #                                           payment_type_id=payment_type_id.id)
    #         db.session.add(salary_add)
    #         db.session.commit()

    # group_room_weeks_list = response.json()['group_room_weeks_list']
    # for time_table in group_room_weeks_list:
    #     group_id = Groups.query.filter(Groups.old_id == time_table['group_id']).first()
    #     location_id = Locations.query.filter(Locations.old_id == time_table['location_id']).first()
    #     room_id = Rooms.query.filter(Rooms.old_id == time_table['room_id']).first()
    #     week_id = Week.query.filter(Week.old_id == time_table['week_id']).first()
    #     if group_id:
    #         table = Group_Room_Week.query.filter(Group_Room_Week.room_id == room_id.id,
    #                                              Group_Room_Week.group_id == group_id.id,
    #                                              Group_Room_Week.location_id == location_id.id,
    #                                              Group_Room_Week.start_time == time_table['start_time'],
    #                                              Group_Room_Week.end_time == time_table['end_time'],
    #                                              Group_Room_Week.week_id == week_id.id).first()
    #         if not table:
    #             table = Group_Room_Week(room_id=room_id.id,
    #                                     group_id=group_id.id,
    #                                     location_id=location_id.id,
    #                                     start_time=time_table['start_time'],
    #                                     end_time=time_table['end_time'],
    #                                     week_id=week_id.id)
    #             db.session.add(table)
    #             db.session.commit()
    #         for student in time_table['students']:
    #             student_get = Students.query.filter(Students.old_id == student).first()
    #             if table not in student_get.time_table:
    #                 student_get.time_table.append(table)
    #                 db.session.commit()
    #         for teacher in time_table['teachers']:
    #             teacher_get = Teachers.query.filter(Teachers.old_id == teacher).first()
    #             if table not in teacher_get.time_table:
    #                 teacher_get.time_table.append(table)
    #                 db.session.commit()
    #
    # capital_expenditures_list = response.json()['capital_expenditures_list']
    # for capital in capital_expenditures_list:
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == capital['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == capital['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == capital['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == capital['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == capital['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == capital['payment_type_id']).first()
    #     by_who = Users.query.filter(Users.old_id == capital['by_who']).first()
    #     user_id = None
    #     if by_who:
    #         user_id = by_who.id
    #     capital_add = CapitalExpenditure.query.filter(CapitalExpenditure.location_id == location_id.id,
    #                                                   CapitalExpenditure.account_period_id == account_period_id.id,
    #                                                   CapitalExpenditure.calendar_day == calendar_day.id,
    #                                                   CapitalExpenditure.calendar_month == calendar_month.id,
    #                                                   CapitalExpenditure.calendar_year == calendar_year.id,
    #                                                   CapitalExpenditure.payment_type_id == payment_type_id.id,
    #                                                   CapitalExpenditure.old_id == capital['id']).first()
    #     if not capital_add:
    #         capital_add = CapitalExpenditure(location_id=location_id.id, item_sum=capital['item_sum'],
    #                                          account_period_id=account_period_id.id, by_who=user_id,
    #                                          calendar_day=calendar_day.id, item_name=capital['item_name'],
    #                                          calendar_month=calendar_month.id, old_id=capital['id'],
    #                                          calendar_year=calendar_year.id,
    #                                          payment_type_id=payment_type_id.id)
    #         db.session.add(capital_add)
    #         db.session.commit()
    # overheads = CapitalExpenditure.query.all()
    # print(len(overheads))
    #
    # deleted_capital_expenditures_list = response.json()['deleted_capital_expenditures_list']
    # for capital in deleted_capital_expenditures_list:
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == capital['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == capital['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == capital['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == capital['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == capital['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == capital['payment_type_id']).first()
    #
    #     capital_add = DeletedCapitalExpenditure.query.filter(DeletedCapitalExpenditure.location_id == location_id.id,
    #                                                          DeletedCapitalExpenditure.account_period_id == account_period_id.id,
    #                                                          DeletedCapitalExpenditure.calendar_day == calendar_day.id,
    #                                                          DeletedCapitalExpenditure.calendar_month == calendar_month.id,
    #                                                          DeletedCapitalExpenditure.calendar_year == calendar_year.id,
    #                                                          DeletedCapitalExpenditure.payment_type_id == payment_type_id.id).first()
    #     if not capital_add:
    #         capital_add = DeletedCapitalExpenditure(location_id=location_id.id, item_sum=capital['item_sum'],
    #                                                 account_period_id=account_period_id.id,
    #                                                 deleted_date=capital['deleted_date'],
    #                                                 calendar_day=calendar_day.id, item_name=capital['item_name'],
    #                                                 calendar_month=calendar_month.id,
    #                                                 calendar_year=calendar_year.id,
    #                                                 payment_type_id=payment_type_id.id)
    #         db.session.add(capital_add)
    #         db.session.commit()
    #
    # overheads_list = response.json()['overheads_list']
    # for capital in overheads_list:
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == capital['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == capital['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == capital['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == capital['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == capital['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == capital['payment_type_id']).first()
    #     by_who = Users.query.filter(Users.old_id == capital['by_who']).first()
    #     user_id = None
    #     if by_who:
    #         user_id = by_who.id
    #     if calendar_day:
    #         capital_add = Overhead.query.filter(Overhead.location_id == location_id.id,
    #                                             Overhead.old_id == capital['id'],
    #                                             Overhead.account_period_id == account_period_id.id,
    #                                             Overhead.calendar_day == calendar_day.id,
    #                                             Overhead.calendar_month == calendar_month.id,
    #                                             Overhead.calendar_year == calendar_year.id,
    #                                             Overhead.payment_type_id == payment_type_id.id).first()
    #         if not capital_add:
    #             capital_add = Overhead(location_id=location_id.id, item_sum=capital['item_sum'],
    #                                    account_period_id=account_period_id.id, by_who=user_id,
    #                                    calendar_day=calendar_day.id, item_name=capital['item_name'],
    #                                    calendar_month=calendar_month.id, old_id=capital['id'],
    #                                    calendar_year=calendar_year.id,
    #                                    payment_type_id=payment_type_id.id)
    #             db.session.add(capital_add)
    #             db.session.commit()
    # overheads = Overhead.query.all()
    # print(len(overheads))
    #
    # deleted_overheads_list = response.json()['deleted_overheads_list']
    # for capital in deleted_overheads_list:
    #     calendar_day = CalendarDay.query.filter(CalendarDay.old_id == capital['calendar_day']).first()
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == capital['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == capital['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == capital['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == capital['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == capital['payment_type_id']).first()
    #
    #     capital_add = DeletedOverhead.query.filter(DeletedOverhead.location_id == location_id.id,
    #                                                DeletedOverhead.account_period_id == account_period_id.id,
    #                                                DeletedOverhead.calendar_day == calendar_day.id,
    #                                                DeletedOverhead.calendar_month == calendar_month.id,
    #                                                DeletedOverhead.calendar_year == calendar_year.id,
    #                                                DeletedOverhead.payment_type_id == payment_type_id.id).first()
    #     if not capital_add:
    #         capital_add = DeletedOverhead(location_id=location_id.id, item_sum=capital['item_sum'],
    #                                       account_period_id=account_period_id.id,
    #                                       deleted_date=capital['deleted_date'],
    #                                       calendar_day=calendar_day.id, item_name=capital['item_name'],
    #                                       calendar_month=calendar_month.id,
    #                                       calendar_year=calendar_year.id,
    #                                       payment_type_id=payment_type_id.id)
    #         db.session.add(capital_add)
    #         db.session.commit()
    # accounting_infos_list = response.json()['accounting_infos_list']
    # for account in accounting_infos_list:
    #     calendar_month = CalendarMonth.query.filter(CalendarMonth.old_id == account['calendar_month']).first()
    #     calendar_year = CalendarYear.query.filter(CalendarYear.id == account['calendar_year']).first()
    #     location_id = Locations.query.filter(Locations.old_id == account['location_id']).first()
    #     account_period_id = AccountingPeriod.query.filter(
    #         AccountingPeriod.old_id == account['account_period_id']).first()
    #     payment_type_id = PaymentTypes.query.filter(PaymentTypes.old_id == account['payment_type_id']).first()
    #     account_add = AccountingInfo.query.filter(AccountingInfo.account_period_id == account_period_id.id,
    #                                               AccountingInfo.payment_type_id == payment_type_id.id,
    #                                               AccountingInfo.calendar_year == calendar_year.id,
    #                                               AccountingInfo.location_id == location_id.id,
    #                                               AccountingInfo.calendar_month == calendar_month.id).first()
    #     if not account_add:
    #         account_add = AccountingInfo(account_period_id=account_period_id.id, all_payments=account['all_payments'],
    #                                      payment_type_id=payment_type_id.id, all_overhead=account['all_overhead'],
    #                                      all_staff_salaries=account['all_staff_salaries'], old_cash=account['old_cash'],
    #                                      all_teacher_salaries=account['all_teacher_salaries'],
    #                                      calendar_year=calendar_year.id, all_capital=account['all_capital'],
    #                                      location_id=location_id.id, current_cash=account['current_cash'],
    #                                      calendar_month=calendar_month.id, all_discount=account['all_discount'])
    #     db.session.add(account_add)
    #     db.session.commit()
    # comments = response.json()['comments_list']
    # for comment in comments:
    #     user = Users.query.filter(Users.old_id == comment['user_id']).first()
    #     add_comment = Comments(comment=comment['comment'], user_id=user.id, old_id=comment['id'])
    #     db.session.add(add_comment)
    #     db.session.commit()
    #
    # commentlikes_list = response.json()['commentlikes_list']
    # for comment in commentlikes_list:
    #     comment_get = Comments.query.filter(Comments.old_id == comment['comment_id']).first()
    #     user_id = Users.query.filter(Users.old_id == comment['user_id']).first()
    #     like_add = CommentLikes.query.filter(CommentLikes.comment_id == comment_get.id,
    #                                          CommentLikes.user_id == user_id.id).first()
    #     if not like_add:
    #         like_add = CommentLikes(comment_id=comment_get.id, user_id=user_id.id)
    #         db.session.add(like_add)
    #         db.session.commit()
    # gallery_list = response.json()['gallery_list']
    # for gallery in gallery_list:
    #     gallery_add = Gallery(img=gallery['img'])
    #     db.session.add(gallery_add)
    #     db.session.commit()
    return "True"
