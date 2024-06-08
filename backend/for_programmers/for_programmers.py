import pprint

from app import app, db, request, jsonify
from backend.models.models import Subjects, PaymentTypes, Professions, Locations, AccountingPeriod, EducationLanguage, \
    CourseTypes
from backend.functions.utils import api, find_calendar_date, get_json_field
from flask_jwt_extended import jwt_required


@app.route(f'{api}/change_location_info/<int:location_id>', methods=['POST', "GET"])
@jwt_required()
def change_location_info(location_id):
    location = Locations.query.filter(Locations.id == location_id).first()
    if request.method == "POST":
        location.code = get_json_field('code')
        location.bank = get_json_field('bank')
        location.bank_sheet = get_json_field('bank_sheet')
        location.director_fio = get_json_field('director_fio')
        location.district = get_json_field('district')
        location.inn = get_json_field('inn')
        location.location_type = get_json_field('location_type')
        location.campus_name = get_json_field('campus_name')
        location.mfo = get_json_field('mfo')
        location.address = get_json_field('address')
        location.number_location = get_json_field('tel')
        db.session.commit()

        return jsonify({
            "msg": "Ma'lumotlar o'zgartirildi.",
            "data": location.convert_json()
        })

    else:
        return jsonify({
            "data": location.convert_json()
        })


@app.route(f'{api}/list_tools_info', methods=["GET"])
@jwt_required()
def list_tools():
    """

    :return: Subjects, PaymentTypes, CourseTypes, EducationLanguage, Professions, Locations, AccountingPeriod datas
    """
    subjects = Subjects.query.order_by(Subjects.id).all()
    subject_list = [{
        "id": subject.id,
        "name": subject.name,
        "number": subject.ball_number
    } for subject in subjects]

    payment_types = PaymentTypes.query.order_by(PaymentTypes.id).all()
    payment_list = [{
        "id": payment.id,
        "name": payment.name
    } for payment in payment_types]

    course_types = CourseTypes.query.order_by(CourseTypes.id).all()
    course_types_list = [{
        "id": course.id,
        "name": course.name
    } for course in course_types]
    education_languages = EducationLanguage.query.order_by(EducationLanguage.id).all()
    education_languages_list = [{
        "id": course.id,
        "name": course.name
    } for course in education_languages]
    professions = Professions.query.order_by(Professions.id).all()
    profession_list = [{
        "id": profession.id,
        "name": profession.name
    } for profession in professions]
    locations = Locations.query.order_by(Locations.id).all()
    location_list = [{
        "id": location.id,
        "name": location.name
    } for location in locations]

    periods = AccountingPeriod.query.order_by(AccountingPeriod.id).all()
    period_list = [{
        "id": period.id,
        "ot": period.from_date.strftime("%Y-%m-%d"),
        "do": period.to_date.strftime("%Y-%m-%d")
    } for period in periods]

    return jsonify({
        "tools": [
            {
                "title": "Subjects",
                "values": subject_list
            },
            {
                "title": "Payment Types",
                "values": payment_list
            },
            {
                "title": "Education Language",
                "values": education_languages_list
            },
            {
                "title": "Periods",
                "values": period_list
            },
            {
                "title": "Location",
                "values": location_list
            },
            {
                "title": "Profession",
                "values": profession_list
            },
            {
                "title": "Course Types",
                "values": course_types_list
            },
        ]
    })


@app.route(f'{api}/create_constants', methods=["POST"])
@jwt_required()
def create_constants():
    """
    add data or update datas in  Subjects, PaymentTypes, CourseTypes, EducationLanguage, Professions, Locations,
    AccountingPeriod
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    title = request.get_json()['title']
    if title == "Subjects":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:

                Subjects.query.filter(Subjects.id == sub['id']).update({
                    "name": sub['name'],
                    'ball_number': sub['number']
                })
                db.session.commit()
            else:
                subject = Subjects.query.filter(Subjects.name == sub['name']).first()
                if not subject:
                    subject = Subjects(name=sub['name'], ball_number=sub['number'])
                    db.session.add(subject)
                    db.session.commit()
        return jsonify({
            "msg": "Fan nomi o'zgardi",
            "success": True
        })

    if title == "Education Language":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:
                EducationLanguage.query.filter(EducationLanguage.id == sub['id']).update({
                    "name": sub['name']
                })
                db.session.commit()

            else:
                subject = EducationLanguage(name=sub['name'])
                db.session.add(subject)
                db.session.commit()
        return jsonify({
            "msg": "Yangi o'quv tili qo'shildi",
            "success": True
        })
    if title == "Location":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:
                Locations.query.filter(Locations.id == sub['id']).update({
                    "name": sub['name']
                })
                db.session.commit()
            else:
                subject = Locations(name=sub['name'],
                                    calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                    calendar_year=calendar_year.id)
                db.session.add(subject)
                db.session.commit()
        return jsonify({
            "msg": "Yangi o'quv joyi qo'shildi",
            "success": True
        })

    if title == "Course Types":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:
                CourseTypes.query.filter(CourseTypes.id == sub['id']).update({
                    "name": sub['name']
                })
                db.session.commit()

            else:

                subject = CourseTypes(name=sub['name'])
                db.session.add(subject)
                db.session.commit()
        return jsonify({
            "msg": "Yangi kurs turi qo'shildi",
            "success": True
        })
    if title == "Payment Types":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:
                PaymentTypes.query.filter(PaymentTypes.id == sub['id']).update({
                    "name": sub['name']
                })
                db.session.commit()

            else:
                subject = PaymentTypes(name=sub['name'])
                db.session.add(subject)
                db.session.commit()
        return jsonify({
            "msg": "Yangi to'lov turi qo'shildi",
            "success": True
        })
    if title == "Profession":
        item = request.get_json()['items']
        for sub in item:
            if 'id' in sub:
                Professions.query.filter(Professions.id == sub['id']).update({
                    "name": sub['name']
                })
                db.session.commit()

            else:
                subject = Professions(name=sub['name'])
                db.session.add(subject)
                db.session.commit()
        return jsonify({
            "msg": "Yangi kasb qo'shildi",
            "success": True
        })
