import pprint

from app import app, api, or_, db, contains_eager, extract, jsonify, request, desc
from backend.models.models import Groups, CalendarDay, Students, AttendanceDays, SubjectLevels, \
    AttendanceHistoryStudent, Group_Room_Week, Attendance, CalendarMonth, Week, Rooms, Teachers, Roles, \
    CertificateLinks, GroupTest
from flask_jwt_extended import jwt_required
from backend.student.class_model import Student_Functions
from backend.functions.filters import old_current_dates, update_lesson_plan
from backend.group.class_model import Group_Functions
from backend.functions.utils import find_calendar_date, get_json_field, iterate_models
from datetime import datetime

import os

from backend.account.models import StudentCharity


@app.route(f'{api}/group_statistics/<int:group_id>', methods=['POST', 'GET'])
@jwt_required()
def group_statistics(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    group = Groups.query.filter(Groups.id == group_id).first()
    student_ids = []
    for student in group.student:
        student_ids.append(student.id)
    attendance = Attendance.query.filter(Attendance.calendar_year == calendar_year.id,
                                         Attendance.calendar_month == calendar_month.id,
                                         Attendance.group_id == group_id).first()
    discount_summ = 0
    percentage = 0
    attendance_percentage = 0
    if attendance:
        attendance_days = AttendanceDays.query.filter(AttendanceDays.attendance_id == attendance.id).all()
        for attendance_day in attendance_days:
            discount_summ += attendance_day.discount_per_day

    students_charities = db.session.query(Students).join(Students.charity).options(
        contains_eager(Students.charity)).filter(
        StudentCharity.group_id == group.id, StudentCharity.student_id.in_(student_ids),
        StudentCharity.calendar_year == calendar_year.id, StudentCharity.calendar_month == calendar_month.id).count()
    if students_charities:
        percentage = round((students_charities / len(group.student)) * 100)
    students_attendanced_count = db.session.query(Students).join(Students.attendance).options(
        contains_eager(Students.attendance)).filter(
        Attendance.group_id == group.id, Attendance.student_id.in_(student_ids),
        Attendance.calendar_year == calendar_year.id, Attendance.calendar_month == calendar_month.id).count()
    if students_attendanced_count:
        attendance_percentage = round((students_attendanced_count / len(group.student)) * 100)
    info = {
        "discount_summ": discount_summ,
        "discount_percentage": percentage,
        "attendance_percentage": attendance_percentage
    }
    return jsonify({
        "info": info
    })


@app.route(f'{api}/groups/<location_id>', methods=['POST', 'GET'])
@jwt_required()
def groups(location_id):
    groups = Groups.query.filter(Groups.location_id == location_id,
                                 Groups.teacher_id != None).filter(
        or_(Groups.deleted == None, Groups.deleted == False)).order_by('id').all()
    list_group = [{
        "id": gr.id,
        "name": gr.name.title(),
        "teacherID": gr.teacher_id,
        "subjects": gr.subject.name.title(),
        "payment": gr.price,
        "typeOfCourse": gr.course_type.name,
        "studentsLength": len(gr.student),
        "status": "True" if gr.status else "False",
        "teacherName": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.name.title(),
        "teacherSurname": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.surname.title(),
    } for gr in groups]

    return jsonify({
        "groups": list_group
    })


@app.route(f'{api}/my_groups/<int:user_id>', methods=['POST', 'GET'])
@jwt_required()
def my_groups(user_id):
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    student = Students.query.filter(Students.user_id == user_id).first()
    if teacher:
        groups = Groups.query.filter(Groups.teacher_id == teacher.id, Groups.deleted != True,
                                     Groups.status == True).order_by(Groups.id).all()
    else:
        group_id = []
        for gr in student.group:
            group_id.append(gr.id)
        groups = Groups.query.filter(Groups.deleted != True, Groups.status == True,
                                     Groups.id.in_([group_id for group_id in group_id])).order_by(Groups.id).all()
    list_group = [{
        "id": gr.id,
        "name": gr.name.title(),
        "teacherID": gr.teacher_id,
        "subjects": gr.subject.name.title(),
        "payment": gr.price,
        "typeOfCourse": gr.course_type.name,
        "studentsLength": len(gr.student),
        "status": "True" if gr.status else "False",
        "teacherName": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.name.title(),
        "teacherSurname": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.surname.title(),
    } for gr in groups]

    return jsonify({
        "groups": list_group
    })


@app.route(f'{api}/groups_by_id/<int:group_id>', methods=['POST', 'GET'])
@jwt_required()
def groups_by_id(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()

    groups = Groups.query.filter(Groups.location_id == group.location_id, Groups.status == True,
                                 Groups.id != group.id, Groups.subject_id == group.subject_id).filter(
        or_(Groups.deleted == False, Groups.deleted == None)).order_by('id').all()
    list_group = []
    list_group.append(
        {
            "id": gr.id,
            "name": gr.name.title(),
            "teacherID": gr.teacher_id,
            "subjects": gr.subject.name.title(),
            "payment": gr.price,
            "typeOfCourse": gr.course_type.name,
            "studentsLength": len(gr.student),
            "status": "True" if gr.status else "False",
            "teacherName": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.name.title(),
            "teacherSurname": Teachers.query.filter(Teachers.id == gr.teacher_id).first().user.surname.title(),
        } for gr in groups
    )
    return jsonify({
        "groups": list_group
    })


@app.route(f'{api}/group_profile/<int:group_id>')
@jwt_required()
def group_profile(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    group = Groups.query.filter_by(id=group_id).first()
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).order_by(Students.id).all()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    data = {}
    levels = SubjectLevels.query.filter(SubjectLevels.subject_id == group.subject_id).filter(
        or_(SubjectLevels.disabled == False, SubjectLevels.disabled == None)).order_by(SubjectLevels.id).all()
    level = ''
    update_lesson_plan(group_id)
    if group.level and group.level.name:
        level = group.level.name
    data["information"] = {
        "groupName": {
            "name": "Guruh nomi",
            "value": group.name.title()
        },
        "eduLang": {
            "name": "O'qitish tili",
            "value": group.language.name
        },
        "studentsLength": {
            "name": "Studentlar soni",
            "value": len(group.student)
        },
        "groupPrice": {
            "name": "Guruh narxi",
            "value": group.price
        },
        "groupCourseType": {
            "name": "Kurs turi",
            "value": group.course_type.name
        },
        "groupLevel": {
            "name": "Level",
            "value": level
        },
        "teacherSalary": {
            "name": "O'qituvchi ulushi",
            "value": group.teacher_salary
        },
        "teacherName": {
            "name": "O'qituvchi ismi",
            "value": teacher.user.name.title()
        },
        "teacherSurname": {
            "name": "O'qituvchi familyasi",
            "value": teacher.user.surname.title()
        },
    }

    data['students'] = [{
        "id": st.user.id,
        "img": None,
        "name": st.user.name.title(),
        "surname": st.user.surname.title(),
        "money": st.user.balance,
        "moneyType": ["green", "yellow", "red", "navy", "black"][st.debtor] if st.debtor else 0,
        "comment": st.user.comment,
        "reg_date": st.user.day.date.strftime("%Y-%m-%d"),
        "phone": st.user.phone[0].phone,
        "username": st.user.username,
        "age": st.user.age,
        "photo_profile": st.user.photo_profile,
        "role": Roles.query.filter(Roles.id == st.user.role_id).first().role
    } for st in students]
    gr_functions = Group_Functions(group_id=group_id)
    gr_functions.update_list_balance()
    group_time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).order_by(
        Group_Room_Week.id).all()
    time_table_list = [{
        "time_id": time_get.id,
        "day": time_get.week.name,
        "room": time_get.room.name,
        "start_time": time_get.start_time.strftime("%H:%M"),
        "end_time": time_get.end_time.strftime("%H:%M")
    } for time_get in group_time_table if time_get.week]
    is_time = False
    links = []
    link = ''

    if group.time_table:
        is_time = True
        link = {
            "type": "link",
            "link": "addGroup",
            "title": "Add to group",
            "iconClazz": "fa-user-plus",

        }
    links.append(link)
    links.append(
        {
            "type": "btn",
            "name": "deleteGroup",
            "title": "Gruppani o'chirish",
            "iconClazz": "fa-times",
        }
    )
    certificate_links = CertificateLinks.query.filter(CertificateLinks.group_id == group.id).all()
    for link in certificate_links:
        if os.path.exists(link.link):
            os.remove(link.link)
        db.session.delete(link)
        db.session.commit()
    Groups.query.filter(Groups.id == group.id).update({
        "certificate_url": ""
    })
    db.session.commit()
    info_level = {}
    if group.level:
        info_level = {
            "id": group.level.id,
            "name": group.level.name
        }
    subject_levels = SubjectLevels.query.filter(SubjectLevels.subject_id == group.subject_id).order_by(
        SubjectLevels.id).all()

    group_tests = GroupTest.query.filter(GroupTest.group_id == group_id,
                                         GroupTest.calendar_year == calendar_year.id,
                                         GroupTest.calendar_month == calendar_month.id,
                                         ).all()

    test_status = GroupTest.query.filter(GroupTest.group_id == group_id, GroupTest.calendar_year == calendar_year.id,
                                         GroupTest.calendar_month == calendar_month.id,
                                         GroupTest.student_tests == None).first()
    last_test = GroupTest.query.filter(GroupTest.group_id == group_id, GroupTest.calendar_month == calendar_month.id,
                                       GroupTest.calendar_year == calendar_year.id,
                                       GroupTest.student_tests != None).order_by(desc(GroupTest.id)).first()

    if test_status:
        msg = f"Guruhda {test_status.day.date.strftime('%d')} kuni {test_status.level} leveli bo'yicha test olinishi kerak."
    elif last_test and not test_status:
        msg = f"Guruhda oxirgi marta {last_test.day.date.strftime('%d')} kuni {last_test.level} leveli bo'yicha test olingan."
    else:
        msg = f"Guruh uchun {calendar_month.date.strftime('%B')} oyi uchun test kuni belgilanmagan."
    return jsonify({
        "locationId": group.location_id,
        "groupName": group.name.title(),
        "groupID": group.id,
        "data": data,
        "teacher_id": teacher.user.id,
        "groupSubject": group.subject.name.title(),
        'groupStatus': group.status,
        "time_table": time_table_list,
        "level": info_level,
        "links": links,
        "levels": iterate_models(levels),
        "isTime": is_time,
        "test_info": iterate_models(group_tests),
        "msg": msg
    })


@app.route(f'{api}/group_time_table/<int:group_id>')
@jwt_required()
def group_time_table(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    week_days = Week.query.filter(Week.location_id == group.location_id).order_by(Week.order).all()
    table_list = []
    weeks = []
    for week in week_days:
        weeks.append(week.name)
    rooms = db.session.query(Rooms).join(Rooms.time_table).options(contains_eager(Rooms.time_table)).filter(
        Group_Room_Week.group_id == group_id, Rooms.location_id == group.location_id).all()
    for room in rooms:
        room_info = {
            "room": room.name,
            "id": room.id,
            "lesson": []
        }
        week_list = []
        for week in week_days:
            info = {
                "from": "",
                "to": ""
            }
            time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id,
                                                      Group_Room_Week.week_id == week.id,
                                                      Group_Room_Week.room_id == room.id).order_by(
                Group_Room_Week.group_id).first()
            if time_table:
                info["from"] = time_table.start_time.strftime("%H:%M")
                info["to"] = time_table.end_time.strftime("%H:%M")

            week_list.append(info)
            room_info['lesson'] = week_list
        table_list.append(room_info)
    return jsonify({
        "success": True,
        "data": table_list,
        "days": weeks
    })


@app.route(f'{api}/attendances/<int:group_id>', methods=['GET', "POST"])
@jwt_required()
def attendances(group_id):
    update_lesson_plan(group_id)
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).order_by(Students.id).all()
    student_list = [{
        "id": st.user.id,
        "img": None,
        "name": st.user.name.title(),
        "surname": st.user.surname.title(),
        "money": st.user.balance,
        "moneyType": ["green", "yellow", "red", "navy", "black"][st.debtor] if st.debtor else 0,
        "comment": st.user.comment,
        "reg_date": st.user.day.date.strftime("%Y-%m-%d"),
        "phone": st.user.phone[0].phone,
        "username": st.user.username,
        "age": st.user.age,
        "photo_profile": st.user.photo_profile,
        "role": Roles.query.filter(Roles.id == st.user.role_id).first().role
    } for st in students]

    gr_functions = Group_Functions(group_id=group_id)
    if request.method == "GET":
        current_month = datetime.now().month
        if len(str(current_month)) == 1:
            current_month = "0" + str(current_month)
        current_year = datetime.now().year

        return jsonify({

            "data": {
                "attendance_filter": gr_functions.attendance_filter(month=current_month, year=current_year),
                "students": student_list,
                "date": old_current_dates(group_id),
            }
        })

    else:
        year = get_json_field('year')

        month = get_json_field('month')
        print(year)
        print(month)
        return jsonify({

            "data": {
                "attendance_filter": gr_functions.attendance_filter(month=month, year=year),
                "students": student_list,
                "date": old_current_dates(group_id),
            }
        })


