from app import api, app, jsonify, contains_eager, request, db, and_, or_, extract
from backend.functions.utils import remove_items_create_group
from backend.models.models import Subjects, CourseTypes, Rooms, Week, Teachers, Group_Room_Week, Students, Users, \
    StudentHistoryGroups, Groups, RegisterDeletedStudents, Roles, Locations, DeletedStudents, GroupReason, CalendarDay, \
    TeacherGroupStatistics
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.functions.utils import get_json_field, find_calendar_date
from datetime import datetime

from pprint import pprint


@app.route(f'{api}/create_group_tools')
@jwt_required()
def create_group_tools():
    course_types = CourseTypes.query.order_by('id').all()
    subjects = Subjects.query.order_by('id').all()
    subject_list = []
    course_list = []
    for subject in subjects:
        info = {
            "name": subject.name,
            "id": subject.id
        }
        subject_list.append(info)

    for course in course_types:
        info = {
            "name": course.name,
            "id": course.id
        }
        course_list.append(info)
    filters = {
        "subjects": subject_list,
        "course_types": course_list,
    }
    return jsonify({
        "createGroupTools": filters
    })


@app.route(f'/{api}/get_students/<int:location_id>', methods=['POST'])
def get_students(location_id):
    gr_errors = []
    student_errors = []
    teacher_errors = []
    lessons = request.get_json()['lessons']
    for lesson in lessons:
        start_time = datetime.strptime(lesson.get('startTime'), "%H:%M")
        end_time = datetime.strptime(lesson.get('endTime'), "%H:%M")

        time_table_start = Group_Room_Week.query.filter(Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                        Group_Room_Week.room_id == lesson['selectedRoom'].get('id')
                                                        ).filter(
            and_(Group_Room_Week.start_time <= start_time, Group_Room_Week.end_time >= start_time)).order_by(
            Group_Room_Week.id).first()
        time_table_end = Group_Room_Week.query.filter(Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                      Group_Room_Week.room_id == lesson['selectedRoom'].get('id')
                                                      ).filter(
            and_(Group_Room_Week.start_time <= end_time, Group_Room_Week.end_time >= end_time)).order_by(
            Group_Room_Week.id).first()
        if time_table_start and time_table_end:
            error = f"{time_table_start.week.name} kuni {time_table_start.room.name} da soat: '{time_table_start.start_time.strftime('%H:%M')} {time_table_start.end_time.strftime('%H:%M')}' da {time_table_start.group.name} ni darsi bor. "
            gr_errors.append(error)
        elif time_table_start and not time_table_end:
            error = f"{time_table_start.week.name} kuni {time_table_start.room.name} da soat {time_table_start.start_time.strftime('%H:%M')} da {time_table_start.group.name} ni darsi boshlangan bo'ladi. "
            gr_errors.append(error)
        elif time_table_end and not time_table_start:
            error = f"{time_table_end.week.name} kuni {time_table_end.room.name} da soat {time_table_end.end_time.strftime('%H:%M')} da {time_table_end.group.name} ni darsi davom etayotgan bo'ladi. "
            gr_errors.append(error)
        role = Roles.query.filter(Roles.type_role == "student").first()
        role_teacher = Roles.query.filter(Roles.type_role == "teacher").first()

        teachers = db.session.query(Teachers).join(Teachers.user).options(contains_eager(Teachers.user)).filter(
        ).join(Teachers.locations).options(contains_eager(Teachers.locations)).filter(
            Locations.id == location_id).order_by(Teachers.id).all()
        for teacher in teachers:
            teacher_time_start = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
                contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                                Group_Room_Week.week_id == lesson['selectedDay'].get(
                                                                    'id'),
                                                                Group_Room_Week.location_id == location_id).filter(
                and_(Group_Room_Week.start_time <= start_time, Group_Room_Week.end_time >= start_time)).first()
            teacher_time_end = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
                contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                                Group_Room_Week.location_id == location_id,
                                                                Group_Room_Week.week_id == lesson['selectedDay'].get(
                                                                    'id')).filter(
                and_(Group_Room_Week.start_time <= end_time, Group_Room_Week.end_time >= end_time)).first()

            info = {
                "id": teacher.user.id,
                "name": teacher.user.name.title(),
                "surname": teacher.user.surname.title(),
                "username": teacher.user.username,
                "language": teacher.user.language.name,
                "age": teacher.user.age,
                "reg_date": teacher.user.day.date.strftime("%Y-%m-%d"),
                "comment": teacher.user.comment,
                'money': teacher.user.balance,
                "role": role_teacher.role,
                "subjects": [subject.name for subject in teacher.subject],
                "photo_profile": teacher.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            if teacher_time_start and teacher_time_end:
                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{teacher_time_start.week.name} da soat: '{teacher_time_start.start_time.strftime('%H:%M')} dan " \
                               f"{teacher_time_end.end_time.strftime('%H:%M')}' gacha {teacher_time_end.group.name} da darsi bor."
            elif teacher_time_start and not teacher_time_end:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{teacher_time_start.week.name} da soat: {teacher_time_start.start_time.strftime('%H:%M')} " \
                               f"da {teacher_time_start.group.name} da darsi bor."
            elif teacher_time_end and not teacher_time_start:
                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{teacher_time_end.week.name} da soat: {teacher_time_end.start_time.strftime('%H:%M')} " \
                               f"da {teacher_time_end.group.name} da darsi davom etayotgan bo'ladi."
            teacher_errors.append(info)
        time_start = "14:00"
        time_end = "07:00"
        time_start = datetime.strptime(time_start, "%H:%M")
        time_end = datetime.strptime(time_end, "%H:%M")
        morning_shift = False
        night_shift = False
        if start_time >= time_start and end_time <= time_end:
            night_shift = True
        else:
            morning_shift = True
        students_not_available_morning = ''
        students_not_available_night = ''
        if night_shift:
            students_available = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(or_(
                Students.night_shift == night_shift, Students.night_shift == None)).filter(
                Users.location_id == location_id, Students.group == None, Students.deleted_from_register == None,
            ).join(Students.subject).options(
                contains_eager(Students.subject)).order_by(
                Users.calendar_day).all()
            students_not_available_morning = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(
                Students.night_shift == False, Students.group == None, Students.deleted_from_register == None,
            ).filter(Users.location_id == location_id).join(
                Students.subject).order_by(
                Users.calendar_day).all()
        else:
            students_available = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(or_(
                Students.morning_shift == morning_shift, Students.morning_shift == None)).filter(
                Users.location_id == location_id, Students.group == None, Students.deleted_from_register == None,
            ).join(Students.subject).options(
                contains_eager(Students.subject)).order_by(
                Users.calendar_day).all()
            students_not_available_night = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(
                Students.morning_shift == False, Students.group == None, Students.deleted_from_register == None,
            ).filter(Users.location_id == location_id).join(
                Students.subject).options(
                contains_eager(Students.subject)).order_by(
                Users.calendar_day).all()

        for student in students_available:
            info = {
                "id": student.user.id,
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "username": student.user.username,
                "language": student.user.language.name,
                "age": student.user.age,
                "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                "comment": student.user.comment,
                'money': student.user.balance,
                "role": role.role,
                "subjects": [subject.name for subject in student.subject],
                "photo_profile": student.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            student_errors.append(info)
        if students_not_available_morning and not students_not_available_night:
            for student in students_not_available_morning:
                info = {
                    "id": student.user.id,
                    "name": student.user.name.title(),
                    "surname": student.user.surname.title(),
                    "username": student.user.username,
                    "language": student.user.language.name,
                    "age": student.user.age,
                    "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                    "comment": student.user.comment,
                    'money': student.user.balance,
                    "role": role.role,
                    "subjects": [[subject.name for subject in student.subject]],
                    "photo_profile": student.user.photo_profile,
                    "color": "red",
                    "error": True,
                    "shift": "Studentga ertalabki smen belgilangan."
                }
                student_errors.append(info)
            else:
                for student in students_not_available_night:
                    info = {
                        "id": student.user.id,
                        "name": student.user.name.title(),
                        "surname": student.user.surname.title(),
                        "username": student.user.username,
                        "language": student.user.language.name,
                        "age": student.user.age,
                        "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                        "comment": student.user.comment,
                        'money': student.user.balance,
                        "role": role.role,
                        "subjects": [subject.name for subject in student.subject],
                        "photo_profile": student.user.photo_profile,
                        "color": "red",
                        "error": True,
                        "shift": "Studentga kechki smen belgilangan."
                    }
                    student_errors.append(info)
        students = db.session.query(Students).join(Students.subject).options(contains_eager(Students.subject)).filter(
            Students.group != None, Students.deleted_from_register == None,
        ).join(Students.user).options(
            contains_eager(Students.user)).filter(
            Users.location_id == location_id).all()
        for student in students:
            student_group_start = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == lesson['selectedDay'].get('id'),

                                                     ).filter(
                and_(Group_Room_Week.start_time <= start_time, Group_Room_Week.end_time >= start_time)).first()
            student_group_end = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == lesson['selectedDay'].get('id'),

                                                     ).filter(
                and_(Group_Room_Week.start_time <= end_time, Group_Room_Week.end_time >= end_time)).first()
            info = {
                "id": student.user.id,
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "username": student.user.username,
                "language": student.user.language.name,
                "age": student.user.age,
                "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                "comment": student.user.comment,
                'money': student.user.balance,
                "role": role.role,
                "subjects": [subject.name for subject in student.subject],
                "photo_profile": student.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            if student_group_start and student_group_end:
                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: '{student_group_start.start_time.strftime('%H:%M')} dan {student_group_end.end_time.strftime('%H:%M')}' gacha {student_group_start.group.name} da darsi bor."
                student_errors.append(info)
            elif student_group_start and not student_group_end:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: {student_group_start.start_time.strftime('%H:%M')} da {student_group_start.group.name} da darsi bor."
                student_errors.append(info)
            elif student_group_end and not student_group_start:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_end.week.name} da soat: {student_group_end.end_time.strftime('%H:%M')} da {student_group_end.group.name} da darsi bor."

                student_errors.append(info)
            else:
                student_errors.append(info)
    filtered_students = remove_items_create_group(student_errors)
    filtered_teachers = remove_items_create_group(teacher_errors)
    return jsonify({
        "success": True,
        "data": {
            'gr_errors': gr_errors,
            "students": filtered_students,
            "teachers": filtered_teachers,
        }
    })


