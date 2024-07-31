from app import app, api, request, db, get_jwt_identity, jwt_required, jsonify, generate_password_hash, classroom_server
import os
from backend.models.models import Users, PhoneList, Students, Teachers, Roles, StudentExcuses, Subjects
from backend.functions.small_info import checkFile, user_photo_folder
from backend.functions.utils import find_calendar_date, send_user_info
from werkzeug.utils import secure_filename
from datetime import datetime
import requests


@app.route(f"{api}/update_photo_profile/<int:user_id>", methods=["POST"])
@jwt_required()
def update_photo_profile(user_id):
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


@app.route(f'{api}/change_student_info/<int:user_id>', methods=['POST'])
@jwt_required()
def change_student_info(user_id):
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
                send_user_info(user)
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

                del_phone = PhoneList.query.filter(PhoneList.user_id == user.id, PhoneList.personal == True).first()
                

                if not del_phone:
                    del_phone = PhoneList(user_id=user_id, personal=True, phone=json['phone'])
                    db.session.add(del_phone)
                    db.session.commit()
                del_phone.phone = json['phone']
                db.session.commit()

                del_phone = PhoneList.query.filter(PhoneList.user_id == user.id, PhoneList.parent == True).first()
                if not del_phone:
                    del_phone = PhoneList(user_id=user_id, parent=True, phone=json['parentPhone'])
                    db.session.add(del_phone)
                    db.session.commit()
                del_phone.phone = json['parentPhone']

                db.session.commit()

                send_user_info(user)
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
            user = Users.query.filter(Users.id == user_id).first()
            user.username = json['username']
            db.session.commit()
            send_user_info(user)
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


@app.route(f'{api}/debt_reason/<int:user_id>', methods=['POST'])
@jwt_required()
def debt_reason(user_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    reason = request.get_json()['reason']
    select = request.get_json()['select']
    to_date = request.get_json()['date']
    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    student = Students.query.filter(Students.user_id == user_id).first()
    if select == "yes":
        add = StudentExcuses(reason=reason, to_date=to_date, added_date=calendar_day.date, student_id=student.id)
        db.session.add(add)
        db.session.commit()
    else:
        reason = "tel ko'tarmadi"
        add = StudentExcuses(reason=reason, added_date=calendar_day.date, student_id=student.id)
        db.session.add(add)
        db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Ma'lumot kiritildi"
    })