@app.route(f'{api}/attendances_android/<int:group_id>', methods=['GET', "POST"])
@jwt_required()
def attendances_android(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    attendance_group = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
        contains_eager(AttendanceDays.attendance)).filter(Attendance.group_id == group_id,
                                                          Attendance.calendar_month == calendar_month.id,
                                                          Attendance.calendar_year == calendar_year.id).order_by(
        AttendanceDays.id).all()
    day_list = []
    for get_att in attendance_group:
        if get_att.day.date.strftime("%Y-%m-%d") not in day_list:
            day_list.append(get_att.day.date.strftime("%Y-%m-%d"))
    day_list.sort()
    attendance_info = []
    for day in day_list:
        present = db.session.query(CalendarDay).join(CalendarDay.attendance).options(
            contains_eager(CalendarDay.attendance)).filter(AttendanceDays.group_id == group_id,
                                                           extract("year", CalendarDay.date) == int(day[0:4]),
                                                           extract("month", CalendarDay.date) == int(day[5:7]),
                                                           extract("day", CalendarDay.date) == int(day[8:10]),
                                                           AttendanceDays.status == 1,
                                                           ).count()
        absent = db.session.query(CalendarDay).join(CalendarDay.attendance).options(
            contains_eager(CalendarDay.attendance)).filter(AttendanceDays.group_id == group_id,
                                                           extract("year", CalendarDay.date) == int(day[0:4]),
                                                           extract("month", CalendarDay.date) == int(day[5:7]),
                                                           extract("day", CalendarDay.date) == int(day[8:10]),

                                                           AttendanceDays.status == 0).count()
        info = {
            "day": day,
            "present": present,
            "absent": absent
        }
        attendance_info.append(info)
    return jsonify({
        "attendance_info": attendance_info
    })