@app.route(f'{api}/create_group_time/<int:location_id>', methods=['POST'])
def create_group_time(location_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    group_name = request.get_json()['groupInfo']['groupName']
    group_price = request.get_json()['groupInfo']['groupPrice']
    subject = request.get_json()['groupInfo']['subject']
    type_course = request.get_json()['groupInfo']['typeCourse']
    teacher_salary = int(request.get_json()['groupInfo']['teacherDolya'])
    subject = Subjects.query.filter(Subjects.name == subject).first()
    type_course = CourseTypes.query.filter(CourseTypes.name == type_course).first()
    teacher = Teachers.query.filter(Teachers.user_id == request.get_json()['teacher']['id']).first()
    add = Groups(name=group_name, course_type_id=type_course.id, subject_id=subject.id, location_id=location_id,
                 education_language=teacher.user.education_language, calendar_day=calendar_day.id, attendance_days=13,
                 calendar_month=calendar_month.id, calendar_year=calendar_year.id, teacher_id=teacher.id,
                 price=group_price, teacher_salary=teacher_salary)
    db.session.add(add)
    db.session.commit()
    for time in request.get_json()['time']:
        start_time = time['startTime']
        end_time = time['endTime']
        start_time = datetime.strptime(start_time, "%H:%M")
        end_time = datetime.strptime(end_time, "%H:%M")
        room = Rooms.query.filter(Rooms.id == time['selectedRoom']['id']).first()
        week_day = Week.query.filter(Week.id == time['selectedDay']['id']).first()

        time_table = Group_Room_Week(group_id=add.id, room_id=room.id, week_id=week_day.id, start_time=start_time,
                                     end_time=end_time, location_id=location_id)
        db.session.add(time_table)
        db.session.commit()
        teacher.time_table.append(time_table)
        db.session.commit()
        student_list = request.get_json()['students']
        student_id_list = []

        for loc in student_list:
            student_id_list.append(int(loc['id']))

        students_checked = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
            Users.id.in_([user_id for user_id in student_id_list])).order_by('id').all()

        for st in students_checked:
            for sub in st.subject:
                if sub.name == subject.name:
                    st.subject.remove(subject)
            st.group.append(add)
            st.time_table.append(time_table)
            group_history = StudentHistoryGroups.query.filter(StudentHistoryGroups.teacher_id == teacher.id,
                                                              StudentHistoryGroups.student_id == st.id,
                                                              StudentHistoryGroups.group_id == add.id,
                                                              StudentHistoryGroups.joined_day == calendar_day.date).first()
            if not group_history:
                group_history = StudentHistoryGroups(teacher_id=teacher.id, student_id=st.id, group_id=add.id,
                                                     joined_day=calendar_day.date)
                db.session.add(group_history)
                db.session.commit()
    teacher.group.append(add)
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Guruh muvaffiqiyatli yaratildi, Kassani bosila"
    })


