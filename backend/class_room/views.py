from app import app, check_password_hash, db, request, jsonify, or_, contains_eager, classroom_server
from backend.models.models import Users, Roles, CalendarMonth, CalendarDay, CalendarYear, Attendance, AttendanceDays, \
    Students, Groups, Teachers, StudentCharity, Subjects, SubjectLevels, TeacherBlackSalary, StaffSalary, \
    DeletedTeachers
from backend.functions.utils import api, refresh_age, update_salary, iterate_models, get_json_field, check_exist_id
from datetime import datetime
from backend.functions.debt_salary_update import salary_debt
from flask_jwt_extended import jwt_required, create_refresh_token, create_access_token, get_jwt_identity
from backend.functions.filters import old_current_dates
from backend.group.class_model import Group_Functions
from backend.student.class_model import Student_Functions
from datetime import timedelta
from pprint import pprint
import requests


# @app.route(f'{api}/update_users_datas')
# def update_users_datas():
#     users = Users.query.filter(Users.id > 7999, Users.id < 9000).order_by(Users.id).all()
#     for user in users:
#         user_id = check_exist_id()
#         user.user_id = user_id
#         db.session.commit()
#     print(len(users))
#     return jsonify({
#         "count": len(users)
#     })


@app.route(f'{api}/login2', methods=['POST', 'GET'])
def login2():
    """
    login function
    create token
    :return: logged User datas
    """
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


@app.route(f'{api}/attendance_classroom/<int:group_id>')
@jwt_required()
def attendance_classroom(group_id):
    """
    filter Student and User table data
    :param group_id: Group primary key
    :return: Student table and User table data
    """
    today = datetime.today()

    hour = datetime.strftime(today, "%Y/%m/%d/%H/%M")
    hour2 = datetime.strptime(hour, "%Y/%m/%d/%H/%M")

    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).filter(or_(Students.ball_time <= hour2, Students.ball_time == None)).order_by('id').all()

    group = Groups.query.filter(Groups.id == group_id).first()
    attendance_info = []
    for student in group.student:
        if group.subject.ball_number > 2:
            score = [
                {
                    "name": "Homework",
                    "activeBall": 0
                },
                {
                    "name": "activity",
                    "activeBall": 0
                },
                {
                    "name": "dictionary",
                    "activeBall": 0
                }
            ]
        else:
            score = [
                {
                    "name": "Homework",
                    "activeBall": 0
                },
                {
                    "name": "activity",
                    "activeBall": 0
                }
            ]
        att = {
            "id": student.user.id,
            "name": student.user.name,
            "surname": student.user.surname,
            "balance": student.user.balance,
            "score": score,
            "money_type": ["green", "yellow", "red", "navy", "black"][student.debtor],
            "type": ""
        }
        attendance_info.append(att)

    gr_functions = Group_Functions(group_id=group_id)
    gr_functions.update_list_balance()
    return jsonify({
        "date": old_current_dates(group_id),
        "users": attendance_info
    })


