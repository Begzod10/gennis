import calendar
import pprint
from datetime import datetime

from app import app, request, jsonify, classroom_server, db
from backend.functions.utils import api, send_subject_server
from backend.functions.utils import get_or_creat_datetime, find_calendar_date, iterate_models, get_json_field, \
    filter_month_day
from backend.group.models import GroupTest
from backend.models.models import CalendarMonth, CalendarYear
from backend.models.models import Groups, SubjectLevels
from backend.student.models import StudentTest, Students
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/create_test/<int:group_id>', methods=["POST", "GET", "PUT", "DELETE"])
@jwt_required()
def create_test(group_id):
    if request.method == "POST":
        year = get_json_field('date')[0:4]
        month = get_json_field('date')[5:7]
        day = get_json_field('date')[8:]
        year, month, day = get_or_creat_datetime(year, month, day)
        group = Groups.query.filter(Groups.id == group_id).first()
        test = GroupTest(name=get_json_field('name'), group_id=group_id, subject_id=group.subject_id,
                         level=get_json_field('level'), calendar_year=year.id, calendar_month=month.id,
                         calendar_day=day.id, number_tests=get_json_field('number'))
        test.add()
        return jsonify({
            "status": True,
            "msg": "Texst yaratildi.",
            "test": test.convert_json()
        })
    elif request.method == "DELETE":
        group_test = GroupTest.query.filter(GroupTest.id == get_json_field('test_id')).first()
        db.session.delete(group_test)
        db.session.commit()
        return jsonify({
            "msg": "Test o'chirildi",
            "success": True
        })
    else:
        test_get = GroupTest.query.filter(GroupTest.id == get_json_field('test_id')).first()
        year = get_json_field('date')[0:4]
        month = get_json_field('date')[5:7]
        day = get_json_field('date')[8:]
        year, month, day = get_or_creat_datetime(year, month, day)
        test_get.name = get_json_field('name')
        test_get.level = get_json_field('level')
        test_get.calendar_year = year.id
        test_get.calendar_day = day.id
        test_get.calendar_month = month.id
        db.session.commit()
        return jsonify({
            "msg": "Test ma'lumotlari o'zgartirildi",
            "success": True,
            "test": test_get.convert_json()
        })


@app.route(f'{api}/filter_datas_in_group/<int:group_id>', methods=["POST", "GET"])
@jwt_required()
def filter_datas_in_group(group_id):
    month_list = []
    if request.method == "GET":
        calendar_year, calendar_month, calendar_day = find_calendar_date()
        group_tests = GroupTest.query.filter(GroupTest.group_id == group_id).all()
        group_tests_month = GroupTest.query.filter(GroupTest.group_id == group_id,
                                                   GroupTest.calendar_year == calendar_year.id).all()
        group = Groups.query.filter(Groups.id == group_id).first()
        subject_levels = SubjectLevels.query.filter(SubjectLevels.subject_id == group.subject_id).order_by(
            SubjectLevels.id).all()
        years_list = []

        for group_test in group_tests:
            years_list.append(group_test.year.date.strftime("%Y"))
        for group_test in group_tests_month:
            month_list.append(group_test.month.date.strftime("%m"))
        years_list.sort()
        month_list.sort()
        years_list = list(dict.fromkeys(years_list))
        month_list = list(dict.fromkeys(month_list))
        return jsonify({
            "years_list": years_list,
            "month_list": month_list,
            "current_year": calendar_year.date.strftime("%Y"),
            "current_month": calendar_month.date.strftime("%m"),
        })
    else:
        year = datetime.strptime(f"{get_json_field('year')}", "%Y")

        calendar_year = CalendarYear.query.filter(CalendarYear.date == year).first()

        group_tests = GroupTest.query.filter(GroupTest.group_id == group_id,
                                             GroupTest.calendar_year == calendar_year.id).all()
        for group_test in group_tests:
            month_list.append(group_test.month.date.strftime("%m"))
        month_list = list(dict.fromkeys(month_list))
        return jsonify({
            "month_list": month_list
        })


@app.route(f'{api}/filter_test_group/<int:group_id>', methods=['POST'])
@jwt_required()
def filter_test_group(group_id):
    year = get_json_field('year')
    month = get_json_field('month')
    month = f"{year}-{month}"
    calendar_year = CalendarYear.query.filter(CalendarYear.date == datetime.strptime(year, "%Y")).first()
    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == datetime.strptime(month, "%Y-%m"),
                                                CalendarMonth.year_id == calendar_year.id).first()
    tests = GroupTest.query.filter(GroupTest.calendar_year == calendar_year.id,
                                   GroupTest.calendar_month == calendar_month.id,
                                   GroupTest.group_id == group_id).order_by(GroupTest.calendar_month).all()
    return jsonify({"tests": iterate_models(tests)})


@app.route(f'{api}/submit_test_group/<int:group_id>', methods=["POST"])
@jwt_required()
def submit_test_group(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    if request.method == "POST":
        group_test = GroupTest.query.filter(GroupTest.group_id == group.id,
                                            GroupTest.id == get_json_field('test_id')).first()
        group_percentage = 0
        for student in get_json_field('students'):
            student_get = Students.query.filter(Students.user_id == student['id']).first()
            true_answers = int(student['true_answers']) if "true_answers" in student else 0
            percentage = round((true_answers / group_test.number_tests) * 100)
            group_percentage += percentage
            exist_test = StudentTest.query.filter(StudentTest.student_id == student_get.id,
                                                  StudentTest.group_id == group_id,
                                                  StudentTest.group_test_id == group_test.id,
                                                  StudentTest.calendar_day == group_test.calendar_day).first()
            if not exist_test:
                add_test_result = StudentTest(subject_id=group.subject_id, group_test_id=group_test.id,
                                              calendar_day=group_test.calendar_day,
                                              student_id=student_get.id, true_answers=true_answers,
                                              percentage=percentage, group_id=group_id)
                add_test_result.add()
            else:
                exist_test.true_answers = true_answers
                exist_test.percentage = percentage
                db.session.commit()
        group_test.percentage = round(group_percentage / len(get_json_field('students')))
        db.session.commit()
        return jsonify({
            "status": True,
            "test": group_test.convert_json(),
            "msg": "Test natijasi kiritildi"
        })


