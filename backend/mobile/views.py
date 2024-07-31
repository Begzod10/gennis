import os
from datetime import datetime

from flask_jwt_extended import create_access_token, get_jwt_identity, create_refresh_token, \
    unset_jwt_cookies
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app import app, or_, api, db, jsonify, contains_eager, request, desc, extract
# from backend.book.utils import handle_get_request, handle_post_request, get_observations_for_year
from backend.functions.debt_salary_update import staff_salary_update
from backend.functions.small_info import checkFile, user_photo_folder
from backend.functions.utils import find_calendar_date, get_json_field
from backend.functions.utils import refresh_age, iterate_models, update_salary
from backend.group.class_model import Group_Functions
from backend.group.models import AttendanceDays, Attendance
from backend.models.models import Groups, Students, SubjectLevels, \
    AttendanceHistoryStudent, Group_Room_Week, Week, Roles, CertificateLinks, LessonPlanStudents
from backend.models.models import LessonPlan, ObservationInfo, ObservationOptions, TeacherObservationDay, \
    TeacherObservation, CalendarDay
from backend.models.models import PhoneList, Contract_Students
from backend.models.models import Subjects
from backend.models.models import Teachers, TeacherSalary, StaffSalary, Staff, CalendarMonth, Users, CalendarYear, \
    TeacherBlackSalary
from backend.student.class_model import Student_Functions


@app.route(f"{api}/mobile/refresh", methods=["POST"])
@jwt_required(refresh=True)
def mobile_refresh():
    """
    refresh jwt token
    :return:
    """

    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    username_sign = Users.query.filter_by(user_id=identity).first()
    role = Roles.query.filter(Roles.id == username_sign.role_id).first()
    return jsonify({
        "username": username_sign.username,
        "surname": username_sign.surname.title(),
        "name": username_sign.name.title(),
        "id": username_sign.id,
        "access_token": access_token,
        "role": role.role,
        "profile_photo": username_sign.photo_profile,
        "location_id": username_sign.location_id,
        "observer": username_sign.observer
    })


@app.route(f'{api}/mobile/login2', methods=['POST', 'GET'])
def mobile_login2():
    """
    login function
    create token
    :return: logged User datas
    """
    year = datetime.strptime("2024", "%Y")
    month = datetime.strptime("2024-03", "%Y-%m")
    calendar_year = CalendarYear.query.filter(CalendarYear.date == year).first()
    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == month).first()
    if request.method == "POST":
        username = get_json_field('username')
        password = get_json_field('password')
        username_sign = Users.query.filter_by(username=username).first()
        if username_sign and check_password_hash(username_sign.password, password):
            role = Roles.query.filter(Roles.id == username_sign.role_id).first()
            access_token = create_access_token(identity=username_sign.user_id)
            refresh_age(username_sign.id)
            class_status = False
            if role.type_role == "student" or role.type_role == "teacher" or role.type_role == "methodist":
                class_status = True
            return jsonify({
                'class': class_status,
                "access_token": access_token,
                "refresh_token": create_refresh_token(identity=username_sign.user_id),
                "data": {
                    "username": username_sign.username,
                    "surname": username_sign.surname.title(),
                    "name": username_sign.name.title(),
                    "id": username_sign.id,
                    "role": role.role,
                    "location_id": username_sign.location_id,
                    "access_token": access_token,
                    "refresh_token": create_refresh_token(identity=username_sign.user_id),
                },
                "success": True
            })
        else:
            return jsonify({
                "success": False,
                "msg": "Username yoki parol noturg'i"
            })


@app.route(f"{api}/mobile/logout", methods=["POST"])
def mobile_logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route(f'{api}/mobile/my_groups/<int:user_id>', methods=['POST', 'GET'])
@jwt_required()
def mobile_my_groups(user_id):
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


@app.route(f'{api}/mobile/group_profile/<int:group_id>')
@jwt_required()
def mobile_group_profile(group_id):
    group = Groups.query.filter_by(id=group_id).first()
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).order_by(Students.id).all()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    data = {}
    levels = SubjectLevels.query.filter(SubjectLevels.subject_id == group.subject_id).filter(
        or_(SubjectLevels.disabled == False, SubjectLevels.disabled == None)).order_by(SubjectLevels.id).all()
    level = ''
    if group.level and group.level.name:
        level = group.level.name
    data["information"] = {
        "groupName": {
            "name": "Gruppa nomi",
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
            "name": "Gruppa narxi",
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
        "isTime": is_time
    })


@app.route(f'{api}/mobile/lesson_plan_list/<int:group_id>', defaults={"date": None})
@app.route(f'{api}/mobile/lesson_plan_list/<int:group_id>/<date>')
@jwt_required()
def mobile_lesson_plan_list(group_id, date):
    days_list = []
    month_list = []
    years_list = []
    plan_list = LessonPlan.query.filter(LessonPlan.group_id == group_id).order_by(LessonPlan.id).all()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    if date:
        date = datetime.strptime(date, "%Y-%m")
    else:
        date = calendar_month.date

    plan_list_month = LessonPlan.query.filter(
        extract('month', LessonPlan.date) == int(date.strftime("%m")),
        extract('year', LessonPlan.date) == int(date.strftime("%Y")), LessonPlan.group_id == group_id).all()
    for data in plan_list_month:
        days_list.append(data.date.strftime("%d"))
    days_list.sort()
    for plan in plan_list:
        if plan.date:
            month_list.append(plan.date.strftime("%m"))
            years_list.append(plan.date.strftime("%Y"))
    month_list = list(dict.fromkeys(month_list))
    years_list = list(dict.fromkeys(years_list))
    month_list.sort()
    years_list.sort()
    return jsonify({
        "month_list": month_list,
        "years_list": years_list,
        "month": date.strftime("%m"),
        "year": date.strftime("%Y"),
        "days": days_list
    })