@app.route(f'{api}/get_attendance_day/<int:group_id>/<day>')
@jwt_required()
def get_attendance_day(group_id, day):
    day_attendances = db.session.query(AttendanceDays).join(AttendanceDays.day).options(
        contains_eager(AttendanceDays.day)).filter(AttendanceDays.group_id == group_id,
                                                   extract("year", CalendarDay.date) == int(day[0:4]),
                                                   extract("month", CalendarDay.date) == int(day[5:7]),
                                                   extract("day", CalendarDay.date) == int(day[8:10]),
                                                   ).order_by(AttendanceDays.id).all()
    return jsonify({
        "attendance_info": iterate_models(day_attendances)
    })


@app.route(f'{api}/group_dates2/<int:group_id>')
@jwt_required()
def group_dates(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    year_list = []
    month_list = []
    attendance_month = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.group_id == group_id,
    ).order_by(AttendanceHistoryStudent.id).all()

    for attendance in attendance_month:
        year = AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.group_id == group_id,
                                                     AttendanceHistoryStudent.calendar_year == attendance.calendar_year).all()
        info = {
            'year': '',
            'months': []
        }
        if info['year'] != attendance.year.date.strftime("%Y"):
            info['year'] = attendance.year.date.strftime("%Y")
        for month in year:
            if attendance.year.date.strftime("%Y") not in year_list:
                year_list.append(attendance.year.date.strftime("%Y"))
            if month.month.date.strftime("%m") not in info['months']:
                info['months'].append(month.month.date.strftime("%m"))
                info['months'].sort()
        month_list.append(info)
    year_list = list(dict.fromkeys(year_list))
    filtered_list = []
    for student in month_list:
        added_to_existing = False
        for merged in filtered_list:
            if merged['year'] == student['year']:
                added_to_existing = True
            if added_to_existing:
                break
        if not added_to_existing:
            filtered_list.append(student)
    return jsonify({
        "data": {
            "months": filtered_list,
            "years": year_list,
            "current_year": calendar_year.date.strftime("%Y"),
            "current_month": calendar_month.date.strftime("%m"),
        }
    })


