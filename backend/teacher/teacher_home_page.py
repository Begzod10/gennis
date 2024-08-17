from app import app, request, api, secure_filename, db, jsonify, checkFile
from backend.models.models import Users, Groups, StudentCertificate, Teachers, TeacherData
import json
from datetime import date
from backend.functions.small_info import certificate
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from pprint import pprint
from backend.functions.filters import iterate_models


@app.route(f'{api}/add_student_certificate', methods=['POST'])
@jwt_required()
def add_student_certificate():
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    res = eval(data['res'])
    text = res.get('text')
    teacher_id = res['teacher_id']
    student_id = res['student_id']
    today = date.today()
    group_id = res['group_id']
    photo = request.files['img']
    app.config['UPLOAD_FOLDER'] = certificate()

    student = Users.query.filter(Users.id == student_id).first()
    teacher = Users.query.filter(Users.id == teacher_id).first()

    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "certificates" + "/" + photo_filename
        new = StudentCertificate(teacher_id=teacher.teacher.id, group_id=group_id, student_id=student.student.id,
                                 text=text,
                                 date=today, img=url)
        db.session.add(new)
        db.session.commit()
        return jsonify({
            "msg": "Student sertifikati yaratildi",
            "success": True,
            "certificate": new.convert_json()
        })
    else:
        return jsonify({
            "msg": "Rasm formati to'gri kelmadi",
            "success": False
        })


@app.route(f'{api}/change_student_certificate/<int:certificate_id>', methods=['POST'])
@jwt_required()
def change_student_certificate(certificate_id):
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    res = eval(data['res'])
    text = res.get('text')
    photo = request.files['img']
    teacher_id = res['teacher_id']
    student_id = res['student_id']
    group_id = res['group_id']
    app.config['UPLOAD_FOLDER'] = certificate()
    student = Users.query.filter(Users.id == student_id).first()
    teacher = Users.query.filter(Users.id == teacher_id).first()
    certificate_get = StudentCertificate.query.filter(StudentCertificate.id == certificate_id).first()
    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "certificates" + "/" + photo_filename
        certificate_get.img = url

    certificate_get.text = text
    certificate_get.teacher_id = teacher.teacher.id
    certificate_get.student_id = student.student.id
    certificate_get.group_id = group_id
    db.session.commit()
    return jsonify({
        "msg": "Student sertifikati o'zgartirildi",
        "success": True,
        "certificate": certificate_get.convert_json()
    })


@app.route(f'{api}/delete_student_certificate/<certificate_id>', methods=['DELETE'])
@jwt_required()
def delete_student_certificate(certificate_id):
    StudentCertificate.query.filter(StudentCertificate.id == certificate_id).delete()
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Student sertifikati o'chirildi",
        "certificate_id": certificate_id
    })


@app.route(f'{api}/get_teacher_data/<int:teacher_id>', methods=['GET'])
def get_teacher_data(teacher_id):
    teacher = Teachers.query.filter(Teachers.user_id == teacher_id).first()
    data = TeacherData.query.filter(TeacherData.teacher_id == teacher.id).first()
    list = []
    certificates = StudentCertificate.query.filter(StudentCertificate.teacher_id == teacher.id).order_by(
        StudentCertificate.id).all()
    certificates_list = iterate_models(certificates)
    teacher_subjects = []
    for subject in teacher.subject:
        teacher_subjects.append(subject.name)
    if data:
        return jsonify({
            'data': data.convert_json(),
            'full_name': teacher.user.name + ' ' + teacher.user.surname,
            "teacher_img": teacher.user.photo_profile,
            'list': certificates_list,
            'subjects': teacher_subjects,
            'status': True
        })
    else:
        return jsonify({
            'status': False,
            'full_name': teacher.user.name + ' ' + teacher.user.surname,
            "teacher_img": teacher.user.photo_profile,
            'list': certificates_list,
            'subjects': teacher_subjects,
        })


@app.route(f'{api}/change_teacher_data', methods=['POST'])
@jwt_required()
def change_teacher_data():
    identity = get_jwt_identity()
    form = json.dumps(dict(request.form))
    data = json.loads(form)

    req = eval(data['res'])
    photo = request.files['img']

    text = req['text']
    telegram = req['telegram']
    instagram = req['instagram']
    facebook = req['facebook']
    teacher = Users.query.filter(Users.user_id == identity).first()
    data = TeacherData.query.filter(TeacherData.teacher_id == teacher.teacher.id).first()

    if data:
        data.text = text
        data.telegram = telegram
        data.instagram = instagram
        data.facebook = facebook
        app.config['UPLOAD_FOLDER'] = certificate()
        if photo and checkFile(photo.filename):
            if os.path.exists(f'frontend/build/{data.img}'):
                os.remove(f'frontend/build/{data.img}')
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "certificates" + "/" + photo_filename
            data.img = url
        db.session.commit()
        return jsonify({
            "msg": "Ma'lumotlar o'zgartirildi",
            'data': data.convert_json(),
            "success": True
        })
    else:
        app.config['UPLOAD_FOLDER'] = certificate()
        if photo and checkFile(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "certificates" + "/" + photo_filename
            new = TeacherData(teacher_id=teacher.teacher.id, text=text, telegram=telegram, instagram=instagram,
                              facebook=facebook, img=url)
            db.session.add(new)
            db.session.commit()
        else:
            new = TeacherData(teacher_id=teacher.teacher.id, text=text, telegram=telegram, instagram=instagram,
                              facebook=facebook)
            db.session.add(new)
            db.session.commit()
        return jsonify({
            "msg": "Ma'lumotlar qo'shildi",
            'data': new.json(),
            "success": True
        })
