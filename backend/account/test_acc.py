from flask import session
from sqlalchemy import func

from app import app, db, desc, contains_eager, request, jsonify
from backend.group.models import Attendance, AttendanceDays

from backend.student.models import Students
from backend.account.models import ExpensesType, ExpensesConnectionTypes

from backend.account.utils import student_collection_api, teacher_collection_api
from backend.functions.utils import api, find_calendar_date, get_json_field, update_staff_salary_id, \
    update_teacher_salary_id, update_salary
from pprint import pprint
from sqlalchemy.orm import sessionmaker


@app.route('/collection', methods=["POST", "GET"])
def collection():
    return jsonify(
        {
            "students_collection": student_collection_api(),
            "teacher_collection": teacher_collection_api()
        }
    )


@app.route('/calculate_student_debts/<int:student_id>', methods=["POST", "GET"])
def calculate_student_debts(student_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    attendance = Attendance.query.filter(Attendance.student_id == student_id,
                                         Attendance.calendar_year == calendar_year.id,
                                         Attendance.calendar_month == calendar_month.id).first()
    student = Students.query.filter(Students.id == student_id).first()
    courses = []
    for group in student.group:
        attendance = Attendance.query.filter(Attendance.student_id == student_id,
                                             Attendance.calendar_year == calendar_year.id,
                                             Attendance.calendar_month == calendar_month.id,
                                             Attendance.group_id == group.id).first()
        attendance_days = AttendanceDays.query.filter(AttendanceDays.attendance_id == attendance.id).all()
        info = {
            "group": {
                "id": group.id,
                "name": group.name,
                "price": group.price
            },
            "result": ""
        }
        balance = 0
        balance_per_day = 0
        if attendance_days:
            for attendance_day in attendance_days:
                balance_per_day = attendance_day.balance_per_day
                balance += attendance_day.balance_per_day
            if len(attendance_days) < 13:
                calculate_day = 13 - len(attendance_days)
                calculate_debt = balance_per_day * calculate_day
                result = calculate_debt + balance
                info["result"] = result
        else:
            result = group.price
            info["result"] = result
        courses.append(info)
    total_debt = 0
    for course in courses:
        total_debt += int(course["result"])
    return jsonify({"total_debt": total_debt})


@app.route('/expenses_type_add', methods=["POST", "GET"])
def expenses_type_add():
    info = request.get_json()['info']
    if info['parent_type_id']:

        add = ExpensesType(name=info['name'])
        db.session.add(add)
        db.session.commit()
        parent_connection = ExpensesConnectionTypes.query.filter(
            ExpensesConnectionTypes.parent_type_id == info['parent_type_id']).first()
        if parent_connection:
            subqry = db.session.query(func.max(ExpensesConnectionTypes.order)).filter(
                ExpensesConnectionTypes.parent_type_id == info['parent_type_id']).first()
            order = int(subqry[0]) + 1
            add_connection = ExpensesConnectionTypes(expenses_type_id=add.id, parent_type_id=info['parent_type_id'],
                                                     order=order)
            db.session.add(add_connection)
            db.session.commit()
        else:
            add_connection = ExpensesConnectionTypes(expenses_type_id=add.id, parent_type_id=info['parent_type_id'],
                                                     order=1)
            db.session.add(add_connection)
            db.session.commit()
    else:
        add = ExpensesType(name=info['name'])
        db.session.add(add)
        db.session.commit()
    return jsonify({"status": "True"})


@app.route('/get_expenses', methods=["POST", "GET"])
def get_expenses():
    def build_children(expense_type):
        children = []
        for child in expense_type.parent:
            child_info = {
                'id': child.expenses_type.id,
                'name': child.expenses_type.name,
                'parent_type_id': child.parent_type_id,
                'order': child.order
            }
            if child.expenses_type.parent:
                child_info['child'] = build_children(child.expenses_type)
            children.append(child_info)
        return children

    def build_type_tree(expenses_types):
        types = []
        for expense_type in expenses_types:
            info = {
                'id': expense_type.id,
                'name': expense_type.name
            }
            if expense_type.parent:
                info['child'] = build_children(expense_type)
            types.append(info)
        return types

    expenses_types = ExpensesType.query.all()
    types = build_type_tree(expenses_types)
    return jsonify({"status": types})