@app.route(f'{api}/student_attendances/<int:student_id>/<int:group_id>/<month>')
@jwt_required()
def student_attendances(student_id, group_id, month):
    selected_month = datetime.strptime(month, "%Y-%m")
    student = Students.query.filter(Students.user_id == student_id).first()

    attendance_student_history = db.session.query(AttendanceHistoryStudent).join(
        AttendanceHistoryStudent.month).options(contains_eager(AttendanceHistoryStudent.month)).filter(
        CalendarMonth.date == selected_month, AttendanceHistoryStudent.student_id == student.id,
        AttendanceHistoryStudent.group_id == group_id).first()

    attendance = db.session.query(Attendance).join(Attendance.month).options(
        contains_eager(Attendance.month)).filter(
        CalendarMonth.date == selected_month, Attendance.group_id == group_id,
        Attendance.student_id == student.id).first()
    if attendance:
        student_attendances_present = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
            contains_eager(AttendanceDays.attendance)).filter(AttendanceDays.student_id == student.id,
                                                              AttendanceDays.group_id == group_id,
                                                              Attendance.calendar_month == attendance.calendar_month,
                                                              Attendance.calendar_year == attendance.calendar_year,
                                                              ).filter(
            or_(AttendanceDays.status == 1, AttendanceDays.status == 2)).order_by(
            AttendanceDays.calendar_day).all()
        student_attendances_absent = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
            contains_eager(AttendanceDays.attendance)).filter(AttendanceDays.student_id == student.id,
                                                              AttendanceDays.group_id == group_id,
                                                              Attendance.calendar_month == attendance.calendar_month,
                                                              Attendance.calendar_year == attendance.calendar_year,
                                                              AttendanceDays.status == 0).order_by(
            AttendanceDays.calendar_day).all()

        present_list = [{
            "id": present.id,
            "homework": present.homework,
            "dictionary": present.dictionary,
            "activeness": present.activeness,
            "averageBall": present.average_ball,
            "date": present.day.date.strftime("%Y.%m.%d")
        }

            for present in student_attendances_present]
        for present in student_attendances_present:
            print(present.day.date.strftime("%Y.%m.%d"))
        absent_list = [{
            "id": present.id,
            "date": present.day.date.strftime("%Y.%m.%d")
        } for present in student_attendances_absent]

        return jsonify({
            "data": {
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "present": present_list,
                "absent": absent_list,
                "totalBall": attendance_student_history.average_ball,
                "main_attendance": attendance_student_history.id,
                "status": False
            }

        })
    else:
        return jsonify({
            "data": {
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "present": [],
                "absent": [],
                "totalBall": 0,
                "main_attendance": 0,
                "status": 0
            }

        })


