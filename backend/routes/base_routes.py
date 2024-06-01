import requests
from app import app, api, db, jsonify, contains_eager, request, extract
from werkzeug.security import generate_password_hash, check_password_hash
from backend.functions.utils import refresh_age, iterate_models, refreshdatas, hour2, update_salary
from datetime import timedelta
from backend.functions.filters import new_students_filters, teacher_filter, staff_filter, collection, \
    accounting_payments, group_filter, \
    deleted_students_filter, debt_students, deleted_reg_students_filter
import uuid
from backend.student.class_model import Student_Functions
from backend.functions.utils import find_calendar_date, get_json_field, check_exist_id

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, create_refresh_token, \
    unset_jwt_cookies
from backend.models.models import CourseTypes, Students, Users, Staff, \
    PhoneList, Roles, Group_Room_Week, Locations, Professions, Teachers, Subjects, Week, AccountingInfo, Groups, \
    AttendanceHistoryStudent, PaymentTypes, StudentExcuses, SubjectLevels, EducationLanguage, Contract_Students, \
    CalendarYear, StaffSalary, DeletedStudents, GroupReason, TeacherGroupStatistics, CalendarMonth, CalendarDay, \
    Advantages, Link, TeacherData
from datetime import datetime
from pprint import pprint


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')


@app.errorhandler(413)
def img_larger(e):
    return jsonify({
        "success": False,
        "msg": "rasm hajmi kotta"
    })


@app.route('/', methods=['POST', 'GET'])
def index():
    refreshdatas()
    # list = ['Co-working zone', 'Friendly atmosphere', 'Football games in 3 branches', 'Different interesting events',
    #         'Cybersport']
    # for name in list:
    #     advantage = Advantages.query.filter(Advantages.name == name).first()
    #     if not advantage:
    #         add = Advantages(name=name)
    #         db.session.add(add)
    #         db.session.commit()
    # link_names = ['Youtube', 'Telegram', 'Instagram', 'Facebook']
    # for link_name in link_names:
    #     link = Link.query.filter(Link.name == link_name).first()
    #     if not link:
    #         new = Link(name=link_name)
    #         db.session.add(new)
    #         db.session.commit()
    return app.send_static_file("index.html")


@app.route(f'{api}/locations')
def locations():
    locations_list = Locations.query.order_by(Locations.id).all()
    years = CalendarYear.query.order_by(CalendarYear.id).all()

    return jsonify({
        "locations": iterate_models(locations_list)
    })


@app.route(f"{api}/filters/<name>/<int:location_id>/", defaults={"type_filter": None}, methods=["GET"])
@app.route(f"{api}/filters/<name>/<int:location_id>/<type_filter>", methods=["GET"])
@jwt_required()
def filters(name, location_id, type_filter):
    """
    :param type_filter: 
    :param name: filter type
    :param location_id: Location table primary key
    :return: returns filter block
    """

    filter_block = ""
    if name == "newStudents":
        filter_block = new_students_filters()
    if name == "teachers":
        filter_block = teacher_filter()
    if name == "employees":
        filter_block = staff_filter()
    if name == 'groups':
        filter_block = group_filter(location_id)
    if name == "accounting_payment":
        filter_block = accounting_payments(type_filter)
    if name == "collection":
        filter_block = collection()
    if name == "debt_students":
        filter_block = debt_students(location_id)
    if name == "deletedGroupStudents":
        filter_block = deleted_students_filter(location_id)
    if name == "deleted_reg_students":
        filter_block = deleted_reg_students_filter(location_id)

    return jsonify({
        "filters": filter_block,
    })