@app.route(f'{api}/create_group', methods=['POST'])
@jwt_required()
def create_group():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    group_name = get_json_field('groupName')
    group_price = int(get_json_field('groupPrice'))
    subject = get_json_field('subject')
    teacher = int(get_json_field('teacher'))
    type_course = get_json_field('typeCourse')
    teacher_dolya = int(get_json_field('teacherDolya'))
    # attendance_days = int(json_request['attendanceDays'])
    student_list = get_json_field('checkedStudents')
    location = 0
    student_id_list = []

    for loc in student_list:
        location = int(loc['location_id'])
        student_id_list.append(int(loc['id']))
    teacher_get = Teachers.query.filter(Teachers.user_id == teacher).first()
    location_get = Locations.query.filter(Locations.id == location).first()
    subject_get = Subjects.query.filter(Subjects.name == subject).first()
    course_type_get = CourseTypes.query.filter(CourseTypes.name == type_course).first()
    add = Groups(name=group_name, course_type_id=course_type_get.id, subject_id=subject_get.id,
                 teacher_salary=teacher_dolya, location_id=location_get.id, calendar_day=calendar_day.id,
                 calendar_month=calendar_month.id, calendar_year=calendar_year.id, price=group_price,
                 education_language=teacher_get.user.education_language, teacher_id=teacher_get.id,
                 attendance_days=13)
    db.session.add(add)
    db.session.commit()
    teacher_get.group.append(add)
    students_checked = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
        Users.id.in_([user_id for user_id in student_id_list])).order_by('id').all()

    for st in students_checked:
        for sub in st.subject:
            if sub.name == subject_get.name:
                st.subject.remove(subject_get)
        st.group.append(add)
        group_history = StudentHistoryGroups(teacher_id=teacher_get.id, student_id=st.id, group_id=add.id,
                                             joined_day=calendar_day.date)
        db.session.add(group_history)
        db.session.commit()
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Guruh muvaffiqiyatli yaratildi, Kassani bosila"
    })


