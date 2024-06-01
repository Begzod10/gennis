from app import app, api, request, jsonify, db, contains_eager, desc
from backend.models.models import Students, StudentCallingInfo, Users
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/new_students_calling', defaults={"location_id": None}, methods=["POST", "GET"])
@app.route(f'{api}/new_students_calling/<int:location_id>', methods=["POST", "GET"])
@jwt_required()
def new_students_calling(location_id):
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    location_id = user.location_id if not location_id else location_id
    students = Students.query.filter(Students.group == None).join(Students.user).filter(
        Users.location_id == location_id).all()
    students_info = []
    if request.method == "GET":
        for student in students:
            phone = next((phones.phone for phones in student.user.phone if phones.personal), None)
            subjects = [subject.name for subject in student.subject]
            info = {
                'id': student.id,
                'name': student.user.name,
                'surname': student.user.surname,
                'number': phone,
                'subject': subjects,
                'history': []
            }
            if student.student_calling_info:
                for calling_info in student.student_calling_info:
                    calling_date = {
                        'id': calling_info.id,
                        'comment': calling_info.comment,
                        'day': f'{calling_info.day.year}-{calling_info.day.month}-{calling_info.day.day}'
                    }
                    info['history'].append(calling_date)
            students_info.append(info)
        return jsonify({
            "students": students_info
        })
    if request.method == "POST":
        students = request.get_json()['students']
        today = datetime.today()
        for student in students:
            add_info = StudentCallingInfo(student_id=student['id'], comment=student['comment'], day=today)
            add_info.add()
        return jsonify({
            "status": "true"
        })
