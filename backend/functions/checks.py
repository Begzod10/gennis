from app import app, request, jsonify
from backend.models.models import *
from backend.functions.utils import api
from flask_jwt_extended import *
from werkzeug.security import generate_password_hash, check_password_hash


@app.route(f'{api}/check_username', methods=['POST'])
def check_username():
    """
    check exist data in Users  table
    :return:
    """
    body = {}
    username = request.get_json()

    find_username_users = Users.query.filter_by(username=username).first()

    body['found'] = True if find_username_users else False
    return jsonify(body)


@app.route(f'{api}/check_exist_username/<int:user_id>', methods=['POST'])
def check_exist_username(user_id):
    """
    check exist data in Users table by user_id
    :param user_id: Users table primary key
    :return:
    """
    username = request.get_json()['username']
    user = Users.query.filter(Users.id == user_id).first()
    exist_username = Users.query.filter(and_(Users.username == username, Users.username != user.username)).first()

    error = True if exist_username else False
    return jsonify({
        "found": error
    })


@app.route(f'{api}/check_subject/<int:user_id>', methods=['POST'])
@jwt_required()
def check_subject(user_id):
    """
    check exist data in Student.subject relationship
    :param user_id: Users table primary key
    :return:
    """

    subject = request.get_json()['subject']
    student = Students.query.filter(Students.user_id == user_id).first()
    subject_list = []
    if student.group:
        for sub in student.group:
            subject_group = Subjects.query.filter(Subjects.id == sub.subject_id).first()
            subject_list.append(subject_group.name)

    error = True if subject in subject_list else False
    return jsonify({
        "found": error
    })


@app.route(f'{api}/check_password', methods=['POST'])
@jwt_required()
def check_password():
    """
    compare passwords
    :return:
    """
    body = {}
    user_id = int(request.get_json()['id'])
    password = request.get_json()['password']
    username = Users.query.filter_by(id=user_id).first()
    body['password'] = True if username and check_password_hash(username.password, password) else False
    return jsonify(body)