@app.route(f'{api}/make_attendance_classroom', methods=['POST'])
# @jwt_required()
def make_attendance_classroom():
    """
    make attendance to students, update students' balance and teacher salary
    :return:
    """
    month = str(datetime.now().month)
    current_year = datetime.now().year
    old_year = datetime.now().year - 1
    data = request.get_json()['data']
    day = data['day']
    get_month = data['month']
    current_day = datetime.now().day
    if len(month) == 1:
        month = "0" + str(month)

    students = data['users']
    group_id = int(data['group_id'])
    group = Groups.query.filter(Groups.id == group_id).first()
    teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
    errors = []
    for st in students:
        student = Students.query.filter(Students.user_id == st['id']).first()
        homework = 0
        dictionary = 0
        active = 0
        type_attendance = st['type']

        if type_attendance == "yes":
            type_status = True
        else:
            type_status = False

        discount = StudentCharity.query.filter(StudentCharity.group_id == group_id,
                                               StudentCharity.student_id == student.id).first()
        if get_month == "12" and month == "01":
            current_year = old_year
        if not get_month:
            get_month = month

        date_day = str(current_year) + "-" + str(get_month) + "-" + str(day)
        date_month = str(current_year) + "-" + str(get_month)
        date_year = str(current_year)
        date_day = datetime.strptime(date_day, "%Y-%m-%d")
        date_month = datetime.strptime(date_month, "%Y-%m")
        date_year = datetime.strptime(date_year, "%Y")
        calendar_day = CalendarDay.query.filter(CalendarDay.date == date_day).first()
        calendar_month = CalendarMonth.query.filter(CalendarMonth.date == date_month).first()
        calendar_year = CalendarYear.query.filter(CalendarYear.date == date_year).first()
        if not calendar_year:
            calendar_year = CalendarYear(date=date_year)
            db.session.add(calendar_year)
            db.session.commit()
        if not calendar_month:
            calendar_month = CalendarMonth(date=date_month, year_id=calendar_year.id)
            db.session.add(calendar_month)
            db.session.commit()
        if not calendar_day:
            calendar_day = CalendarDay(date=date_day, month_id=calendar_month.id)
            db.session.add(calendar_day)
            db.session.commit()
        balance_with_discount = 0
        discount_per_day = 0
        discount_status = False
        if discount:
            balance_with_discount = round(
                (group.price / group.attendance_days) - (discount.discount / group.attendance_days))
            discount_per_day = round(discount.discount / group.attendance_days)
            discount_status = True
        today = datetime.today()
        hour = datetime.strftime(today, "%Y/%m/%d/%H/%M")
        hour2 = datetime.strptime(hour, "%Y/%m/%d/%H/%M")
        balance_per_day = round(group.price / group.attendance_days)
        salary_per_day = round(group.teacher_salary / group.attendance_days)
        ball_time = hour2 + timedelta(minutes=0)
        Students.query.filter(Students.id == student.id).update({"ball_time": ball_time})
        subject = Subjects.query.filter(Subjects.id == group.subject_id).first()
        attendance = Attendance.query.filter(Attendance.student_id == student.id,
                                             Attendance.calendar_year == calendar_year.id,
                                             Attendance.location_id == group.location_id,
                                             Attendance.calendar_month == calendar_month.id,
                                             Attendance.teacher_id == group.teacher_id,
                                             Attendance.group_id == group.id, Attendance.subject_id == subject.id,
                                             Attendance.course_id == group.course_type_id).first()

        if not attendance:
            attendance = Attendance(student_id=student.id, calendar_year=calendar_year.id,
                                    location_id=group.location_id,
                                    calendar_month=calendar_month.id, teacher_id=teacher.id, group_id=group_id,
                                    course_id=group.course_type_id, subject_id=subject.id)
            db.session.add(attendance)
            db.session.commit()

        exist_attendance = db.session.query(AttendanceDays).join(AttendanceDays.attendance).options(
            contains_eager(AttendanceDays.attendance)).filter(AttendanceDays.student_id == student.id,
                                                              AttendanceDays.calendar_day == calendar_day.id,
                                                              AttendanceDays.group_id == group_id,
                                                              Attendance.calendar_month == calendar_month.id,
                                                              Attendance.calendar_year == calendar_year.id).first()
        if exist_attendance:
            info = {
                "active": True,
                "message": f"{student.user.name} {student.user.surname} bu kunda davomat qilingan",
                "status": "danger"

            }
            errors.append(info)
            continue
        len_attendance = AttendanceDays.query.filter(AttendanceDays.student_id == student.id,
                                                     AttendanceDays.group_id == group_id,
                                                     AttendanceDays.location_id == group.location_id,
                                                     AttendanceDays.attendance_id == attendance.id,
                                                     ).count()

        if len_attendance >= group.attendance_days:
            info = {
                "active": True,
                "message": f"{student.user.name} {student.user.surname} bu oyda 13 kun dan ko'p davomat qilindi",
                "status": "danger"
            }
            errors.append(info)
            continue
        ball = 5
        if int(day) < int(current_day):
            late_days = int(current_day) - int(day)

            ball -= late_days
            if ball < 0:
                ball = 0
        if not type_status:
            attendance_add = AttendanceDays(teacher_id=teacher.id, student_id=student.id,
                                            calendar_day=calendar_day.id, attendance_id=attendance.id,
                                            reason="",
                                            status=0, balance_per_day=balance_per_day,
                                            balance_with_discount=balance_with_discount,
                                            salary_per_day=salary_per_day, group_id=group_id,
                                            location_id=group.location_id,
                                            discount_per_day=discount_per_day, teacher_ball=ball,
                                            discount=discount_status)
            db.session.add(attendance_add)
            db.session.commit()
        elif homework == 0 and dictionary == 0 and active == 0:
            attendance_add = AttendanceDays(teacher_id=teacher.id, student_id=student.id,
                                            calendar_day=calendar_day.id, attendance_id=attendance.id,
                                            status=1, balance_per_day=balance_per_day, teacher_ball=ball,
                                            balance_with_discount=balance_with_discount,
                                            salary_per_day=salary_per_day, group_id=group_id,
                                            location_id=group.location_id, discount=discount_status,
                                            discount_per_day=discount_per_day)
            db.session.add(attendance_add)
            db.session.commit()
        else:
            average_ball = round((homework + dictionary + active) / subject.ball_number)
            attendance_add = AttendanceDays(student_id=student.id, attendance_id=attendance.id,
                                            dictionary=dictionary, teacher_ball=ball,
                                            calendar_day=calendar_day.id,
                                            status=2, balance_per_day=balance_per_day, homework=homework,
                                            average_ball=average_ball, activeness=active, group_id=group_id,
                                            location_id=group.location_id, teacher_id=teacher.id,
                                            balance_with_discount=balance_with_discount,
                                            salary_per_day=salary_per_day, discount=discount_status,
                                            discount_per_day=discount_per_day)
            db.session.add(attendance_add)
            db.session.commit()
        attendance_days = AttendanceDays.query.filter(AttendanceDays.attendance_id == attendance.id,
                                                      AttendanceDays.teacher_ball != None).all()
        total_ball = 0
        for attendance_day in attendance_days:
            total_ball += attendance_day.teacher_ball
        result = round(total_ball / len(attendance_days))
        Attendance.query.filter(Attendance.id == attendance.id).update({
            "ball_percentage": result
        })
        db.session.commit()
        st_functions = Student_Functions(student_id=student.id)
        st_functions.update_debt()
        st_functions.update_balance()

        salary_location = salary_debt(student_id=student.id, group_id=group_id, attendance_id=attendance_add.id,
                                      status_attendance=False, type_attendance="add")

        update_salary(teacher_id=teacher.user_id)

        if student.debtor == 2:
            black_salary = TeacherBlackSalary.query.filter(TeacherBlackSalary.teacher_id == teacher.id,
                                                           TeacherBlackSalary.student_id == student.id,
                                                           TeacherBlackSalary.calendar_month == calendar_month.id,
                                                           TeacherBlackSalary.calendar_year == calendar_year.id,
                                                           TeacherBlackSalary.status == False,
                                                           TeacherBlackSalary.location_id == student.user.location_id,
                                                           TeacherBlackSalary.salary_id == salary_location.id).first()
            if not black_salary:
                black_salary = TeacherBlackSalary(teacher_id=teacher.id, total_salary=salary_per_day,
                                                  student_id=student.id, salary_id=salary_location.id,
                                                  calendar_month=calendar_month.id,
                                                  calendar_year=calendar_year.id,
                                                  location_id=student.user.location_id
                                                  )
                black_salary.add()
            else:
                black_salary.total_salary += salary_per_day
                db.session.commit()

        requests.post(f"{classroom_server}/api/update_student_balance", json={
            "platform_id": student.user.id,
            "balance": student.user.balance,
            "teacher_id": teacher.user_id,
            "salary": teacher.user.balance,
            "debtor": student.debtor
        })
    if errors:
        status = "danger"
    else:
        status = "success"

    return jsonify({
        "message": "O'quvchilar davomat qilindi",
        "status": status,
        "errors": errors
    })