@app.route(f'{api}/add_group_students2/<int:group_id>', methods=['POST', 'GET'])
def add_group_students2(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    if request.method == "POST":
        group = Groups.query.filter(Groups.id == group_id).first()
        subject = Subjects.query.filter(Subjects.id == group.subject_id).first()
        student_list = get_json_field('checkedStudents')
        student_id_list = []
        for loc in student_list:
            student_id_list.append(int(loc['id']))
        msg = "O'quvchi guruhga qo'shildi"
        if len(student_id_list) > 1:
            msg = "O'quvchilar guruhga qo'shildi"
        print('st',student_id_list)
        students_checked = db.session.query(Students).join(Students.user).options(contains_eager(Students.user)).filter(
            Users.id.in_([user_id for user_id in student_id_list]),
        ).order_by(
            'id').all()
        print(students_checked)
        for st in students_checked:
            for sub in st.subject:
                if sub.name == subject.name:
                    st.subject.remove(subject)
            st.group.append(group)
            group_history = StudentHistoryGroups(teacher_id=group.teacher_id, student_id=st.id, group_id=group.id,
                                                 joined_day=calendar_day.date)
            db.session.add(group_history)
            db.session.commit()
        time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).all()
        for st in students_checked:
            for time in time_table:
                st.time_table.append(time)
                db.session.commit()
        return jsonify({
            "success": True,
            "msg": msg
        })

    group = Groups.query.filter(Groups.id == group_id).first()

    time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).all()
    location_id = group.location_id
    time_start = "14:00"
    time_end = "07:00"
    time_start = datetime.strptime(time_start, "%H:%M")
    time_end = datetime.strptime(time_end, "%H:%M")
    student_errors = []
    role = Roles.query.filter(Roles.type_role == "student").first()

    for time in time_table:
        morning_shift = False
        night_shift = False
        startTime = time.start_time
        endTime = time.end_time
        if startTime >= time_start or endTime <= time_end:
            night_shift = True
        else:
            morning_shift = True
        students_not_available_morning = ''
        students_not_available_night = ''
        if night_shift:
            students_available = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(or_(
                Students.night_shift == night_shift, Students.night_shift == None)).filter(
                Users.location_id == location_id, Students.group == None, Students.deleted_from_register == None,
            ).join(Students.subject).options(
                contains_eager(Students.subject)).order_by(
                Users.calendar_day).filter(Subjects.id == group.subject_id).all()
            students_not_available_morning = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(
                Students.night_shift == False, Students.group == None, Students.deleted_from_register == None,
            ).filter(Users.location_id == location_id).join(
                Students.subject).filter(Subjects.id == group.subject_id).order_by(
                Users.calendar_day).all()
        else:
            students_available = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(or_(
                Students.morning_shift == morning_shift, Students.morning_shift == None)).filter(
                Users.location_id == location_id, Students.group == None, Students.deleted_from_register == None,
            ).join(Students.subject).options(
                contains_eager(Students.subject)).filter(Subjects.id == group.subject_id).order_by(
                Users.calendar_day).all()
            students_not_available_night = db.session.query(Students).join(Students.user).options(
                contains_eager(Students.user)).filter(
                Students.morning_shift == False, Students.group == None, Students.deleted_from_register == None,
            ).filter(Users.location_id == location_id).join(
                Students.subject).options(
                contains_eager(Students.subject)).filter(Subjects.id == group.subject_id).order_by(
                Users.calendar_day).all()
        for student in students_available:
            info = {
                "id": student.user.id,
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "username": student.user.username,
                "language": student.user.language.name,
                "age": student.user.age,
                "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                "comment": student.user.comment,
                'money': student.user.balance,
                "role": role.role,
                "subjects": [subject.name for subject in student.subject],
                "photo_profile": student.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            student_errors.append(info)
        if students_not_available_morning and not students_not_available_night:
            for student in students_not_available_morning:
                info = {
                    "id": student.user.id,
                    "name": student.user.name.title(),
                    "surname": student.user.surname.title(),
                    "username": student.user.username,
                    "language": student.user.language.name,
                    "age": student.user.age,
                    "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                    "comment": student.user.comment,
                    'money': student.user.balance,
                    "role": role.role,
                    "subjects": [subject.name for subject in student.subject],
                    "photo_profile": student.user.photo_profile,
                    "color": "red",
                    "error": True,
                    "shift": "Studentga ertalabki smen belgilangan."
                }
                student_errors.append(info)
        else:
            for student in students_not_available_night:
                info = {
                    "id": student.user.id,
                    "name": student.user.name.title(),
                    "surname": student.user.surname.title(),
                    "username": student.user.username,
                    "language": student.user.language.name,
                    "age": student.user.age,
                    "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                    "comment": student.user.comment,
                    'money': student.user.balance,
                    "role": role.role,
                    "subjects": [subject.name for subject in student.subject],
                    "photo_profile": student.user.photo_profile,
                    "color": "red",
                    "error": True,
                    "shift": "Studentga kechki smen belgilangan."
                }
                student_errors.append(info)
        students = db.session.query(Students).join(Students.subject).options(contains_eager(Students.subject)).filter(
            Students.group != None, Subjects.id == group.subject_id).join(Students.user).options(
            contains_eager(Students.user)).filter(
            Users.location_id == location_id).all()
        for student in students:
            student_group_start = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == time.week_id,

                                                     ).filter(
                and_(Group_Room_Week.start_time <= startTime, Group_Room_Week.end_time >= startTime)).first()
            student_group_end = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == time.week_id,

                                                     ).filter(
                and_(Group_Room_Week.start_time <= endTime, Group_Room_Week.end_time >= endTime)).first()
            info = {
                "id": student.user.id,
                "name": student.user.name.title(),
                "surname": student.user.surname.title(),
                "username": student.user.username,
                "language": student.user.language.name,
                "age": student.user.age,
                "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                "comment": student.user.comment,
                'money': student.user.balance,
                "role": role.role,
                "subjects": [subject.name for subject in student.subject],
                "photo_profile": student.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            if student_group_start and student_group_end:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: '{student_group_start.start_time.strftime('%H:%M')} dan " \
                               f"{student_group_end.end_time.strftime('%H:%M')}' gacha {student_group_start.group.name} da darsi bor."

            elif student_group_start and not student_group_end:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: {student_group_start.start_time.strftime('%H:%M')} " \
                               f"da {student_group_start.group.name} da darsi bor."
            elif student_group_end and not student_group_start:

                info["color"] = "red",
                info["error"] = True,
                info[
                    "shift"] = f"{student_group_end.week.name} da soat: {student_group_end.end_time.strftime('%H:%M')} " \
                               f"da {student_group_end.group.name} da darsi bor."
            student_errors.append(info)
    filtered_students = remove_items_create_group(student_errors)
    return jsonify({
        "data": filtered_students,
        "success": True
    })


@app.route(f'{api}/move_group/<int:new_group_id>/<int:old_group_id>', methods=['POST'])
@jwt_required()
def move_group(new_group_id, old_group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    students = get_json_field('checkedStudents')
    reason = get_json_field('reason')
    student_list = []
    for st in students:
        if st['id'] not in student_list:
            student_list.append(st['id'])

    new_group = Groups.query.filter(Groups.id == new_group_id).first()
    old_group = Groups.query.filter(Groups.id == old_group_id).first()

    students_checked = db.session.query(Students).join(Students.user).options(
        contains_eager(Students.user)).filter(Users.id.in_([st_id for st_id in student_list])).all()
    for st in students_checked:
        st.group.remove(old_group)
        db.session.commit()
        st.group.append(new_group)
        StudentHistoryGroups.query.filter(StudentHistoryGroups.group_id == old_group.id,
                                          StudentHistoryGroups.student_id == st.id,
                                          StudentHistoryGroups.teacher_id == old_group.teacher_id).update(
            {'left_day': calendar_day.date,
             "reason": reason})
        db.session.commit()
        group_history = StudentHistoryGroups(teacher_id=new_group.teacher_id, student_id=st.id, group_id=new_group.id,
                                             joined_day=calendar_day.date)
        db.session.add(group_history)
        db.session.commit()
    db.session.commit()
    if len(student_list) > 1:
        return jsonify({
            "success": True,
            "msg": "O'quvchilar yangi guruhga qo'shilishdi"
        })
    else:
        return jsonify({
            "success": True,
            "msg": "O'quvchi yangi guruhga qo'shildi"
        })


@app.route(f'{api}/filtered_groups/<int:group_id>')
@jwt_required()
def filtered_groups(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    groups = Groups.query.filter(Groups.location_id == group.location_id,
                                 Groups.id != group.id,
                                 Groups.teacher_id != None, Groups.time_table != None).filter(
        or_(Groups.deleted == None, Groups.deleted == False)).order_by('id').all()
    list_group = []
    for gr in groups:
        if gr.status:
            status = "True"
        else:
            status = "False"
        info = {
            "id": gr.id,
            "name": gr.name.title(),
            "teacherID": gr.teacher_id,
            "subjects": gr.subject.name.title(),
            "payment": gr.price,
            "typeOfCourse": gr.course_type.name,
            "studentsLength": len(gr.student),
            "status": status,
        }
        teacher = Teachers.query.filter(Teachers.id == gr.teacher_id).first()

        info['teacherName'] = teacher.user.name.title()
        info['teacherSurname'] = teacher.user.surname.title()
        list_group.append(info)
    return jsonify({
        "groups": list_group
    })


@app.route(f'{api}/filtered_groups2/<int:location_id>')
@jwt_required()
def filtered_groups2(location_id):
    groups = Groups.query.filter(Groups.location_id == location_id,

                                 Groups.teacher_id != None, Groups.time_table != None).filter(
        or_(Groups.deleted == None, Groups.deleted == False)).order_by('id').all()
    list_group = []
    for gr in groups:
        if gr.status:
            status = "True"
        else:
            status = "False"
        info = {
            "id": gr.id,
            "name": gr.name.title(),
            "teacherID": gr.teacher_id,
            "subjects": gr.subject.name.title(),
            "payment": gr.price,
            "typeOfCourse": gr.course_type.name,
            "studentsLength": len(gr.student),
            "status": status,
        }
        teacher = Teachers.query.filter(Teachers.id == gr.teacher_id).first()

        info['teacherName'] = teacher.user.name.title()
        info['teacherSurname'] = teacher.user.surname.title()
        list_group.append(info)
    return jsonify({
        "groups": list_group
    })


@app.route(f'{api}/moving_students/<int:old_id>/<int:new_id>')
def moving_students(old_id, new_id):
    old_group = Groups.query.filter(Groups.id == old_id).first()
    new_group = Groups.query.filter(Groups.id == new_id).first()
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == old_group.id).all()
    time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == new_group.id).all()
    student_errors = []
    role = Roles.query.filter(Roles.type_role == "student").first()
    if time_table:
        for time in time_table:
            for student in students:
                student_group_start = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                    contains_eager(
                        Group_Room_Week.student)).filter(Students.id == student.id,
                                                         Group_Room_Week.week_id == time.week_id,
                                                         Group_Room_Week.group_id != old_group.id,
                                                         ).filter(
                    and_(Group_Room_Week.start_time <= time.start_time,
                         Group_Room_Week.end_time >= time.start_time)).first()
                student_group_end = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                    contains_eager(
                        Group_Room_Week.student)).filter(Students.id == student.id,
                                                         Group_Room_Week.week_id == time.week_id,
                                                         Group_Room_Week.group_id != old_group.id,
                                                         ).filter(
                    and_(Group_Room_Week.start_time <= time.end_time,
                         Group_Room_Week.end_time >= time.end_time)).first()
                info = {
                    "id": student.user.id,
                    "name": student.user.name.title(),
                    "surname": student.user.surname.title(),
                    "username": student.user.username,
                    "language": student.user.language.name,
                    "age": student.user.age,
                    "reg_date": student.user.day.date.strftime("%Y-%m-%d"),
                    "comment": student.user.comment,
                    'money': student.user.balance,
                    "role": role.role,
                    "subjects": [subject.name for subject in student.subject],
                    "photo_profile": student.user.photo_profile,
                    "color": "green",
                    "error": False,
                    "shift": ""
                }
                if student_group_start and student_group_end:

                    info["color"] = "red",
                    info["error"] = True,
                    info[
                        "shift"] = f"{student_group_start.week.name} da soat: '{student_group_start.start_time.strftime('%H:%M')} dan " \
                                   f"{student_group_end.end_time.strftime('%H:%M')}' gacha {student_group_start.group.name} da darsi bor."
                elif student_group_start and not student_group_end:
                    info["color"] = "red",
                    info["error"] = True,
                    info[
                        "shift"] = f"{student_group_start.week.name} da soat: {student_group_start.start_time.strftime('%H:%M')} " \
                                   f"da {student_group_start.group.name} da darsi bor."
                elif student_group_end and not student_group_start:

                    info["color"] = "red",
                    info["error"] = True,
                    info[
                        "shift"] = f"{student_group_end.week.name} da soat: {student_group_end.end_time.strftime('%H:%M')} " \
                                   f"da {student_group_end.group.name} da darsi bor."

                student_errors.append(info)

    filtered_students = remove_items_create_group(student_errors)

    return jsonify({
        "students": filtered_students,
        "success": True
    })


