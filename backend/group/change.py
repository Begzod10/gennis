from app import app, db, and_, jsonify, contains_eager, request
from backend.models.models import Teachers, Group_Room_Week, Students, Groups, Subjects, Locations, Roles, \
    EducationLanguage, CourseTypes, Rooms, Week
from flask_jwt_extended import jwt_required
from datetime import datetime
from pprint import pprint
from backend.functions.utils import get_json_field, remove_items_create_group, api


# from datetime import datetime


@app.route(f'{api}/change_group_info/<int:group_id>', methods=['POST'])
@jwt_required()
def change_group_info(group_id):
    name = get_json_field('name')
    teacher_salary = int(get_json_field('teacherQuota'))
    price = int(get_json_field('groupCost'))
    teacher_id = int(get_json_field('teacher'))
    language = get_json_field('eduLang')
    course_type = get_json_field('courseType')
    status = get_json_field('status')
    level_id = None

    if 'level_id' in request.get_json():
        level_id = get_json_field('level_id')

    if level_id == {}:
        level_id = None
    teacher = Teachers.query.filter(Teachers.user_id == teacher_id).first()
    language = EducationLanguage.query.filter(EducationLanguage.name == language).first()
    course_type = CourseTypes.query.filter(CourseTypes.name == course_type).first()
    group = Groups.query.filter(Groups.id == group_id).first()
    old_teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()

    Groups.query.filter(Groups.id == group_id).update({
        "name": name,
        "teacher_salary": teacher_salary,
        "price": price,
        "teacher_id": teacher.id,
        "education_language": language.id,
        "course_type_id": course_type.id,
        "status": status,
        "level_id": level_id
    })
    if old_teacher.id != teacher.id:
        if group in old_teacher.group:
            old_teacher.group.remove(group)
            db.session.commit()
        teacher.group.append(group)
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Guruh ma'lumotlari o'zgartirildi"
    })


@app.route(f'{api}/add_teacher_group/<int:teacher_id>/<int:group_id>')
@jwt_required()
def add_teacher_group(teacher_id, group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    new_teacher = Teachers.query.filter(Teachers.user_id == teacher_id).first()
    old_teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).all()

    if group in old_teacher.group:
        old_teacher.group.remove(group)
        db.session.commit()
    if group not in new_teacher.group:
        new_teacher.group.append(group)
        db.session.commit()
    for time in time_table:
        if time not in new_teacher.time_table:
            new_teacher.time_table.append(time)
            db.session.commit()
        if time in old_teacher.time_table:
            old_teacher.time_table.remove(time)
            db.session.commit()
    Groups.query.filter(Groups.id == group_id).update({
        "teacher_id": new_teacher.id
    })
    db.session.commit()
    return jsonify({
        "msg": "O'qtuvchi o'zgartirildi",
        "success": True
    })


@app.route(f'{api}/delete_group/<int:group_id>')
@jwt_required()
def delete_group(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    Groups.query.filter(Groups.id == group_id).update({"deleted": True})
    subject = Subjects.query.filter(Subjects.id == group.subject_id).first()
    db.session.commit()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    stduents = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group.id).all()
    time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).all()
    for st in stduents:
        st.group.remove(group)
        db.session.commit()
        st.subject.append(subject)
        db.session.commit()
        for time in time_table:
            if time in st.time_table:
                st.time_table.remove(time)
                db.session.commit()
    for time in time_table:
        print('vaqt', time)
        if time in teacher.time_table:
            print('vaqt', time)
            teacher.time_table.remove(time)
            db.session.commit()
    print(teacher.time_table)
    for time in time_table:
        Group_Room_Week.query.filter(Group_Room_Week.id == time.id).delete()
        db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Guruh o'chirildi"
    })