@app.route(f'{api}/combined_attendances/<int:student_id>', methods=["POST", "GET"])
@jwt_required()
def combined_attendances(student_id):
    student = Students.query.filter(Students.user_id == student_id).first()
    st_functions = Student_Functions(student_id=student.id)
    if request.method == "GET":
        current_month = datetime.now().month
        if len(str(current_month)) == 1:
            current_month = "0" + str(current_month)
        current_year = datetime.now().year
        return jsonify({
            "data": st_functions.attendance_filter_student(month=current_month, year=current_year)
        })
    else:
        year = get_json_field('year')

        month = get_json_field('month')

        return jsonify({
            "data": st_functions.attendance_filter_student(month=month, year=year)
        })


@app.route(f'{api}/student_group_dates2/<int:student_id>')
@jwt_required()
def student_group_dates2(student_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    year_list = []
    month_list = []
    student = Students.query.filter(Students.user_id == student_id).first()
    attendance_month = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.student_id == student.id,
    ).order_by(AttendanceHistoryStudent.id).all()

    for attendance in attendance_month:
        year = AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.student_id == student.id,

                                                     AttendanceHistoryStudent.calendar_year == attendance.calendar_year).all()
        info = {
            'year': '',
            'months': []
        }
        if info['year'] != attendance.year.date.strftime("%Y"):
            info['year'] = attendance.year.date.strftime("%Y")
        for month in year:
            if attendance.year.date.strftime("%Y") not in year_list:
                year_list.append(attendance.year.date.strftime("%Y"))
            if month.month.date.strftime("%m") not in info['months']:
                info['months'].append(month.month.date.strftime("%m"))
                info['months'].sort()
        month_list.append(info)

    day_dict = {gr['year']: gr for gr in month_list}
    filtered_list = list(day_dict.values())
    return jsonify({
        "data": {
            "months": filtered_list,
            "years": year_list,
            "current_year": calendar_year.date.strftime("%Y"),
            "current_month": calendar_month.date.strftime("%m"),
        }
    })