@app.route(f'{api}/get_user')
@jwt_required()
def get_user():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    user = Users.query.filter_by(user_id=identity).first()
    subjects = Subjects.query.order_by(Subjects.id).all()
    subject_list = []
    for sub in subjects:
        subject_list.append(sub.convert_json())
    # users = Users.query.order_by(Users.id).all()

    return jsonify({
        "data": user.convert_json(),
        "access_token": access_token,
        "refresh_token": create_refresh_token(identity=user.user_id),
        "subject_list": subject_list,
        # "users": iterate_models(users, entire=True)
    })


@app.route(f'{api}/get_group_datas/<int:group_id>')
@jwt_required()
def get_group_datas(group_id):
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    students = Students.query.join(Students.group).filter(Groups.id == group_id).all()
    users = Users.query.filter(Users.id.in_([user.user.id for user in students])).all()
    # for user in users:
    #     user_id = check_exist_id(user.user_id)
    #     user.user_id = user_id
    #     db.session.commit()
    return jsonify({
        "users": iterate_models(users),
        "access_token": access_token
    })


@app.route(f'{api}/update_group_datas', methods=['POST'])
@jwt_required()
def update_group_datas():
    group = Groups.query.filter(Groups.id == request.get_json()['group']['platform_id']).first()
    if request.get_json()['group']['course']:
        level = SubjectLevels.query.filter(
            SubjectLevels.classroom_id == request.get_json()['group']['course']['id']).first()
        if not level:
            level = SubjectLevels.query.filter(
                SubjectLevels.name == request.get_json()['group']['course']['name']).first()
        group.level_id = level.id
    return jsonify({
        "msg": "O'zgarildi"
    })