@app.route(f"{api}/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    refresh jwt token
    :return:
    """

    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    username_sign = Users.query.filter_by(user_id=identity).first()
    role = Roles.query.filter(Roles.id == username_sign.role_id).first() if username_sign else {}

    if username_sign.teacher:
        data = TeacherData.query.filter(TeacherData.teacher_id == username_sign.teacher.id).first()
    else:
        data = None
    return jsonify({
        "username": username_sign.username,
        "surname": username_sign.surname.title(),
        "name": username_sign.name.title(),
        "id": username_sign.id,
        "access_token": access_token,
        "role": role.role if role else "",
        "profile_photo": username_sign.photo_profile,
        "observer": username_sign.observer,
        "location_id": username_sign.location_id,
        "teacher_info": data.convert_json() if data else {}

    })


@app.route(f'{api}/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":

        username = get_json_field('username')
        password = get_json_field('password')
        username_sign = Users.query.filter_by(username=username).first()

        if username_sign and check_password_hash(username_sign.password, password):
            access_token = create_access_token(identity=username)
            # if username_sign.role_id == 5 or username_sign.role_id == 4:
            #     return jsonify({
            #         'class': True,
            #         "access_token": access_token,
            #     })
            role = Roles.query.filter(Roles.id == username_sign.role_id).first()
            refresh_age(username_sign.id)
            return jsonify({
                "data": {
                    "username": username_sign.username,
                    "surname": username_sign.surname.title(),
                    "name": username_sign.name.title(),
                    "id": username_sign.id,
                    "access_token": access_token,
                    "role": role.role,
                    "observer": username_sign.observer,
                    "refresh_token": create_refresh_token(identity=username),
                    "location_id": username_sign.location_id
                },
                "success": True
            })

        else:
            return jsonify({
                "success": False,
                "msg": "Username yoki parol noturg'i"
            })


@app.route(f"{api}/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route(f'{api}/register', methods=['POST', 'GET'])
def register():
    refreshdatas()
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    if request.method == 'POST':
        json_request = request.get_json()

        username = json_request['username']
        username_check = Users.query.filter_by(username=username).first()

        morning_shift = None
        night_shift = None
        time = json_request['time']
        if time == "1-smen":
            morning_shift = True
        elif time == "2-smen":
            night_shift = True

        if username_check:
            return jsonify({
                "message": "Username is already exists",
                "isUsername": True,
                "isError": True
            })

        name = json_request['name']
        surname = json_request['surname']
        fatherName = json_request['fatherName']
        birthDay = int(json_request['birthDay'])
        birthMonth = int(json_request['birthMonth'])
        birthYear = int(json_request['birthYear'])
        phone = json_request['phone']
        phoneParent = json_request['phoneParent']
        confirmPassword = json_request['confirmPassword']
        comment = json_request['comment']
        location = json_request['eduCenLoc']
        studyLang = json_request['studyLang']
        if not studyLang:
            studyLang = "Uz"
        language = EducationLanguage.query.filter_by(id=studyLang).first()
        password = generate_password_hash(confirmPassword, method='sha256')

        if not location:
            location = Locations.query.first()
        location = Locations.query.filter_by(id=location).first()

        a = datetime.today().year
        age = a - birthYear
        users = Users.query.all()

        if len(users) == 0:
            director = True
            role = Roles.query.filter(Roles.type_role == "director").first()
        else:
            director = False
            role = Roles.query.filter(Roles.type_role == "student").first()
        user_id = check_exist_id()
        if username == "monstrCoder" or username == "rimeprogrammer":
            role = Roles.query.filter(Roles.type_role == "programmer").first()
        ball_time = hour2() + timedelta(minutes=-5)
        add = Users(name=name, surname=surname, password=password, education_language=language.id,
                    location_id=location.id, user_id=user_id, username=username, born_day=birthDay,
                    born_month=birthMonth, comment=comment, calendar_day=calendar_day.id, director=director,
                    calendar_month=calendar_month.id, calendar_year=calendar_year.id, role_id=role.id,
                    born_year=birthYear, age=age, father_name=fatherName, balance=0)
        db.session.add(add)

        db.session.commit()
        if director == False and not role.type_role == "programmer":
            student = Students(user_id=add.id, ball_time=ball_time)
            db.session.add(student)
            db.session.commit()

            Students.query.filter(Students.id == student.id).update({
                "morning_shift": morning_shift,
                "night_shift": night_shift,
            })
            db.session.commit()

            selectedSubjects = json_request['selectedSubjects']
            for sub in selectedSubjects:
                subject = Subjects.query.filter_by(name=sub['name']).first()
                student.subject.append(subject)
                db.session.commit()
        add_phone = PhoneList(phone=phone, user_id=add.id, personal=True)
        parent_phone = PhoneList(phone=phoneParent, user_id=add.id, parent=True)
        db.session.add(parent_phone)
        db.session.add(add_phone)
        db.session.commit()
        profession = Professions.query.filter(Professions.name == "programmer").first()
        if role.type_role == "programmer":
            add = Staff(profession_id=profession.id, user_id=add.id)
            db.session.add(add)
            db.session.commit()
        return jsonify({
            "success": True,
            "msg": "Registration was successful"
        })
    if request.method == "GET":
        subjects = Subjects.query.all()
        locations = Locations.query.order_by('id').all()
        languages = EducationLanguage.query.order_by('id').all()
        professions = Professions.query.order_by('id').all()

        data = {}
        subjects_list = [{"id": sub.id, "name": sub.name} for sub in subjects]
        locations_list = [{"id": sub.id, "name": sub.name} for sub in locations]
        languages_list = [{"id": sub.id, "name": sub.name} for sub in languages]
        professions_list = [{"id": sub.id, "name": sub.name} for sub in professions]
        data['subject'] = subjects_list
        data['location'] = locations_list
        data['language'] = languages_list
        data['jobs'] = professions_list
        return jsonify({
            "data": data
        })


@app.route(f'{api}/register_teacher', methods=['POST', 'GET'])
def register_teacher():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    if request.method == "POST":
        get_json = request.get_json()
        username = get_json['username']
        username_check = Users.query.filter_by(username=username).first()
        if username_check:
            return jsonify({
                "message": "Username is already exists",
                "isUsername": True,
                "isError": True,
            })
        name = get_json['name']
        surname = get_json['surname']
        fatherName = get_json['fatherName']
        birthDay = int(get_json['birthDay'])
        birthMonth = int(get_json['birthMonth'])
        birthYear = int(get_json['birthYear'])
        phone = get_json['phone']
        confirmPassword = get_json['confirmPassword']
        location = int(get_json['eduCenLoc'])

        studyLang = get_json['studyLang']
        comment = get_json['comment']
        if not studyLang:
            studyLang = "Uz"
        a = datetime.today().year
        age = a - birthYear
        user_id = check_exist_id()
        if not location:
            location = Locations.query.first()
        hash = generate_password_hash(confirmPassword, method='sha256')
        location = Locations.query.filter_by(id=location).first()
        language = EducationLanguage.query.filter_by(id=studyLang).first()
        role = Roles.query.filter(Roles.type_role == "teacher").first()
        add = Users(name=name, surname=surname, username=username, password=hash,
                    education_language=language.id, born_day=birthDay, born_month=birthMonth,
                    calendar_day=calendar_day.id, role_id=role.id,
                    calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                    born_year=birthYear, location_id=location.id, age=age, user_id=user_id, comment=comment,
                    father_name=fatherName, balance=0)
        db.session.add(add)
        db.session.commit()
        teacher = Teachers(user_id=add.id)
        db.session.add(teacher)
        db.session.commit()
        selectedSubjects = get_json['selectedSubjects']
        for sub in selectedSubjects:
            subject = Subjects.query.filter_by(name=sub['name']).first()
            teacher.subject.append(subject)
            db.session.commit()
        add_phone = PhoneList(phone=phone, user_id=add.id, personal=True)
        db.session.add(add_phone)
        db.session.commit()

        return jsonify({
            "msg": "Registration was successful",
            "success": True
        })


@app.route(f'{api}/register_staff', methods=['POST'])
def register_staff():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    get_json = request.get_json()
    username = get_json['username']
    username_check = Users.query.filter_by(username=username).first()
    if username_check:
        return jsonify({
            "message": "Username is already exists",
            "isUsername": True,
            "isError": True,
        })
    name = get_json['name']
    surname = get_json['surname']
    fatherName = get_json['fatherName']
    birthDay = int(get_json['birthDay'])
    birthMonth = int(get_json['birthMonth'])
    birthYear = int(get_json['birthYear'])
    phone = get_json['phone']
    confirmPassword = get_json['confirmPassword']
    location = get_json['eduCenLoc']
    studyLang = get_json['studyLang']
    comment = get_json['comment']
    if not studyLang:
        studyLang = "Uz"
    if not location:
        location = Locations.query.first()
    a = datetime.today().year
    age = a - birthYear
    user_id = check_exist_id()
    hash = generate_password_hash(confirmPassword, method='sha256')
    location = Locations.query.filter_by(id=location).first()
    language = EducationLanguage.query.filter_by(id=studyLang).first()
    selectedSubjects = get_json['selectedJobs'][0]['name']
    profession = Professions.query.filter_by(name=selectedSubjects).first()
    if selectedSubjects == "Administrator":
        role = Roles.query.filter(Roles.type_role == "admin").first()
    elif selectedSubjects == "Muxarir":
        role = Roles.query.filter(Roles.type_role == "muxarir").first()
    elif selectedSubjects == "Buxgalter":
        role = Roles.query.filter(Roles.type_role == "accountant").first()
    else:
        role = Roles.query.filter(Roles.type_role == "user").first()
    add = Users(name=name, surname=surname, username=username, password=hash,
                education_language=language.id, born_day=birthDay, born_month=birthMonth,
                calendar_day=calendar_day.id, role_id=role.id,
                calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                born_year=birthYear, location_id=location.id, age=age, user_id=user_id, comment=comment,
                father_name=fatherName, balance=0)
    db.session.add(add)
    db.session.commit()
    staff = Staff(user_id=add.id, profession_id=profession.id)
    db.session.add(staff)

    add_phone = PhoneList(user_id=add.id, phone=phone, personal=True)
    db.session.add(add_phone)
    db.session.commit()

    return jsonify({
        "msg": "Registration was successful",
        "success": True
    })


@app.route(f'{api}/my_profile/<int:user_id>')
@jwt_required()
def my_profile(user_id):
    links = []
    refreshdatas()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user = Users.query.filter(Users.id == user_id).first()
    role = Roles.query.filter(Roles.id == user.role_id).first()
    student_get = Students.query.filter(Students.user_id == user.id).first()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    staff = Staff.query.filter(Staff.user_id == user_id).first()

    combined_debt = student_get.combined_debt if student_get and student_get.combined_debt else 0

    subject_list = [{"name": sub.name} for sub in student_get.subject] if student_get and student_get.subject else []
    current_rates = AttendanceHistoryStudent.query.filter(
        AttendanceHistoryStudent.calendar_year == calendar_year.id,
        AttendanceHistoryStudent.calendar_month == calendar_month.id,
        AttendanceHistoryStudent.student_id == student_get.id).all() if student_get else []
    rate_list = [{"subject": rate.subject.name, "degree": rate.average_ball} for rate in current_rates]

    changes = {}
    contract_url = ""
    if not student_get:
        link4 = {
            "link": "changeInfo",
            "title": "Ma'lumotlarni o'zgratirish",
            "iconClazz": "fa-pen",
            "type": "link"
        }
        links.append(link4)
        link6 = {
            "link": "changePhoto",
            "title": "Rasmni yangilash",
            "iconClazz": "fa-camera",
            "type": "link"
        }
        links.append(link6)

    if teacher:
        link = {
            "link": "employeeSalary",
            "title": "To'lov",
            "iconClazz": "fa-dollar-sign",
            "type": "link"
        }
        links.append(link)
    if student_get:
        link2 = {
            "link": "studentAccount",
            "title": "To'lov va Qarzlari",
            "iconClazz": "fa-wallet",
            "type": "link"
        }

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
    if student_get:
        info = {
            "username": True
        }
        contract_url = {"contract_url": student_get.contract_pdf_url}

        changes = info
    if staff or user.director or teacher:
        info = {
            "username": True,
            "name": True,
            "surname": True,
            "fathersName": True,
            "birth": True,
            "phone": True,
            "birthDate": True,
        }
        changes = info
    phone_list = {}
    parent_phone = {}
    for tel in user.phone:
        if tel.parent:
            parent_phone = {
                "name": "Ota-onasining tel raqam",
                "value": tel.phone,
                "order": 6
            }
        elif tel.personal:
            phone_list = {
                "name": "Tel raqam",
                "value": tel.phone,
                "order": 5
            }
    balance = student_get.user.balance if student_get and student_get.user.balance else 0
    combined_payment = {
        "name": "Umumiy summa",
        "value": combined_debt,
        "order": 11
    } if student_get else {}
    balance_info = {
        "name": "Hisobi",
        "value": balance,
        "order": 12
    } if student_get else {}
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": role.role,
        "name": user.name.title(),
        "surname": user.surname.title(),
        "location": user.location_id,
        'profile_photo': user.photo_profile,
        "rate": rate_list,
        "contract_url": contract_url,
        "location_id": user.location_id,
        "balance": user.balance,
        "extraInfo": {
            "username": {
                "name": "Foydalanuvchi",
                "value": user.username,
                "order": 0
            },
            "name": {
                "name": "Ism",
                "value": user.name.title(),
                "order": 1
            },
            "surname": {
                "name": "Familya",
                "value": user.surname.title(),
                "order": 2
            },
            "fathersName": {
                "name": "Otasining Ismi",
                "value": user.father_name.title(),
                "order": 3
            },
            "age": {
                "name": "age",
                "value": user.age,
                "order": 4
            },
            "birthDate": {
                "name": "Tug'ulgan kun",
                "value": str(user.born_year) + "-" + str(user.born_month) + "-" + str(user.born_day),
                "order": 7,
            },
            "birthDay": {
                "name": "Tug'ulgan kun",
                "value": user.born_day,
                "order": 8,
                "display": "none"
            },
            "birthMonth": {
                "name": "Tug'ulgan oy",
                "value": user.born_month,
                "order": 9,
                "display": "none"
            },

            "birthYear": {
                "name": "Tug'ulgan yil",
                "value": user.born_year,
                "order": 10,
                "display": "none"
            },
            "combined_payment": combined_payment,
            'balance': balance_info,
            "phone": phone_list,
            "parentPhone": parent_phone,
            "subjects": subject_list,

        },
        "links": links,

        "activeToChange": changes
    })


@app.route(f'{api}/get_price_course/', methods=['POST'])
@jwt_required()
def get_price_course():
    body = {}
    course_type = int(request.get_json()['course_type'])
    course = CourseTypes.query.filter_by(id=course_type).first()
    body['price'] = course.cost
    return jsonify(body)


@app.route(f'{api}/profile/<int:user_id>')
@jwt_required()
def profile(user_id):
    refreshdatas()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    user_get = Users.query.filter(Users.id == user_id).first()
    student_get = Students.query.filter(Students.user_id == user_id).first()
    teacher_get = Teachers.query.filter(Teachers.user_id == user_id).first()
    if teacher_get:
        deleted_students = DeletedStudents.query.filter(DeletedStudents.teacher_id == teacher_get.id).order_by(
            DeletedStudents.id).all()
        deleted_students_len = DeletedStudents.query.filter(DeletedStudents.teacher_id == teacher_get.id).order_by(
            DeletedStudents.id).count()
        groups = Groups.query.filter(Groups.teacher_id == teacher_get.id).all()
        students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
            Groups.id.in_([gr.id for gr in groups]), ~Students.id.in_([st.id for st in deleted_students])).all()
        teacher_get.total_students = len(students) + deleted_students_len
        db.session.commit()
        group_reasons = GroupReason.query.order_by(GroupReason.id).all()
        month_list = CalendarMonth.query.order_by(CalendarMonth.date).all()

        for month in month_list:
            for reason in group_reasons:
                deleted_students_total = DeletedStudents.query.filter(
                    DeletedStudents.teacher_id == teacher_get.id).join(DeletedStudents.day).filter(
                    extract("month", CalendarDay.date) == int(month.date.strftime("%m")),
                    extract("year", CalendarDay.date) == int(month.date.strftime("%Y"))).count()
                deleted_students_list = DeletedStudents.query.filter(DeletedStudents.teacher_id == teacher_get.id,
                                                                     DeletedStudents.reason_id == reason.id,
                                                                     ).join(DeletedStudents.day).filter(
                    extract("month", CalendarDay.date) == int(month.date.strftime("%m")),
                    extract("year", CalendarDay.date) == int(month.date.strftime("%Y"))).count()
                if deleted_students_total:
                    result = round((deleted_students_list / deleted_students_total) * 100)
                    teacher_statistics = TeacherGroupStatistics.query.filter(
                        TeacherGroupStatistics.reason_id == reason.id,
                        TeacherGroupStatistics.calendar_month == month.id,
                        TeacherGroupStatistics.calendar_year == month.year_id,
                        TeacherGroupStatistics.teacher_id == teacher_get.id).first()
                    if not teacher_statistics:
                        teacher_statistics = TeacherGroupStatistics(
                            reason_id=reason.id,
                            calendar_month=month.id,
                            calendar_year=month.year_id,
                            percentage=result,
                            number_students=deleted_students_list,
                            teacher_id=teacher_get.id)
                        teacher_statistics.add()
                    else:

                        teacher_statistics.number_students = deleted_students_list
                        teacher_statistics.percentage = result
                        db.session.commit()
    staff_get = Staff.query.filter(Staff.user_id == user_id).first()
    director_get = Users.query.filter(Users.id == user_id).first()
    refresh_age(user_get.id)

    salary_status = True
    role = ''
    group_list = []
    links = []
    username = ''
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
            "observer": user_get.observer,
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


@app.route(f'{api}/user_time_table/<int:user_id>/<int:location_id>')
@jwt_required()
def user_time_table(user_id, location_id):
    student = Students.query.filter(Students.user_id == user_id).first()
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()

    table_list = []
    weeks = []

    if student:
        week_days = Week.query.filter(Week.location_id == student.user.location_id).order_by(Week.order).all()
        for week in week_days:
            weeks.append(week.name)
        groups = db.session.query(Groups).join(Groups.student).options(contains_eager(Groups.student)).filter(
            Students.id == student.id).order_by(Groups.id).all()

        for group in groups:
            group_info = {
                "name": group.name,
                "id": group.id,
                "lesson": []
            }
            week_list = []
            for week in week_days:
                info = {
                    "from": "",
                    "to": "",
                    "room": ""
                }
                time_table = db.session.query(Group_Room_Week).join(Group_Room_Week.student).options(
                    contains_eager(Group_Room_Week.student)).filter(Students.id == student.id,
                                                                    Group_Room_Week.week_id == week.id,
                                                                    ).order_by(
                    Group_Room_Week.group_id).first()

                if time_table:
                    info["from"] = time_table.start_time.strftime("%H:%M")
                    info["to"] = time_table.end_time.strftime("%H:%M")
                    info['room'] = time_table.room.name

                week_list.append(info)
                group_info['lesson'] = week_list
            table_list.append(group_info)
    else:
        week_days = Week.query.filter(Week.location_id == location_id).order_by(Week.id).all()
        for week in week_days:
            weeks.append(week.name)
        groups = db.session.query(Groups).join(Groups.teacher).options(contains_eager(Groups.teacher)).filter(
            Teachers.id == teacher.id).order_by(Groups.id).all()
        for group in groups:
            group_info = {
                "name": group.name,
                "id": group.id,
                "lesson": []
            }
            week_list = []
            for week in week_days:
                info = {
                    "from": "",
                    "to": "",
                    "room": ""
                }
                time_table = db.session.query(Group_Room_Week).join(Group_Room_Week.teacher).options(
                    contains_eager(Group_Room_Week.teacher)).filter(Teachers.id == teacher.id,
                                                                    Group_Room_Week.group_id == group.id,
                                                                    Groups.location_id == location_id,
                                                                    Group_Room_Week.week_id == week.id,
                                                                    ).order_by(
                    Group_Room_Week.group_id).first()

                if time_table:
                    info["from"] = time_table.start_time.strftime("%H:%M")
                    info["to"] = time_table.end_time.strftime("%H:%M")
                    info['room'] = time_table.room.name

                week_list.append(info)
                group_info['lesson'] = week_list
            table_list.append(group_info)

    return jsonify({
        "success": True,
        "data": table_list,
        "days": weeks
    })


@app.route(f'{api}/extend_att_date/<int:student_id>', methods=['POST'])
@jwt_required()
def extend_att_date(student_id):
    student = Students.query.filter(Students.user_id == student_id).first()
    reason = get_json_field('reason')
    date = get_json_field('date')
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    result_date = year + '-' + month + '-' + day

    date = datetime.strptime(result_date, "%Y-%m-%d")
    add = StudentExcuses(student_id=student.id, reason=reason, to_date=date)
    db.session.add(add)
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Davomat limit kuni belgilandi"

    })


@app.route(f'{api}/request_get')
def request_get():
    payment_type = PaymentTypes.query.filter(PaymentTypes.name == "cash").first()

    accounting_info = AccountingInfo.query.filter(AccountingInfo.location_id == 3,
                                                  AccountingInfo.payment_type_id == payment_type.id).all()

    response = requests.get("http://176.96.243.157/request_get")

    # subject_list = response.json()['subject_list']
    # for sub in subject_list:
    #     subject = Subjects.query.filter(Subjects.name == sub['name']).first()
    #     if not subject:
    #         if sub['name'] == "Ingliz tili" or sub['name'] == "Rus tili" or sub[
    #             'name'] == "Ingliz tili+mental arifmetika" or sub['name'] == "Rus tili+mental arifmetika":
    #             ball_number = 3
    #         else:
    #             ball_number = 2
    #         subject = Subjects(name=sub['name'], ball_number=ball_number)
    #         db.session.add(subject)
    #         db.session.commit()
    #
    # education_language = response.json()['education_language']
    # for language in education_language:
    #     if language == "Узбекский":
    #         lan = "Uz"
    #     else:
    #         lan = "Rus"
    #     get_language = EducationLanguage.query.filter(EducationLanguage.name == lan).first()
    #     if not get_language:
    #         get_language = EducationLanguage(name=lan)
    #         db.session.add(get_language)
    #         db.session.commit()
    #
    # course_types = response.json()['course_types']
    # for course in course_types:
    #     get_course = CourseTypes.query.filter(CourseTypes.name == course).first()
    #     if not get_course:
    #         get_course = CourseTypes(name=course)
    #         db.session.add(get_course)
    #         db.session.commit()
    #
    # jobs = response.json()['job_list']
    # for job in jobs:
    #
    #     get_job = Professions.query.filter(Professions.name == job).first()
    #     if not get_job:
    #         get_job = Professions(name=job)
    #         db.session.add(get_job)
    #         db.session.commit()

    # student_list = response.json()['student_list']
    # #
    # for student in student_list:
    #     id = uuid.uuid1()
    #     user_id = id.hex[0:15]
    #     role = Roles.query.filter(Roles.student == True).first()
    #     if student['education_language'] == "Узбекский":
    #         language = "Uz"
    #     else:
    #         language = "Rus"
    #     language = EducationLanguage.query.filter(EducationLanguage.name == language).first()
    #     location = Locations.query.filter(Locations.id == student['locations']).first()
    #     if not student['xojakent_admin'] and not student['gazalkent_admin'] and not student['chirchiq_admin'] and not \
    #             student['director']:
    #         user = Users.query.filter(Users.name == student['name'], Users.surname == student['surname'],
    #                                   Users.education_language == language.id, Users.username == student['username'],
    #                                   Users.born_day == student['born_day'], Users.born_month == student['born_month'],
    #                                   Users.born_year == student['year_born'], Users.age == student['age'],
    #                                   Users.calendar_day == calendar_day.id).first()
    #         if not user:
    #             add = Users(name=student['name'], surname=student['surname'], password=student['password'],
    #                         education_language=language.id,
    #                         location_id=location.id, user_id=user_id, username=student['username'],
    #                         born_day=student['born_day'], role_id=role.id,
    #                         born_month=student['born_month'], comment=student['comment'], calendar_day=calendar_day.id,
    #                         calendar_month=calendar_month.id, calendar_year=calendar_year.id,
    #                         born_year=student['year_born'], age=student['age'], father_name=student['otasining_ismi'],
    #                         director=student['director'])
    #             db.session.add(add)
    #             db.session.commit()
    #             subject1 = Subjects.query.filter_by(name=student['subject_1']).first()
    #             subject2 = Subjects.query.filter_by(name=student['subject_2']).first()
    #             subject3 = Subjects.query.filter_by(name=student['subject_3']).first()
    #             student_get = Students(user_id=add.id, old_id=student['id'])
    #             db.session.add(student_get)
    #             db.session.commit()
    #             if subject1:
    #                 student_get.subject.append(subject1)
    #                 db.session.commit()
    #             if subject2:
    #                 student_get.subject.append(subject2)
    #                 db.session.commit()
    #             if subject3:
    #                 student_get.subject.append(subject3)
    #                 db.session.commit()
    #             add_phone = PhoneList(phone=student['phone'], personal=True, user_id=add.id)
    #             db.session.add(add_phone)
    #             db.session.commit()
    #             add_parent_phone = PhoneList(phone=student['parent_phone'], parent=True, user_id=add.id)
    #             db.session.add(add_parent_phone)
    #             db.session.commit()
    #             if student['money'] > 0:
    #                 student_get = Students.query.filter(Students.old_id == student['id']).first()
    #
    #                 Students.query.filter(Students.id == student_get.id).update({
    #                     "old_debt": student['money'],
    #                     "old_money": None
    #                 })
    #                 db.session.commit()
    #                 st_functions = Student_Functions(student_id=student_get.id)
    #                 st_functions.update_debt()
    #                 st_functions.update_extra_payment()
    #                 st_functions.update_balance()
    #             else:
    #                 student_get = Students.query.filter(Students.old_id == student['id']).first()
    #                 Students.query.filter(Students.id == student_get.id).update({
    #                     "old_money": student['money'],
    #                     "old_debt": None
    #                 })
    #                 db.session.commit()
    #                 st_functions = Student_Functions(student_id=student_get.id)
    #                 st_functions.update_debt()
    #                 st_functions.update_extra_payment()
    #                 st_functions.update_balance()
    # language = EducationLanguage.query.first()
    # if student['director']:
    #     role = Roles.query.filter(Roles.director == True).first()
    #     user = Users.query.filter(Users.name == student['name'], Users.surname == student['surname'],
    #                               Users.education_language == language.id, Users.username == student['username'],
    #                               Users.born_day == student['born_day'], Users.born_month == student['born_month'],
    #                               Users.born_year == student['year_born'], Users.age == student['age'],
    #                               Users.calendar_day == calendar_day.id).first()
    #     if not user:
    #         add = Users(name=student['name'], surname=student['surname'], password=student['password'],
    #                     education_language=language.id,
    #                     location_id=student['locations'], user_id=user_id, username=student['username'],
    #                     born_day=student['born_day'], role_id=role.id,
    #                     born_month=student['born_month'], comment=student['comment'], calendar_day=calendar_day.id,
    #                     calendar_month=calendar_month.id, calendar_year=calendar_year.id,
    #                     born_year=student['year_born'], age=student['age'], father_name=student['otasining_ismi'],
    #                     director=student['director'])
    #         db.session.add(add)
    #
    #         db.session.commit()

    #
    # teacher_list = response.json()['teacher_list']
    # for teacher in teacher_list:
    #
    #     id = uuid.uuid1()
    #     user_id = id.hex[0:15]
    #     role = Roles.query.filter(Roles.teacher == True).first()
    #     if teacher['education_language'] == "Узбекский":
    #         language = "Uz"
    #     else:
    #         language = "Rus"
    #     language = EducationLanguage.query.filter(EducationLanguage.name == language).first()
    #     location = Locations.query.filter(Locations.id == teacher['locations']).first()
    #     add = Users(name=teacher['name'], surname=teacher['surname'], password=teacher['password'],
    #                 education_language=language.id, role_id=role.id,
    #                 location_id=location.id, user_id=user_id, username=teacher['username'],
    #                 born_day=teacher['day_born'],
    #                 born_month=teacher['month_born'], calendar_day=calendar_day.id,
    #                 calendar_month=calendar_month.id, calendar_year=calendar_year.id,
    #                 born_year=teacher['year_born'], age=teacher['age'], father_name=teacher['otasining_ismi'],
    #                 balance=0)
    #     db.session.add(add)
    #     db.session.commit()
    #     subject1 = Subjects.query.filter_by(name=teacher['subject']).first()
    #     teacher_get = Teachers(user_id=add.id, old_id=teacher['id'])
    #     db.session.add(teacher_get)
    #     db.session.commit()
    #     if subject1:
    #         teacher_get.subject.append(subject1)
    #         db.session.commit()
    #     add_phone = PhoneList(phone=teacher['phone'], personal=True, user_id=add.id)
    #     db.session.add(add_phone)
    #     db.session.commit()
    #
    # group_list = response.json()['group_list']
    # for group in group_list:
    #     group_exist = Groups.query.filter(Groups.old_id == group['id']).first()
    #     if not group_exist:
    #         if group['education_language'] == "Узбекский":
    #             language = "Uz"
    #         else:
    #             language = "Rus"
    #         language = EducationLanguage.query.filter(EducationLanguage.name == language).first()
    #         subject_get = Subjects.query.filter(Subjects.name == group['subject']).first()
    #         location_get = Locations.query.filter(Locations.id == group['location']).first()
    #         teacher_get = Teachers.query.filter(Teachers.old_id == group['teacher_id']).first()
    #         course_type_get = CourseTypes.query.filter(CourseTypes.name == group['type_of_course']).first()
    #
    #         if not teacher_get:
    #             add = Groups(name=group['name'], course_type_id=course_type_get.id, subject_id=subject_get.id,
    #                          teacher_salary=group['teacher_salary'], location_id=location_get.id,
    #                          calendar_day=calendar_day.id, status=True,
    #                          calendar_month=calendar_month.id, calendar_year=calendar_year.id, attendance_days=13,
    #                          price=group['cost'], old_id=group['id'],
    #                          education_language=language.id)
    #             db.session.add(add)
    #         else:
    #             add = Groups(name=group['name'], course_type_id=course_type_get.id, subject_id=subject_get.id,
    #                          teacher_salary=group['teacher_salary'], location_id=location_get.id,
    #                          calendar_day=calendar_day.id, teacher_id=teacher_get.id,
    #                          calendar_month=calendar_month.id, calendar_year=calendar_year.id, attendance_days=13,
    #                          price=group['cost'], old_id=group['id'], status=True,
    #                          education_language=language.id)
    #             db.session.add(add)
    #             teacher_get.group.append(add)
    #         db.session.commit()
    #
    #         for student in group['students']:
    #
    #             student = Students.query.filter(Students.old_id == student).first()
    #             if student:
    #                 student.group.append(add)
    #                 st_functions = Student_Functions(student_id=student.id)
    #                 st_functions.update_debt()
    #                 st_functions.update_extra_payment()
    #                 st_functions.update_balance()
    #                 if teacher_get:
    #                     group_history = StudentHistoryGroups(teacher_id=teacher_get.id, student_id=student.id,
    #                                                          group_id=add.id,
    #                                                          joined_day=calendar_day.date)
    #                     db.session.add(group_history)
    #                     db.session.commit()
    #                 else:
    #                     group_history = StudentHistoryGroups(student_id=student.id,
    #                                                          group_id=add.id,
    #                                                          joined_day=calendar_day.date)
    #                     db.session.add(group_history)
    #                     db.session.commit()
    #
    # staff_list = response.json()['staff_list']
    # for staff in staff_list:
    #     id = uuid.uuid1()
    #     user_id = id.hex[0:15]
    #     location = Locations.query.filter(Locations.id == staff['location']).first()
    #     language = EducationLanguage.query.first()
    #     if staff['job'] == "Administrator":
    #
    #         role = Roles.query.filter(Roles.admin == True).first()
    #     elif staff['job'] == "IT manager":
    #         role = Roles.query.filter(Roles.programmer == True).first()
    #     else:
    #         role = Roles.query.filter(Roles.user == True).first()
    #     hash = generate_password_hash("12345678", method='sha256')
    #     add = Users(name=staff['name'], surname=staff['surname'], password=hash,
    #                 education_language=language.id, role_id=role.id,
    #                 location_id=location.id, user_id=user_id, username=staff['username'],
    #                 born_day=staff['born_day'],
    #                 born_month=staff['born_month'], calendar_day=calendar_day.id,
    #                 calendar_month=calendar_month.id, calendar_year=calendar_year.id,
    #                 born_year=staff['year_born'], age=staff['age'], father_name=staff['father_name'],
    #                 )
    #     db.session.add(add)
    #     db.session.commit()
    #
    #     profession = Professions.query.filter(Professions.name == staff['job']).first()
    #     add = Staff(user_id=add.id, profession_id=profession.id, salary=staff['salary'])
    #     db.session.add(add)
    #     db.session.commit()

    return "Boldi"