@app.route(f'{api}/check_time_group/<int:group_id>', methods=['POST'])
@jwt_required()
def check_time_group(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    lessons = get_json_field('lessons')
    gr_errors = ''
    teacher_error = ''
    student_errors = []

    for lesson in lessons:
        startTime = datetime.strptime(lesson['startTime'], "%H:%M")
        endTime = datetime.strptime(lesson['endTime'], "%H:%M")
        teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
        teacher_time_start = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
            contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                            Group_Room_Week.week_id == lesson['selectedDay'].get(
                                                                'id'),
                                                            Group_Room_Week.location_id == group.location_id,
                                                            Group_Room_Week.group_id != group_id).filter(
            and_(Group_Room_Week.start_time <= startTime, Group_Room_Week.end_time >= startTime)).order_by(
            Group_Room_Week.id).first()
        teacher_time_end = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
            contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                            Group_Room_Week.week_id == lesson['selectedDay'].get(
                                                                'id'),
                                                            Group_Room_Week.location_id == group.location_id,
                                                            Group_Room_Week.group_id != group_id).filter(
            and_(Group_Room_Week.start_time <= endTime, Group_Room_Week.end_time >= endTime)).order_by(
            Group_Room_Week.id).first()

        if teacher_time_start and teacher_time_end:
            teacher_error = f"{teacher_time_start.room.name} da soat: '{teacher_time_start.start_time.strftime('%H:%M')} {teacher_time_start.end_time.strftime('%H:%M')}' da {teacher_time_start.group.name} ni darsi bor"
        elif teacher_time_start and not teacher_time_end:

            teacher_error = f"{teacher_time_start.room.name} da soat {teacher_time_start.start_time.strftime('%H:%M')} da {teacher_time_start.group.name} ni darsi boshlangan bo'ladi"

        elif teacher_time_end and not teacher_time_start:

            teacher_error = f"{teacher_time_end.room.name} da soat {teacher_time_end.end_time.strftime('%H:%M')} da {teacher_time_end.group.name} ni darsi davom etayotgan bo'ladi"

        time_table_start = Group_Room_Week.query.filter(Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                        Group_Room_Week.room_id == lesson['selectedRoom'].get('id'),
                                                        Group_Room_Week.group_id != group_id,
                                                        ).filter(
            and_(Group_Room_Week.start_time <= startTime, Group_Room_Week.end_time >= startTime)).order_by(
            Group_Room_Week.id).first()
        time_table_end = Group_Room_Week.query.filter(Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                      Group_Room_Week.room_id == lesson['selectedRoom'].get('id'),
                                                      Group_Room_Week.group_id != group_id,
                                                      ).filter(
            and_(Group_Room_Week.start_time <= endTime, Group_Room_Week.end_time >= endTime)).order_by(
            Group_Room_Week.id).first()

        if time_table_start and time_table_end:
            gr_errors = f"{time_table_start.room.name} da soat: '{time_table_start.start_time.strftime('%H:%M')} {time_table_start.end_time.strftime('%H:%M')}' da {time_table_start.group.name} ni darsi bor"
        elif time_table_start and not time_table_end:

            gr_errors = f"{time_table_start.room.name} da soat {time_table_start.start_time.strftime('%H:%M')} da {time_table_start.group.name} ni darsi boshlanadi"

        elif time_table_end and not time_table_start:

            gr_errors = f"{time_table_end.room.name} da soat {time_table_end.end_time.strftime('%H:%M')} gacha {time_table_end.group.name} ni darsi bo'ladi"

        role = Roles.query.filter(Roles.type_role == "student").first()
        students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
            Groups.id == group_id).all()
        for student in students:
            student_group_start = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                     Group_Room_Week.room_id == lesson['selectedRoom'].get('id'),
                                                     Group_Room_Week.group_id != group_id).filter(
                and_(Group_Room_Week.start_time <= startTime, Group_Room_Week.end_time >= startTime)).first()
            student_group_end = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                contains_eager(
                    Group_Room_Week.student)).filter(Students.id == student.id,
                                                     Group_Room_Week.week_id == lesson['selectedDay'].get('id'),
                                                     Group_Room_Week.room_id == lesson['selectedRoom'].get('id'),
                                                     Group_Room_Week.group_id != group_id).filter(
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
                "subjects": [],
                "photo_profile": student.user.photo_profile,
                "color": "green",
                "error": False,
                "shift": ""
            }
            if student_group_start and student_group_end:

                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: '{student_group_start.start_time.strftime('%H:%M')} dan " \
                               f"{student_group_end.end_time.strftime('%H:%M')}' gacha {student_group_start.group.name} da darsi bor"

            elif student_group_start and not student_group_end:

                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{student_group_start.week.name} da soat: {student_group_start.start_time.strftime('%H:%M')} " \
                               f"da {student_group_start.group.name} da darsi boshlangan bo'ladi"

            elif student_group_end and not student_group_start:
                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{student_group_end.week.name} da soat: {student_group_end.end_time.strftime('%H:%M')} " \
                               f"da {student_group_end.group.name} da darsi davom etayotgan bo'ladi"
            student_errors.append(info)

    filtered_students = remove_items_create_group(student_errors)
    return jsonify({
        "success": True,
        "students": filtered_students,
        "group": gr_errors,
        "teacher": teacher_error

    })