@app.route(f'{api}/mobile/lesson_plan/<int:plan_id>', methods=['GET', 'POST'])
@jwt_required()
def mobile_lesson_plan(plan_id):
    lesson_plan_get = LessonPlan.query.filter(LessonPlan.id == plan_id).first()
    if request.method == "POST":
        objective = get_json_field('objective')
        main_lesson = get_json_field('main_lesson')
        homework = get_json_field('homework')
        assessment = get_json_field('assessment')
        activities = get_json_field('activities')
        student_id_list = get_json_field("students")
        resources = get_json_field("resources")
        lesson_plan_get.objective = objective
        lesson_plan_get.homework = homework
        lesson_plan_get.assessment = assessment
        lesson_plan_get.main_lesson = main_lesson
        lesson_plan_get.activities = activities
        lesson_plan_get.resources = resources
        db.session.commit()
        for student in student_id_list:
            info = {
                "comment": student['comment'],
                "student_id": student['student']['id'],
                "lesson_plan_id": plan_id
            }
            student_add = LessonPlanStudents.query.filter(LessonPlanStudents.lesson_plan_id == plan_id,
                                                          LessonPlanStudents.student_id == student['student'][
                                                              'id']).first()
            if not student_add:
                student_add = LessonPlanStudents(**info)
                student_add.add()
            else:
                student_add.comment = student['comment']
                db.session.commit()
        return jsonify({
            "success": True,
            "msg": "Darslik jadvali tuzildi",
            "lesson_plan": lesson_plan_get.convert_json()
        })
    else:
        return jsonify({
            "lesson_plan": lesson_plan_get.convert_json()
        })


@app.route(f'{api}/mobile/groups_to_observe')
@jwt_required()
def mobile_groups_to_observe():
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    current_date = datetime.now()
    week_day_name = current_date.strftime("%A")
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    get_week_day = Week.query.filter(Week.eng_name == week_day_name,
                                     Week.location_id == user.location_id).first()
    groups = Groups.query.join(Groups.time_table).filter(
        Group_Room_Week.week_id == get_week_day.id,
        # Group_Room_Week.week_id == 8,
        Groups.status == True,
        Groups.location_id == user.location_id,
        Groups.teacher_id != teacher.id,
    ).filter(or_(Groups.deleted == False, Groups.deleted == None)).order_by(Groups.id).all()
    return jsonify({
        "groups": iterate_models(groups, entire=True)
    })


@app.route(f'{api}/mobile/observe_info')
@jwt_required()
def mobile_observe_info():
    # info = [
    #     {
    #         "title": "Teacher follows her or his lesson plan"
    #     },
    #     {
    #         "title": "Teacher is actively circulating in the room"
    #     },
    #     {
    #         "title": "Teacher uses feedback to encourage critical thinking"
    #     },
    #     {
    #         "title": "Students are collaborating with each other and engaged in"
    #     },
    #     {
    #         "title": "Teacher talking time is 1/3"
    #     },
    #     {
    #         "title": "Teacher uses a variety of media and resources for learning"
    #     },
    #     {
    #         "title": "Teacher uses different approach of method"
    #     },
    #     {
    #         "title": "Teacher has ready made materials for the lesson"
    #     },
    #     {
    #         "title": "Lesson objective is present and communicated to students"
    #     }
    # ]
    # for item in info:
    #     if not ObservationInfo.query.filter(ObservationInfo.title == item['title']).first():
    #         add_observation = ObservationInfo(**item)
    #         add_observation.add()
    #
    # options = [
    #     {
    #         "name": "Missing",
    #         "value": 1
    #     },
    #     {
    #         "name": "Done but poorly",
    #         "value": 2
    #     },
    #     {
    #         "name": "Acceptable",
    #         "value": 3
    #     },
    #     {
    #         "name": "Sample for others",
    #         "value": 4
    #     },
    # ]
    # for item in options:
    #     if not ObservationOptions.query.filter(ObservationOptions.name == item['name']).first():
    #         add_observation_options = ObservationOptions(**item)
    #         add_observation_options.add()
    observations = ObservationInfo.query.order_by(ObservationInfo.id).all()
    options = ObservationOptions.query.order_by(ObservationOptions.id).all()
    return jsonify({
        "observations": iterate_models(observations),
        "options": iterate_models(options)
    })