@app.route(f'{api}/update_user/<user_id>', methods=['POST'])
@jwt_required()
def update_user(user_id):
    Users.query.filter(Users.id == user_id).update({
        "user_id": get_json_field('user_id')
    })
    db.session.commit()
    return jsonify({
        "msg": "User id o'zgartirildi"
    })


@app.route(f'/api/get_datas', methods=['POST'])
def get_datas():
    type_info = request.get_json()['type']
    if type_info == "subject":
        response = request.get_json()['subject']
        for res in response:
            get_subject = Subjects.query.filter(Subjects.classroom_id == res['id']).first()
            if not get_subject:
                get_subject = Subjects.query.filter(Subjects.name == res['name']).first()
            if not get_subject:
                get_subject = Subjects(name=res['name'], ball_number=2, classroom_id=res['id'])
                get_subject.add()
            else:

                get_subject.disabled = res['disabled']
                get_subject.classroom_id = res['id']
                get_subject.name = res['name']
                db.session.commit()
        # disabled_subjects = Subjects.query.filter(Subjects.disabled == True).all()
        # for level in disabled_subjects:
        #     for gr in level.groups:
        #         gr.subject_id = None
        #         db.session.commit()
    else:
        response = request.get_json()['levels']
        for level in response:
            get_subject = Subjects.query.filter(Subjects.classroom_id == level['subject']['id']).first()
            if not get_subject:

                get_subject = Subjects.query.filter(Subjects.name == level['subject']['name']).first()

            elif not get_subject:
                get_subject = Subjects(name=level['subject']['name'], ball_number=2,
                                       classroom_id=level['subject']['id'])
                get_subject.add()
            else:
                get_subject.disabled = level['subject']['disabled']
                get_subject.classroom_id = level['subject']['id']
                get_subject.name = level['subject']['name']
                db.session.commit()
            get_level = SubjectLevels.query.filter(SubjectLevels.classroom_id == level['id'],
                                                   SubjectLevels.subject_id == get_subject.id).first()
            if not get_level:
                get_level = SubjectLevels.query.filter(SubjectLevels.name == level['name'],
                                                       SubjectLevels.subject_id == get_subject.id).first()

            if not get_level:
                get_level = SubjectLevels(name=level['name'], subject_id=get_subject.id, classroom_id=level['id'])
                get_level.add()
            else:
                get_level.disabled = level['disabled']
                get_level.classroom_id = level['id']
                get_level.name = level['name']
                db.session.commit()
        # disabled_levels = SubjectLevels.query.filter(SubjectLevels.disabled == True).all()
        # for level in disabled_levels:
        #     for gr in level.groups:
        #         gr.level_id = None
        #         db.session.commit()
    return jsonify({
        "msg": "Zo'r"
    })