@app.route(f'{api}/move_group_time/<int:old_group_id>/<int:new_group_id>', methods=['POST'])
@jwt_required()
def move_group_time(old_group_id, new_group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    students = get_json_field('checkedStudents')
    reason = get_json_field('reason')
    student_list = []

    for st in students:
        if st['id'] not in student_list:
            student_list.append(st['id'])

    new_group = Groups.query.filter(Groups.id == new_group_id).first()
    old_group = Groups.query.filter(Groups.id == old_group_id).first()

    students_checked = db.session.query(Students).join(Students.user).options(
        contains_eager(Students.user)).filter(Users.id.in_([st_id for st_id in student_list])).all()

    old_time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == old_group.id).all()
    new_time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == new_group.id).all()
    for st in students_checked:
        st.group.remove(old_group)
        db.session.commit()
        st.group.append(new_group)
        StudentHistoryGroups.query.filter(StudentHistoryGroups.group_id == old_group.id,
                                          StudentHistoryGroups.student_id == st.id,
                                          StudentHistoryGroups.teacher_id == old_group.teacher_id).update(
            {'left_day': calendar_day.date,
             "reason": reason})
        db.session.commit()
        group_history = StudentHistoryGroups(teacher_id=new_group.teacher_id, student_id=st.id, group_id=new_group.id,
                                             joined_day=calendar_day.date)
        db.session.add(group_history)
        db.session.commit()
        for time in old_time_table:
            if time in st.time_table:
                st.time_table.remove(time)
                db.session.commit()
        for time in new_time_table:
            if time in st.time_table:
                st.time_table.append(time)
                db.session.commit()
    db.session.commit()
    if len(student_list) > 1:
        return jsonify({
            "success": True,
            "msg": "O'quvchilar yangi guruhga qo'shilishdi"
        })
    else:
        return jsonify({
            "success": True,
            "msg": "O'quvchi yangi guruhga qo'shildi"
        })