@app.route(f'{api}/change_time_group/<int:group_id>', methods=["POST"])
@jwt_required()
def change_time_group(group_id):
    lessons = get_json_field('lessons')

    group = Groups.query.filter(Groups.id == group_id).first()
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).all()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    group_time_table_get = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).all()
    for student in students:
        for time_get in group_time_table_get:
            if time_get in student.time_table:
                student.time_table.remove(time_get)
                db.session.commit()
    for time_get in group_time_table_get:
        if time_get in teacher.time_table:
            teacher.time_table.remove(time_get)
            db.session.commit()
    for time_get in group_time_table_get:
        db.session.delete(time_get)
        db.session.commit()
    for lesson in lessons:
        start_time = datetime.strptime(lesson['startTime'], "%H:%M")
        end_time = datetime.strptime(lesson['endTime'], "%H:%M")
        add = Group_Room_Week(week_id=lesson['selectedDay'].get('id'), room_id=lesson['selectedRoom'].get('id'),
                              start_time=start_time, end_time=end_time, group_id=group_id,
                              location_id=group.location_id)
        db.session.add(add)
        db.session.commit()
        students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
            Groups.id == group_id).all()
        for student in students:
            student_get = Students.query.filter(Students.id == student.id).first()
            student_get.time_table.append(add)
            db.session.commit()

        teacher.time_table.append(add)
        db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Guruh dars vaqtlari o'zgartirildi"
    })


@app.route(f'{api}/check_teacher_time/<int:group_id>', methods=['GET'])
@jwt_required()
def check_teacher_time(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()

    time_table_group = Group_Room_Week.query.filter(Group_Room_Week.group_id == group_id).all()
    teachers = db.session.query(Teachers).join(Teachers.locations).options(contains_eager(Teachers.locations)).filter(
        Locations.id == group.location_id, Teachers.id != group.teacher_id).join(Teachers.subject).options(
        contains_eager(Teachers.subject)).filter(Subjects.id == group.subject_id).order_by(Teachers.id).all()
    role_teacher = Roles.query.filter(Roles.type_role == "teacher").first()
    teacher_errors = []
    for teacher in teachers:
        for time in time_table_group:
            teacher_time_start = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
                contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                                Group_Room_Week.week_id == time.week_id,
                                                                Group_Room_Week.location_id == group.location_id,
                                                                Group_Room_Week.group_id != group_id).filter(
                and_(Group_Room_Week.start_time <= time.start_time,
                     Group_Room_Week.end_time >= time.start_time)).first()
            teacher_time_end = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
                contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                                Group_Room_Week.location_id == group.location_id,
                                                                Group_Room_Week.week_id == time.week_id,
                                                                Group_Room_Week.group_id != group_id).filter(
                and_(Group_Room_Week.start_time <= time.end_time,
                     Group_Room_Week.end_time >= time.end_time)).first()
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
                info['color'] = 'red'
                info["error"] = True
                info[
                    "shift"] = f"{teacher_time_start.week.name} da soat: '{teacher_time_start.start_time.strftime('%H:%M')} dan " \
                               f"{teacher_time_end.end_time.strftime('%H:%M')}' gacha {teacher_time_end.group.name} da darsi bor"
            elif teacher_time_start and not teacher_time_end:

                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{teacher_time_start.week.name} da soat: {teacher_time_start.start_time.strftime('%H:%M')} " \
                               f"da {teacher_time_start.group.name} da darsi bor"
            elif teacher_time_end and not teacher_time_start:

                info["color"] = "red"
                info["error"] = True
                info[
                    "shift"] = f"{teacher_time_end.week.name} da soat: {teacher_time_end.start_time.strftime('%H:%M')} " \
                               f"da {teacher_time_end.group.name} da darsi davom etayotgan bo'ladi"
            teacher_errors.append(info)
    filtered_teachers = remove_items_create_group(teacher_errors)

    return jsonify({
        "success": True,
        "teachers": filtered_teachers
    })


@app.route(f'{api}/delete_time_table/<int:time_id>')
@jwt_required()
def delete_time_table(time_id):
    time_table = Group_Room_Week.query.filter(Group_Room_Week.id == time_id).first()
    group = Groups.query.filter(Groups.id == time_table.group_id).first()
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group.id).all()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    if time_table in group.time_table:
        group.time_table.remove(time_table)
        db.session.commit()
    if time_table in teacher.time_table:
        teacher.time_table.remove(time_table)
        db.session.commit()
    for st in students:
        if time_table in st.time_table:
            st.time_table.remove(time_table)
            db.session.commit()
    room = Rooms.query.filter(Rooms.id == time_table.room_id).first()
    week_day = Week.query.filter(Week.id == time_table.week_id).first()
    if time_table in room.time_table:
        room.time_table.remove(time_table)
        db.session.commit()
    if time_table in week_day.time_table:
        week_day.time_table.remove(time_table)
        db.session.commit()
    db.session.delete(time_table)
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Dars kuni o'chirildi"
    })