@app.route(f'{api}/mobile/teacher_observe/<int:group_id>', methods=['POST', 'GET'])
@jwt_required()
def mobile_teacher_observe(group_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    identity = get_jwt_identity()
    user = Users.query.filter_by(user_id=identity).first()
    group = Groups.query.filter(Groups.id == group_id).first()
    if request.method == "POST":
        teacher_observation_day = TeacherObservationDay.query.filter(
            TeacherObservationDay.teacher_id == group.teacher_id,
            TeacherObservationDay.calendar_day == calendar_day.id, TeacherObservationDay.group_id == group.id,
        ).first()
        if not teacher_observation_day:
            teacher_observation_day = TeacherObservationDay(teacher_id=group.teacher_id, group_id=group_id,
                                                            calendar_day=calendar_day.id,
                                                            calendar_month=calendar_month.id,
                                                            calendar_year=calendar_year.id, user_id=user.id)
            teacher_observation_day.add()
        result = 0
        for item in get_json_field('list'):
            info = {
                "observation_info_id": item.get('id'),
                "observation_options_id": item.get('value'),
                "comment": item.get('comment'),
                "observation_id": teacher_observation_day.id
            }

            observation_options = ObservationOptions.query.filter(ObservationOptions.id == item.get('value')).first()
            result += observation_options.value
            if not TeacherObservation.query.filter(TeacherObservation.observation_info_id == item.get('id'),
                                                   TeacherObservation.observation_id == teacher_observation_day.id
                                                   ).first():
                teacher_observation = TeacherObservation(**info)
                teacher_observation.add()
            else:
                TeacherObservation.query.filter(TeacherObservation.observation_info_id == item.get('id'),
                                                TeacherObservation.observation_id == teacher_observation_day.id).update(
                    {
                        "observation_options_id": item.get('value'),
                        "comment": item.get('comment')
                    })
                db.session.commit()
        observation_infos = ObservationInfo.query.count()
        result = round(result / observation_infos)
        teacher_observation_day.average = result
        db.session.commit()
        return jsonify({
            "msg": "Teacher has been observed",
            "success": True
        })


@app.route(f'{api}/mobile/observed_group/<int:group_id>', defaults={"date": None})
@app.route(f'{api}/mobile/observed_group/<int:group_id>/<date>')
@jwt_required()
def mobile_observed_group(group_id, date):
    try:
        group = Groups.query.filter(Groups.id == group_id).first()

        days_list = []
        month_list = []
        years_list = []
        calendar_year, calendar_month, calendar_day = find_calendar_date()
        if date:
            calendar_month = datetime.strptime(date, "%Y-%m")
            calendar_month = CalendarMonth.query.filter(CalendarMonth.date == calendar_month).first()
        else:
            calendar_month = calendar_month
        teacher_observation_all = TeacherObservationDay.query.filter(
            TeacherObservationDay.teacher_id == group.teacher_id,

            TeacherObservationDay.group_id == group_id).order_by(
            TeacherObservationDay.id).all()
        teacher_observation = TeacherObservationDay.query.filter(TeacherObservationDay.teacher_id == group.teacher_id,
                                                                 TeacherObservationDay.calendar_month == calendar_month.id,
                                                                 TeacherObservationDay.group_id == group_id).order_by(
            TeacherObservationDay.id).all()

        for data in teacher_observation:
            days_list.append(data.day.date.strftime("%d"))
        days_list.sort()

        for plan in teacher_observation_all:
            if plan.calendar_month:
                month_list.append(plan.month.date.strftime("%m"))
                years_list.append(plan.month.date.strftime("%Y"))

        month_list = list(dict.fromkeys(month_list))
        years_list = list(dict.fromkeys(years_list))
        month_list.sort()
        years_list.sort()

        return jsonify({
            "month_list": month_list,
            "years_list": years_list,
            "month": calendar_month.date.strftime("%m") if month_list[
                                                               len(month_list) - 1] == calendar_month.date.strftime(
                "%m") else month_list[len(month_list) - 1],
            "year": calendar_month.date.strftime("%Y"),
            "days": days_list
        })
    except IndexError:
        return jsonify({
            "msg": "O'qtuvchi hali baholanmagan",
            "success": False
        })


@app.route(f'{api}/mobile/observed_group_info/<int:group_id>', methods=["POST"])
@jwt_required()
def mobile_observed_group_info(group_id):
    day = get_json_field('day')
    month = get_json_field('month')
    year = get_json_field('year')
    date = datetime.strptime(year + "-" + month + "-" + day, "%Y-%m-%d")
    calendar_day = CalendarDay.query.filter(CalendarDay.date == date).first()
    observation_list = []
    observation_options = ObservationOptions.query.order_by(ObservationOptions.id).all()
    observation_infos = ObservationInfo.query.order_by(ObservationInfo.id).all()
    average = 0
    observer = {
        "name": "",
        "surname": ""
    }
    if calendar_day:
        teacher_observation_day = TeacherObservationDay.query.filter(
            TeacherObservationDay.calendar_day == calendar_day.id, TeacherObservationDay.group_id == group_id).first()
        average = teacher_observation_day.average
        observer['name'] = teacher_observation_day.user.name if teacher_observation_day else ""
        observer['surname'] = teacher_observation_day.user.surname if teacher_observation_day else ""
        for item in observation_infos:
            teacher_observations = TeacherObservation.query.filter(
                TeacherObservation.observation_id == teacher_observation_day.id,
                TeacherObservation.observation_info_id == item.id
            ).first()
            info = {
                "title": item.title,
                "values": [],
                "comment": teacher_observations.comment
            }

            for option in observation_options:
                teacher_observations = TeacherObservation.query.filter(
                    TeacherObservation.observation_id == teacher_observation_day.id,
                    TeacherObservation.observation_options_id == option.id,
                    TeacherObservation.observation_info_id == item.id
                ).first()
                info["values"].append({
                    "name": option.name,
                    "value": teacher_observations.observation_option.value if teacher_observations and teacher_observations.observation_option else "",

                })
            observation_list.append(info)
    return jsonify({
        "info": observation_list,
        "observation_options": iterate_models(observation_options),
        "average": average,
        "observer": observer
    })


# @app.route(f'{api}/mobile/teacher_observe/<int:teacher_id>/', defaults={"group_id": None}, methods=['POST', 'GET'])
# @app.route(f'{api}/mobile/teacher_observe/<int:teacher_id>/<int:group_id>', methods=['POST', 'GET'])
# @jwt_required()
# def teacher_observe(teacher_id, group_id):
#     calendar_year, calendar_month, calendar_day = find_calendar_date()
#     identity = get_jwt_identity()
#     user = Users.query.filter_by(user_id=identity).first()
#     if request.method == "POST":
#         if group_id:
#             return handle_post_request(group_id, teacher_id, calendar_day, calendar_year, calendar_month, user)
#         else:
#             year = get_json_field('year')
#             return get_observations_for_year(year, teacher_id)
#     else:
#
#         return handle_get_request(group_id, teacher_id, calendar_year, calendar_month)


@app.route(f'{api}/mobile/change_student_info/<int:user_id>', methods=['POST'])
@jwt_required()
def mobile_change_student_info(user_id):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    json = request.get_json()
    student = Students.query.filter(Students.user_id == user_id).first()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()

    # role = json['role']
    get_role = Roles.query.filter(Roles.id == user.role_id).first()

    if get_role.type_role == "admin" or get_role.type_role == "director":

        if not student:
            type = json['type']
            if type == "info":
                user = Users.query.filter(Users.id == user_id).first()
                Users.query.filter(Users.id == user_id).update({
                    "username": json['username'],
                    "name": json['name'],
                    "surname": json['surname'],
                    "father_name": json['fatherName'],
                    "born_day": json['birthDay'],
                    "born_month": json['birthMonth'],
                    "born_year": json['birthYear']
                })
                db.session.commit()
                age = datetime.now().year - user.born_year
                Users.query.filter(Users.id == user_id).update({
                    "age": age
                })
                db.session.commit()

                for phone in user.phone:
                    if phone.personal:
                        del_phone = PhoneList.query.filter(PhoneList.user_id == phone.user_id).first()
                        db.session.delete(del_phone)
                        db.session.commit()

                add = PhoneList(phone=json['phone'], user_id=user_id, personal=True)
                db.session.add(add)
                db.session.commit()
                if teacher:
                    Teachers.query.filter(Teachers.user_id == user_id).update({
                        "table_color": json['color']
                    })
                    db.session.commit()
                return jsonify({
                    "success": True,
                    "msg": "Ma'lumotlar o'zgartirildi"
                })
            else:
                password = json['password']
                hash = generate_password_hash(password, method='sha256')
                Users.query.filter(Users.id == user_id).update({'password': hash})
                db.session.commit()
                return jsonify({
                    "success": True,
                    "msg": "Parol o'zgartirildi"
                })
        else:
            type = json['type']
            if type == "info":
                user = Users.query.filter(Users.id == user_id).first()
                Users.query.filter(Users.id == user_id).update({
                    "username": json['username'],
                    "name": json['name'],
                    "surname": json['surname'],
                    "father_name": json['fatherName'],
                    "born_day": json['birthDay'],
                    "born_month": json['birthMonth'],
                    "born_year": json['birthYear'],
                    "comment": json['comment']
                })
                db.session.commit()
                age = datetime.now().year - user.born_year
                Users.query.filter(Users.id == user_id).update({
                    "age": age
                })
                db.session.commit()
                morning_shift = None
                night_shift = None
                time = json['shift']

                if time == "1-smen":
                    morning_shift = True
                elif time == "2-smen":
                    night_shift = True
                Students.query.filter(Students.user_id == user_id).update({
                    "morning_shift": morning_shift,
                    "night_shift": night_shift
                })
                db.session.commit()
                for phone in user.phone:
                    if phone.personal:
                        del_phone = PhoneList.query.filter(PhoneList.user_id == phone.user_id).first()
                        db.session.delete(del_phone)
                        db.session.commit()

                add = PhoneList(phone=json['phone'], user_id=user_id, personal=True)
                db.session.add(add)
                db.session.commit()

                for phone in user.phone:
                    if phone.parent:
                        del_phone = PhoneList.query.filter(PhoneList.user_id == phone.user_id).first()
                        db.session.delete(del_phone)
                        db.session.commit()

                add = PhoneList(phone=json['parentPhone'], user_id=user_id, parent=True)
                db.session.add(add)
                db.session.commit()

                subjects = json['selectedSubjects']
                subjects_list = []
                if subjects:
                    student = Students.query.filter(Students.user_id == user_id).first()
                    # for sub in subjects:
                    #     subjects_list.append(sub['id'])
                    #     subject = Subjects.query.filter(Subjects.id == sub['id']).first()
                    #     if student.group:
                    #         student_group = db.session.query(Students).join(Students.group).options(
                    #             contains_eager(Students.group)).filter(
                    #             Groups.subject_id == sub['id']).first()
                    #         if student_group:
                    #             return jsonify({
                    #                 "found": True,
                    #                 "msg": f"Studentni bu {subject.name} guruh ochilgan!"
                    #             })
                    while student.subject:
                        for sub in student.subject:
                            student.subject.remove(sub)
                            db.session.commit()
                    for sub in subjects:
                        subject = Subjects.query.filter(Subjects.id == sub['id']).first()
                        student.subject.append(subject)
                        db.session.commit()
                else:
                    while student.subject:
                        for sub in student.subject:
                            student.subject.remove(sub)
                            db.session.commit()
                return jsonify({
                    "success": True,
                    "msg": "Student ma'lumotlari o'zgartirildi"
                })
            else:
                password = json['password']
                hash = generate_password_hash(password, method='sha256')
                Users.query.filter(Users.id == user_id).update({'password': hash})
                db.session.commit()

            return jsonify({
                "success": True,
                "msg": "Student paroli o'zgartirildi"
            })
    else:
        type = json['type']
        if type == "info":
            Users.query.filter(Users.id == user_id).update({
                "username": json['username']
            })
            db.session.commit()
            return jsonify({
                "success": True,
                "msg": "User ma'lumoti o'zgartirildi o'zgartirildi"
            })
        else:
            password = json['password']
            hash = generate_password_hash(password, method='sha256')
            Users.query.filter(Users.id == user_id).update({'password': hash})
            db.session.commit()

            return jsonify({
                "success": True,
                "msg": "User paroli o'zgartirildi"
            })


@app.route(f'{api}/mobile/profile/<int:user_id>')
@jwt_required()
def mobile_profile(user_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user_get = Users.query.filter(Users.id == user_id).first()
    student_get = Students.query.filter(Students.user_id == user_id).first()
    teacher_get = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff_get = Staff.query.filter(Staff.user_id == user_id).first()
    director_get = Users.query.filter(Users.id == user_id).first()
    refresh_age(user_get.id)
    contract_yes = False
    salary_status = True
    shift = ""
    role = ''
    group_list = []
    rate_list = []
    links = []
    username = ''
    blocked = False
    subject_list = []
    old_balance = 0
    contract_data = {}
    link = ''
    phone_list = {}
    parent_phone = {}
    type_role = ''
    for tel in user_get.phone:
        if tel.personal:
            phone_list = {
                "name": "Tel raqam",
                "value": tel.phone,
                "order": 5
            }

        if tel.parent:
            parent_phone = {
                "name": "Ota-onasining tel raqam",
                "value": tel.phone,
                "order": 6
            }

    if student_get:
        salary_status = False
        contract_yes = True if student_get.contract_pdf_url and student_get.contract_word_url else False
        type_role = "Student"
        shift = "1-smen" if student_get.morning_shift else "2-smen" if student_get.night_shift else "Hamma vaqt"
        role = Roles.query.filter(Roles.id == user_get.role_id).first()
        group_list = [{"id": gr.id, "nameGroup": gr.name.title(), "teacherImg": ""} for gr in student_get.group]

        current_rates = AttendanceHistoryStudent.query.filter(
            AttendanceHistoryStudent.calendar_year == calendar_year.id,
            AttendanceHistoryStudent.calendar_month == calendar_month.id,
            AttendanceHistoryStudent.student_id == student_get.id).all()

        rate_list = [{"subject": rate.subject.name, "degree": rate.average_ball} for rate in current_rates]

        link = {
            "link": "studentPayment",
            "title": "To'lov",
            "iconClazz": "fa-dollar-sign",
            "listAttendance": "fa-calendar-alt",
            "type": "link"
        }
        links.append(link)
        link2 = {
            "link": "studentAccount",
            "title": "To'lov va Qarzlari",
            "iconClazz": "fa-wallet",
            "type": "link"
        }
        username = student_get.user.username
        links.append(link2)
        link4 = {
            "link": "changeInfo",
            "title": "Ma'lumotlarni o'zgratirish",
            "iconClazz": "fa-pen",
            "type": "link"
        }
        link5 = {
            "link": "studentGroupsAttendance",
            "title": "Student davomatlari",
            "iconClazz": "fa-calendar-alt",
            "type": "link"
        }
        link6 = {
            "link": "changePhoto",
            "title": "Rasmni yangilash",
            "iconClazz": "fa-camera",
            "type": "link"
        }
        links.append(link4)
        links.append(link5)
        links.append(link6)
        link7 = {
            "link": "ballHistory",
            "title": "Oylik baholari",
            "iconClazz": "fas fa-star",
            "type": "link"
        }
        links.append(link7)
        link8 = {
            "link": "groupHistory",
            "title": "Guruhlar tarixi",
            "iconClazz": "fas fa-history",
            "type": "link"
        }
        links.append(link8)
        link9 = {
            "link": "timeTable",
            "title": "Dars Jadvali",
            "iconClazz": "fas fa-user-clock",
            "type": "link"
        }
        links.append(link9)

        if student_get.debtor == 2:
            link3 = {
                "name": "delayDay",
                "title": "Kun uzaytirish",
                "iconClazz": "fa-money-check",
                "type": "btn"
            }
            links.append(link3)
        if student_get.debtor == 1 or student_get.debtor == 2:
            link4 = {
                "name": "paymentExcuse",
                "title": "To'lov Sababi",
                "iconClazz": "fa-file-invoice-dollar",
                "type": "btn"
            }
            links.append(link4)
        blocked = True if student_get.debtor == 4 else False
        subject_list = [{"name": sub.name.title()} for sub in student_get.subject]
        old_balance = student_get.old_debt if student_get.old_debt else student_get.old_money if student_get.old_money else 0
        contract = Contract_Students.query.filter(Contract_Students.student_id == student_get.id).first()

        if contract:
            contract_data = {
                "representative_name": student_get.representative_name,
                "representative_surname": student_get.representative_surname,
                "representative_fatherName": contract.father_name,
                "representative_passportSeries": contract.passport_series,
                "representative_givenTime": contract.given_time,
                "representative_givenPlace": contract.given_place,
                "representative_place": contract.place,
                "ot": contract.created_date.strftime("%Y-%m-%d"),
                "do": contract.expire_date.strftime("%Y-%m-%d")
            }
        user = {
            "id": user_get.id,
            "role": role.role,
            "isSalary": salary_status,
            "photo_profile": user_get.photo_profile,
            "contract_data": contract_data,
            "activeToChange": {
                "username": True,
                "name": True,
                "surname": True,
                "fathersName": True,
                "age": True,
                "phone": True,
                "birth": True,
                "parent_phone": True,
                "subject": True,
                "comment": True,
                "language": True,
                "shift": True
            },
            "username": user_get.username,
            "type_role": type_role,
            "isBlocked": blocked,
            "contract_url": student_get.contract_pdf_url,
            "location_id": user_get.location_id,
            "balance": user_get.balance,
            "info": {
                "name": {
                    "name": "Ism",
                    "value": user_get.name.title(),
                    "order": 1
                },
                "surname": {
                    "name": "Familya",
                    "value": user_get.surname.title(),
                    "order": 2
                },
                "fathersName": {
                    "name": "Otasining Ismi",
                    "value": user_get.father_name.title(),
                    "order": 3
                },
                "age": {
                    "name": "Yosh",
                    "value": user_get.age,
                    "order": 4
                },
                "phone": phone_list,
                "parentPhone": parent_phone,

                "birthDate": {
                    "name": "Tug'ulgan kun",
                    "value": str(user_get.born_year) + "-" + str(user_get.born_month) + "-" + str(user_get.born_day),
                    "order": 7
                },
                "username": {
                    "name": "Foydalanuvchi",
                    "value": username,
                    "order": 0
                },
                "subject": {
                    "name": "Fan",
                    "value": subject_list,
                    "order": 8
                },
                "combined_payment": {
                    "name": "Umumiy summa",
                    "value": student_get.combined_debt,
                    "order": 9
                },
                'balance': {
                    "name": "Hisobi",
                    "value": student_get.user.balance,
                    "order": 10
                },

                # "extra_payment": {
                #     "name": "Qo'chimcha to'lovi",
                #     "value": student_get.extra_payment,
                #     "order": 11
                # },
                'old_debt': {
                    "name": "Eski platforma hisobi",
                    "value": old_balance,
                    "order": 11
                },
                "contract": {
                    "name": "Shartnoma",
                    "value": contract_yes,
                    "order": 12,
                    "type": "icon"
                },
                "shift": {
                    "name": "Smen",
                    "value": shift,
                    "order": 13
                },
                "birthDay": {
                    "name": "Tug'ilgan kun",
                    "value": user_get.born_day,
                    "display": "none"
                },
                "birthMonth": {
                    "name": "Tug'ilgan oy",
                    "value": user_get.born_month,
                    "display": "none"
                },
                "birthYear": {
                    "name": "Tug'ilgan yil",
                    "value": user_get.born_year,
                    "display": "none"
                },

            },

            "rate": rate_list,

            "groups": group_list,
            "subjects": subject_list,
            "links": links,

        }
    else:
        location_list = [loc.id for loc in teacher_get.locations] if teacher_get else []
        if teacher_get:
            salary_status = False
            link = {
                "link": "employeeSalary",
                "title": "To'lov",
                "iconClazz": "fa-dollar-sign",
                "type": "link"
            }
            username = teacher_get.user.username
            role = Roles.query.filter(Roles.id == user_get.role_id).first()

            group_list = [{"id": gr.id, "nameGroup": gr.name.title(), "teacherImg": ""} for gr in teacher_get.group if
                          not gr.deleted]
            type_role = "Teacher"
        location_list = list(dict.fromkeys(location_list))

        if staff_get:
            role = Roles.query.filter(Roles.id == user_get.role_id).first()
            link = {
                "link": "employeeSalary",
                "title": "To'lov",
                "iconClazz": "fa-dollar-sign",
                "type": "link"
            }
            username = staff_get.user.username
            type_role = role.type_role

        if director_get.director:
            role = Roles.query.filter(Roles.id == user_get.role_id).first()
            link = {
                "link": "employeeSalary",
                "title": "To'lov",
                "iconClazz": "fa-dollar-sign",
                "type": "link"
            }
            username = director_get.username
            type_role = "Director"
        user = {
            "isSalary": salary_status,
            "id": user_get.id,
            "role": role.role,
            "photo_profile": user_get.photo_profile,
            "activeToChange": {
                "username": True,
                "name": True,
                "surname": True,
                "fathersName": True,
                "age": True,
                "phone": True,
                "birth": True,
                "comment": True,
                "language": True,
                "color": True
            },
            "username": user_get.username,
            "type_role": type_role,
            "location_id": user_get.location_id,
            "info": {
                "name": {
                    "name": "Ism",
                    "value": user_get.name.title(),
                    "order": 1
                },
                "surname": {
                    "name": "Familya",
                    "value": user_get.surname.title(),
                    "order": 2
                },
                "fathersName": {
                    "name": "Otasining Ismi",
                    "value": user_get.father_name,
                    "order": 3
                },
                "age": {
                    "name": "Yosh",
                    "value": user_get.age,
                    "order": 4
                },
                "phone": phone_list,

                "birthDate": {
                    "name": "Tug'ulgan kun",
                    "value": str(user_get.born_year) + "-" + str(user_get.born_month) + "-" + str(user_get.born_day),
                    "order": 7
                },
                "username": {
                    "name": "Foydalanuvchi",
                    "value": username,
                    "order": 0
                },

                "birthDay": {
                    "name": "Tug'ilgan kun",
                    "value": user_get.born_day,
                    "display": "none"
                },
                "birthMonth": {
                    "name": "Tug'ilgan oy",
                    "value": user_get.born_month,
                    "display": "none"
                },
                "birthYear": {
                    "name": "Tug'ilgan yil",
                    "value": user_get.born_year,
                    "display": "none"
                },

            },

            "links": [
                {
                    "link": "changeInfo",
                    "title": "Ma'lumotlarni o'zgratirish",
                    "iconClazz": "fa-pen",
                    "type": "link"
                },
                link,
                {
                    "link": "changePhoto",
                    "title": "Rasmni yangilash",
                    "iconClazz": "fa-camera",
                    "type": "link"
                },
                {
                    "link": "timeTable",
                    "title": "Dars Jadvali",
                    "iconClazz": "fas fa-user-clock",
                    "type": "link"
                }
            ],
            "location_list": location_list,
            "groups": group_list

        }
    if student_get:
        st_functions = Student_Functions(student_id=student_get.id)
        st_functions.filter_charity()
        st_functions.update_debt()
        st_functions.update_balance()
    if teacher_get:
        update_salary(user_id)
    return jsonify({
        "user": user
    })


@app.route(f'{api}/mobile/teacher_salary/<int:user_id>/<int:location_id>')
@jwt_required()
def mobile_teacher_salary(user_id, location_id):
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


@app.route(f"{api}/mobile/update_photo_profile/<int:user_id>", methods=["POST"])
@jwt_required()
def mobile_update_photo_profile(user_id):
    photo = request.files['file']
    app.config['UPLOAD_FOLDER'] = user_photo_folder()
    user = Users.query.filter(Users.id == user_id).first()
    url = ""

    if photo and checkFile(photo.filename):
        if os.path.exists(f'frontend/build{user.photo_profile}'):
            os.remove(f'frontend/build{user.photo_profile}')
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "img_folder" + "/" + photo_filename

        Users.query.filter(Users.id == user_id).update({
            "photo_profile": url
        })
        db.session.commit()
    # user_img = Users.query.filter(Users.id == user_id).first()
    # files = {'upload_file': open(f'frontend/build/{user_img.photo_profile}', 'rb')}
    # headers = request.headers
    # bearer = headers.get('Authorization')
    # headers = {'Authorization': f'Bearer {bearer}'}
    # requests.post(
    #     f'{classroom_server}/api/update_photo/{user_img.id}', files=files, headers=headers)
    return jsonify({
        "success": True,
        "msg": "Shaxsiy profil yangilandi",
        "src": url
    })


@app.route(f'{api}/mobile/get_lesson_plan', methods=['POST'])
@jwt_required()
def mobile_get_lesson_plan():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    day = get_json_field('day')
    month = get_json_field('month')
    year = get_json_field('year')
    group_id = get_json_field('group_id')
    date = year + "-" + month + "-" + day
    date = datetime.strptime(date, "%Y-%m-%d")
    status = True if calendar_day.date < date else False
    lesson_plan = LessonPlan.query.filter(LessonPlan.group_id == group_id, LessonPlan.date == date).first()
    return jsonify({
        "lesson_plan": lesson_plan.convert_json(),
        "status": status
    })


@app.route(f'{api}/mobile/change_lesson_plan/<int:plan_id>', methods=['POST'])
@jwt_required()
def mobile_change_lesson_plan(plan_id):
    lesson_plan_get = LessonPlan.query.filter(LessonPlan.id == plan_id).first()

    objective = get_json_field('objective')
    main_lesson = get_json_field('main_lesson')
    homework = get_json_field('homework')
    assessment = get_json_field('assessment')
    activities = get_json_field('activities')
    student_id_list = get_json_field("students")
    resources = get_json_field("resources")
    lesson_plan_get.objective = objective
    lesson_plan_get.homework = homework
    lesson_plan_get.assessment = assessment
    lesson_plan_get.main_lesson = main_lesson
    lesson_plan_get.activities = activities
    lesson_plan_get.resources = resources

    db.session.commit()
    for student in student_id_list:
        info = {
            "comment": student['comment'],
            "student_id": student['student']['id'],
            "lesson_plan_id": plan_id
        }
        student_add = LessonPlanStudents.query.filter(LessonPlanStudents.lesson_plan_id == plan_id,
                                                      LessonPlanStudents.student_id == student['student']['id']).first()
        if not student_add:
            student_add = LessonPlanStudents(**info)
            student_add.add()
        else:
            student_add.comment = student['comment']
            db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Darslik rejasi tuzildi",
        "lesson_plan": lesson_plan_get.convert_json()
    })


