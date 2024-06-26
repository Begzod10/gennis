from app import app, api, jsonify, db
from backend.models.models import QR_students
from backend.functions.utils import find_calendar_date, get_json_field
import random


@app.route(f'{api}/test_register', methods=['POST'])
def test_register():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    name = get_json_field('name')
    surname = get_json_field('surname')
    phone = int(get_json_field('phone'))
    exist_username = QR_students.query.filter(QR_students.name == name, QR_students.surname == surname,
                                              QR_students.phone == phone).first()
    if exist_username:
        return jsonify({
            "success": False,
            "msg": "Bu ma'lumotlar kiritilgan"
        })

    sums = [50000, 60000, 70000]

    qr_student = QR_students(name=name, surname=surname, phone=phone, winning_amount=random.choice(sums),
                             calendar_day=calendar_day.id)
    db.session.add(qr_student)
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": qr_student.winning_amount
    })


@app.route(f'{api}/qr_students')
def qr_students():
    students = QR_students.query.order_by(QR_students.id).all()
    student_list = [{
            "id": student.id,
            "name": student.name,
            "surname": student.surname,
            'phone': student.phone,
            "money": student.winning_amount,
            "date": student.day.date.strftime("%Y-%m-%d")
        } for student in students]
    return jsonify({
        "students": student_list
    })
