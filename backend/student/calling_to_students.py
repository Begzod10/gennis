from app import app, api, request, jsonify, db, contains_eager, desc
from backend.models.models import Students, StudentCallingInfo
from datetime import datetime


@app.route('/new_students_calling', methods=["POST", "GET"])
def new_students_calling():
    students = Students.query.filter(Students.group == None).all()
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