@app.route(f'{api}/delete_student', methods=['POST'])
@jwt_required()
def delete_student():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    type_delete = get_json_field('typeLocation')
    student_id = int(get_json_field('student_id'))
    student = Students.query.filter(Students.user_id == student_id).first()
    if type_delete == "deletedStudents":
        reason = get_json_field('typeReason')
        groupId = int(get_json_field('groupId'))

        group = Groups.query.filter(Groups.id == groupId).first()
        if reason == "Boshqa":
            reason = get_json_field('otherReason')
            group_reason = GroupReason.query.filter(GroupReason.reason == "Boshqa").first()
        else:
            group_reason = GroupReason.query.filter(GroupReason.reason == reason).first()
        add = DeletedStudents(student_id=student.id, group_id=group.id, reason=reason, teacher_id=group.teacher_id,
                              calendar_day=calendar_day.id, reason_id=group_reason.id)
        db.session.add(add)
        db.session.commit()
        student.group.remove(group)
        db.session.commit()
        time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).all()
        for time in time_table:
            if time in student.time_table:
                student.time_table.remove(time)
                db.session.commit()
        teacher_get = Teachers.query.filter(Teachers.id == group.teacher_id).first()
        deleted_students_total = DeletedStudents.query.filter(
            DeletedStudents.teacher_id == teacher_get.id).join(DeletedStudents.day).filter(
            extract("month", CalendarDay.date) == int(calendar_month.date.strftime("%m")),
            extract("year", CalendarDay.date) == int(calendar_month.date.strftime("%Y"))).count()
        deleted_students_list = DeletedStudents.query.filter(DeletedStudents.teacher_id == teacher_get.id,
                                                             DeletedStudents.reason_id == group_reason.id,
                                                             ).join(DeletedStudents.day).filter(
            extract("month", CalendarDay.date) == int(calendar_month.date.strftime("%m")),
            extract("year", CalendarDay.date) == int(calendar_month.date.strftime("%Y"))).count()
        if deleted_students_total:
            result = round((deleted_students_list / deleted_students_total) * 100)
            teacher_statistics = TeacherGroupStatistics.query.filter(
                TeacherGroupStatistics.reason_id == group_reason.id,
                TeacherGroupStatistics.calendar_month == calendar_month.id,
                TeacherGroupStatistics.calendar_year == calendar_year.id,
                TeacherGroupStatistics.teacher_id == teacher_get.id).first()
            if not teacher_statistics:
                teacher_statistics = TeacherGroupStatistics(
                    reason_id=group_reason.id,
                    calendar_month=calendar_month.id,
                    calendar_year=calendar_year.id,
                    percentage=result,
                    number_students=deleted_students_list,
                    teacher_id=teacher_get.id)
                teacher_statistics.add()
            else:
                teacher_statistics.number_students = deleted_students_list
                teacher_statistics.percentage = result
                db.session.commit()
    elif type_delete == "newStudents":
        groupId = int(request.get_json()['groupId'])

        group = Groups.query.filter(Groups.id == groupId).first()
        subject = Subjects.query.filter(Subjects.id == group.subject_id).first()
        student.subject.append(subject)
        db.session.commit()

        student.group.remove(group)
        db.session.commit()
        time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).all()
        for time in time_table:
            if time in student.time_table:
                student.time_table.remove(time)
                db.session.commit()
    else:
        reason = request.get_json()['otherReason']
        student.user.comment = reason
        add = RegisterDeletedStudents(student_id=student.id, reason=reason, calendar_day=calendar_day.id)
        db.session.add(add)
        db.session.commit()

    if type_delete == "newStudents" or type_delete == "deletedStudents":
        return jsonify({
            "success": True,
            "msg": "Student guruhdan o'chirildi"
        })
    else:
        return jsonify({
            "success": True,
            "msg": "Student ro'yxatdan o'chirildi"
        })