@app.route(f'{api}/mobile/student_time_table/<int:group_id>', methods=['POST', "GET"])
@jwt_required()
def mobile_student_time_table(group_id):
    user = Users.query.filter_by(user_id=get_jwt_identity()).first()
    student = Students.query.filter_by(user_id=user.id).first()
    time_tables = []
    for time_table in student.time_table:
        if time_table.group_id == group_id:
            time_tables.append({
                'room': {
                    'id': time_table.room.id,
                    'name': time_table.room.name
                },
                'time': {
                    'day_name': time_table.start_time.strftime("%A"),
                    'day': time_table.start_time.day,
                    'start': f'{time_table.start_time.hour}:{time_table.start_time.minute}',
                    'end': f'{time_table.end_time.hour}:{time_table.end_time.minute}'
                }
            })
    return jsonify({
        "time_table": time_tables,
    })


@app.route(f'{api}/mobile/group_dates2/<int:group_id>')
@jwt_required()
def mobile_group_dates(group_id):
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


@app.route(f'{api}/mobile/student_attendances/<int:group_id>/<month>')
@jwt_required()
def mobile_student_attendances(group_id, month):
    user = Users.query.filter_by(user_id=get_jwt_identity()).first()
    selected_month = datetime.strptime(month, "%Y-%m")
    student = Students.query.filter(Students.user_id == user.id).first()
    time_tables = []
    for time_table in student.time_table:
        if time_table.group_id == group_id:
            time_tables.append({
                'room': {
                    'id': time_table.room.id,
                    'name': time_table.room.name
                },
                'time': {
                    'day_name': time_table.start_time.strftime("%A"),
                    'day': f'{time_table.start_time.day}.{time_table.start_time.month}.{time_table.start_time.year}',
                    'start': f'{time_table.start_time.hour}:{time_table.start_time.minute}',
                    'end': f'{time_table.end_time.hour}:{time_table.end_time.minute}'
                }
            })
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
            "date": present.day.date.strftime("%d")
        }
            for present in student_attendances_present]

        absent_list = [{
            "id": present.id,
            "date": present.day.date.strftime("%d")
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

            },
            'time_table': time_tables

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
            },
            'time_table': time_tables
        })


@app.route(f'{api}/mobile/combined_attendances/<int:group_id>', methods=["POST", "GET"])
@jwt_required()
def mobile_combined_attendances(group_id):
    user = Users.query.filter_by(user_id=get_jwt_identity()).first()
    student = Students.query.filter(Students.user_id == user.id).first()
    st_functions = Student_Functions(student_id=student.id)
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    year_list = []
    month_list = []
    attendance_month = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.student_id == student.id,
    ).order_by(AttendanceHistoryStudent.id).all()
    time_tables = []
    for time_table in student.time_table:
        if time_table.group_id == group_id:
            time_tables.append({
                'room': {
                    'id': time_table.room.id,
                    'name': time_table.room.name
                },
                'time': {
                    'day_name': time_table.start_time.strftime("%A"),
                    'day': time_table.start_time.day,
                    'start': f'{time_table.start_time.hour}:{time_table.start_time.minute}',
                    'end': f'{time_table.end_time.hour}:{time_table.end_time.minute}'
                }
            })
    for attendance in attendance_month:
        year = AttendanceHistoryStudent.query.filter(AttendanceHistoryStudent.student_id == student.id,
                                                     AttendanceHistoryStudent.group_id == group_id,
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

    if request.method == "GET":
        current_month = datetime.now().month
        if len(str(current_month)) == 1:
            current_month = "0" + str(current_month)
        current_year = datetime.now().year
        return jsonify({
            "data": st_functions.attendance_filter_student_one(month=current_month, year=current_year,
                                                               group_id=group_id),
            'info': info,
            'time_table': time_tables
        })
    else:
        year = get_json_field('year')

        month = get_json_field('month')

        return jsonify({
            "data": st_functions.attendance_filter_student(month=month, year=year, group_id=group_id),
            'info': info,
            'time_table': time_tables
        })


@app.route(f'{api}/mobile/student_self_attendances/<int:group_id>', methods=["POST", "GET"])
@jwt_required()
def student_self_attendances(group_id):
    user = Users.query.filter_by(user_id=get_jwt_identity()).first()
    student = Students.query.filter(Students.user_id == user.id).first()
    st_functions = Student_Functions(student_id=student.id)
    if request.method == 'POST':
        year = get_json_field('year')
        month = get_json_field('month')
        data = st_functions.student_self_attendances(year, month, group_id)
        serialized_data = [attendance.to_dict() for attendance in data]
    else:
        current_month = datetime.now().month
        if len(str(current_month)) == 1:
            current_month = "0" + str(current_month)
        current_year = datetime.now().year
        data = st_functions.student_self_attendances(current_year, current_month, group_id)
        serialized_data = [attendance.to_dict() for attendance in data]
    return jsonify({
        'data': serialized_data
    })
