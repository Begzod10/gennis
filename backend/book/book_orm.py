from app import app, api, request, get_jwt_identity, contains_eager, jsonify, db, jwt_required, desc, or_
from backend.models.models import Users, Teachers, Locations, BookOrder, Book, BookOverhead, BookPayments, \
    BranchPayment, UserBooks, TeacherSalary, StaffSalary, CollectedBookPayments, Staff, AccountingPeriod, EditorBalance, \
    CalendarMonth, CalendarDay, PaymentTypes, Students
from backend.functions.utils import update_staff_salary_id, update_teacher_salary_id, iterate_models, \
    find_calendar_date, get_json_field
from .class_model import check_editor_balance, update_balance_editor
from datetime import datetime
from .utils import handle_get_request, handle_post_request, delete_book_images, update_book
from backend.functions.debt_salary_update import staff_salary_update
from backend.functions.filters import old_current_dates

import os
from pprint import pprint


@app.route(f'{api}/filter_book/')
@jwt_required()
def filter_book():
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()

    filter_data = []
    if user.role_info.type_role == "admin" or user.role_info.type_role == "director":
        teachers = db.session.query(Teachers).join(Teachers.locations).options(
            contains_eager(Teachers.locations)).filter(Locations.id == user.location_id).order_by(Teachers.id).all()
        for teacher in teachers:

            info = {
                "id": teacher.id,
                "name": teacher.user.name,
                "surname": teacher.user.surname,
                "groups": [],
            }
            for gr in teacher.group:
                if not gr.deleted:
                    info['groups'].append(gr.convert_json())
            filter_data.append(info)
    elif user.role_info.type_role == "teacher":
        teacher = Teachers.query.filter(Teachers.user_id == user.id).first()

        location_list = [
            {
                "id": location.id,
                "name": location.name
            } for location in teacher.locations

        ]
        # location_list.append({
        #     "id": teacher.user.location.id,
        #     "name": teacher.user.location.name,
        # })

        info = {
            "id": teacher.id,
            "name": teacher.user.name,
            "surname": teacher.user.surname,
            "groups": [],
            "location_list": location_list
        }
        for group in teacher.group:
            if not group.deleted:
                info['groups'].append(group.convert_json())
        filter_data.append(info)
    return jsonify({
        "data": filter_data,
    })


@app.route(f'{api}/order_confirm/<int:order_id>')
@jwt_required()
def order_confirm(order_id):
    order = BookOrder.query.filter(BookOrder.id == order_id).first()

    if order.editor_confirm:
        order.editor_confirm = False
    else:
        order.editor_confirm = True
    db.session.commit()
    return jsonify({
        "msg": "O'zgartirildi"
    })


@app.route(f'{api}/buy_book', methods=['GET', 'POST'])
@jwt_required()
def buy_book():
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    if request.method == "POST":
        data = request.get_json()

        group_id = None

        if "group_id" in data:
            group_id = data['group_id']
        if "teacher_id" in data:
            teacher_id = data['teacher_id']
        else:
            teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
            teacher_id = teacher.id
        book_id = data['book_id']
        book = Book.query.filter(Book.id == book_id).first()
        count = None
        if 'count' in data:
            count = data['count']
        if 'students' in data and data['students']:
            for student in data['students']:
                student_get = Students.query.filter(Students.id == student['id']).first()
                exist_order = BookOrder.query.filter(BookOrder.student_id == student['id'],
                                                     BookOrder.book_id == book_id, BookOrder.deleted == False).first()
                if not exist_order:
                    book_order = BookOrder(student_id=student['id'], group_id=group_id, teacher_id=teacher_id,
                                           book_id=book_id, accounting_period_id=accounting_period.id,
                                           user_id=user.id, calendar_day=calendar_day.id,
                                           location_id=student_get.user.location_id)
                    book_order.add()
                    add_book_payment = BookPayments(student_id=student['id'], location_id=user.location_id,
                                                    calendar_day=calendar_day.id,
                                                    account_period_id=accounting_period.id,
                                                    calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                                    payment_sum=book.price, book_order_id=book_order.id)
                    add_book_payment.add()

            return jsonify({
                "msg": "Xaridingiz uchun rahmat!",
                "success": True
            })
        if 'location_id' in data:
            location_id = data['location_id']
        else:
            location_id = user.location_id
        teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
        staff = Staff.query.filter(Staff.user_id == user.id).first()

        book_order = BookOrder(group_id=group_id, teacher_id=teacher_id, book_id=book.id, count=count,
                               accounting_period_id=accounting_period.id,
                               user_id=user.id, calendar_day=calendar_day.id, location_id=location_id)
        book_order.add()

        if teacher:
            salary_location = TeacherSalary.query.filter(TeacherSalary.location_id == location_id,
                                                         TeacherSalary.teacher_id == teacher.id,
                                                         TeacherSalary.calendar_year == calendar_year.id,
                                                         TeacherSalary.calendar_month == calendar_month.id).first()
            if not salary_location:
                salary_location = TeacherSalary(location_id=location_id,
                                                teacher_id=teacher.id,
                                                calendar_month=calendar_month.id,
                                                calendar_year=calendar_year.id)
                db.session.add(salary_location)
                db.session.commit()

            add = UserBooks(payment_sum=book_order.book.price,
                            user_id=user.id, location_id=location_id, book_order_id=book_order.id,
                            calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                            calendar_year=calendar_year.id, account_period_id=accounting_period.id,
                            salary_location_id=salary_location.id)
            add.add()
            update_teacher_salary_id(salary_location.id)
        else:
            staff_salary_update()
            staff_salary_info = StaffSalary.query.filter(StaffSalary.calendar_month == calendar_month.id,
                                                         StaffSalary.calendar_year == calendar_year.id,
                                                         StaffSalary.staff_id == staff.id).first()
            if not staff_salary_info:
                staff_salary_info = StaffSalary(calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                                total_salary=staff.salary, staff_id=staff.id,
                                                location_id=staff.user.location_id)
                db.session.add(staff_salary_info)
                db.session.commit()
            add = UserBooks(payment_sum=book_order.book.price,
                            user_id=user.id, location_id=location_id, book_order_id=book_order.id,
                            calendar_month=calendar_month.id, calendar_day=calendar_day.id,
                            calendar_year=calendar_year.id, account_period_id=accounting_period.id,
                            salary_id=staff_salary_info.id)
            add.add()
            update_staff_salary_id(staff_salary_info.id)
        # xdj@hacksnation.com
        return jsonify({
            "msg": "Xaridingiz uchun rahmat!",
            "success": True
        })

    else:
        identity = get_jwt_identity()
        user = Users.query.filter(Users.user_id == identity).first()
        if user.role_info.type_role == "muxarir":

            orders = BookOrder.query.filter(
                BookOrder.deleted == False, BookOrder.editor_confirm == False,
                BookOrder.admin_confirm == False).order_by(
                BookOrder.id).all()
            old_books = BookOrder.query.filter(BookOrder.editor_confirm == True, BookOrder.admin_confirm == True,
                                               BookOrder.deleted == False).order_by(
                BookOrder.id).all()
        elif user.role_info.type_role == "admin":
            orders = BookOrder.query.filter(
                BookOrder.deleted == False, BookOrder.editor_confirm == False,
                BookOrder.admin_confirm == False,
                BookOrder.location_id == user.location_id).order_by(
                BookOrder.id).all()
            old_books = BookOrder.query.filter(BookOrder.editor_confirm == True, BookOrder.admin_confirm == True,
                                               BookOrder.deleted == False,
                                               BookOrder.location_id == user.location_id).order_by(
                BookOrder.id).all()

        return jsonify({
            "old_books": iterate_models(old_books),
            "new_books": iterate_models(orders),

        })


@app.route(f'{api}/teacher_orders', defaults={"type_order": None})
@app.route(f'{api}/teacher_orders/<type_order>')
@jwt_required()
def teacher_orders(type_order):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    student = Students.query.filter(Students.user_id == user.id).first()
    if teacher:
        if type_order == "student":
            orders = BookOrder.query.filter(
                BookOrder.deleted == False, BookOrder.teacher_id == teacher.id,
                BookOrder.editor_confirm == False,
                BookOrder.admin_confirm == False,
                BookOrder.student_id != None).order_by(
                BookOrder.id).all()
            old_books = BookOrder.query.filter(BookOrder.editor_confirm == True, BookOrder.admin_confirm == True,
                                               BookOrder.deleted == False, BookOrder.student_id != None,
                                               BookOrder.teacher_id == teacher.id).order_by(
                BookOrder.id).all()
        else:
            orders = BookOrder.query.filter(
                BookOrder.deleted == False, BookOrder.teacher_id == teacher.id,
                BookOrder.editor_confirm == False,
                BookOrder.admin_confirm == False,
                BookOrder.student_id == None).order_by(
                BookOrder.id).all()
            old_books = BookOrder.query.filter(BookOrder.editor_confirm == True, BookOrder.admin_confirm == True,
                                               BookOrder.deleted == False, BookOrder.student_id == None,
                                               BookOrder.teacher_id == teacher.id).order_by(
                BookOrder.id).all()
    else:
        orders = BookOrder.query.filter(
            BookOrder.deleted == False, BookOrder.student_id == student.id,
            BookOrder.editor_confirm == False,
            BookOrder.admin_confirm == False).order_by(
            BookOrder.id).all()
        old_books = BookOrder.query.filter(BookOrder.editor_confirm == True, BookOrder.admin_confirm == True,
                                           BookOrder.deleted == False,
                                           BookOrder.student_id == student.id).order_by(
            BookOrder.id).all()
    return jsonify({
        "old_books": iterate_models(old_books),
        "new_books": iterate_models(orders),

    })


@app.route(f'{api}/delete_book_order/<int:order_id>', methods=['POST'])
@jwt_required()
def delete_book_order(order_id):
    reason = get_json_field('otherReason')
    BookOrder.query.filter(BookOrder.id == order_id).update({
        "deleted": True,
        "reason": reason
    })
    db.session.commit()
    book_payment_get = BookPayments.query.filter(BranchPayment.book_order_id == order_id).first()
    user_book = UserBooks.query.filter(UserBooks.book_order_id == order_id).first()
    if book_payment_get:
        db.session.delete(book_payment_get)
    if user_book:
        db.session.delete(user_book)
    db.session.commit()

    return jsonify({
        "msg": "Xarid o'chirildi",
        "success": True
    })


@app.route(f'{api}/filtered_orders_books2/', defaults={"type": None})
@app.route(f'{api}/filtered_orders_books2/<type>')
@jwt_required()
def filtered_orders_books(type):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    collected_books = CollectedBookPayments.query.filter(CollectedBookPayments.location_id == user.location_id,
                                                         CollectedBookPayments.status == False).first()
    if type != "archive":
        if user.role_info.type_role == "muxarir":

            orders = BookOrder.query.filter(BookOrder.accounting_period_id == accounting_period.id,
                                            BookOrder.deleted == False, BookOrder.collected_payments_id == None,
                                            ).order_by(
                BookOrder.id).all()

        elif user.role_info.type_role == "admin":
            orders = BookOrder.query.filter(BookOrder.accounting_period_id == accounting_period.id,
                                            BookOrder.deleted == False, BookOrder.collected_payments_id == None,
                                            BookOrder.location_id == user.location_id,
                                            ).order_by(
                BookOrder.id).all()
        else:
            orders = BookOrder.query.filter(BookOrder.accounting_period_id == accounting_period.id,
                                            BookOrder.deleted == False, BookOrder.user_id == user.id,
                                            BookOrder.collected_payments_id == None

                                            ).order_by(
                BookOrder.id).all()
    else:
        if user.role_info.type_role == "muxarir":

            orders = db.session.query(BookOrder).join(BookOrder.collected).options(
                contains_eager(BookOrder.collected)).filter(BookOrder.accounting_period_id == accounting_period.id,
                                                            BookOrder.deleted == False,
                                                            BookOrder.collected_payments_id != None
                                                            ).order_by(
                BookOrder.id).all()

        elif user.role_info.type_role == "admin":

            orders = db.session.query(BookOrder).join(BookOrder.collected).options(
                contains_eager(BookOrder.collected)).filter(
                                                            BookOrder.deleted == False,
                                                            BookOrder.location_id == user.location_id,
                                                            BookOrder.collected_payments_id != None).order_by(
                BookOrder.id).all()
        else:

            orders = db.session.query(BookOrder).join(BookOrder.collected).options(
                contains_eager(BookOrder.collected)).filter(BookOrder.accounting_period_id == accounting_period.id,
                                                            BookOrder.deleted == False, BookOrder.user_id == user.id,
                                                            BookOrder.collected_payments_id != None).order_by(
                BookOrder.id).all()
    return jsonify({
        "orders": iterate_models(orders),
        "debt": collected_books.debt if collected_books else 0
    })


@app.route(f'{api}/deleted_orders')
@jwt_required()
def deleted_orders():
    orders = BookOrder.query.filter(BookOrder.deleted == True).order_by(
        BookOrder.id).all()
    return jsonify({
        "orders": iterate_models(orders)
    })


@app.route(f'{api}/book', methods=['POST', 'GET'])
def book():
    if request.method == "POST":

        return handle_post_request()
    else:
        return handle_get_request()


@app.route(f'{api}/book_inside/<int:book_id>', methods=['POST', 'GET', 'DELETE'])
def book_inside(book_id):
    book = Book.query.filter(Book.id == book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if request.method == "DELETE":
        delete_book_images(book)
        book.delete()
        return jsonify({"success": True, "message": "Book deleted"})

    if request.method == "POST":
        update_book(book)
        return jsonify({"book": book.convert_json(), "success": True})

    # For GET requests, simply return the book's details
    return jsonify({"book": book.convert_json(), "success": True})


@app.route(f'{api}/del_img_book/<int:book_id>/<int:img_num>')
@jwt_required()
def del_img_book(book_id, img_num):
    book = Book.query.filter(Book.id == book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Mapping of img_num to book image attributes
    img_attrs = {0: 'img', 1: 'img2', 2: 'img3'}

    # Get the attribute name for the specified img_num
    img_attr = img_attrs.get(img_num)

    if img_attr:
        img_url = getattr(book, img_attr, None)
        if img_url and os.path.isfile(f'frontend/build/{img_url}'):
            os.remove(f'frontend/build/{img_url}')
        setattr(book, img_attr, "")  # Clear the image attribute
        db.session.commit()
        if img_num == 0:
            if not book.img and book.img2:
                book.img = book.img2
                book.img2 = ""
            elif not book.img and book.img3:
                book.img = book.img3
                book.img3 = ""
        if img_num == 1:
            if not book.img2 and book.img3:
                book.img2 = book.img3
                book.img3 = ""
        db.session.commit()
        return jsonify({"msg": "Rasm o'chirildi", "success": True})
    else:
        return jsonify({"error": "Invalid image number"}), 400


@app.route(f'{api}/book_overhead2/', defaults={"type_info": None}, methods=['POST', 'GET', "DELETE"])
@app.route(f'{api}/book_overhead2/<type_info>', methods=['POST', 'GET', "DELETE"])
@jwt_required()
def book_overhead(type_info):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    editor_balances = EditorBalance.query.filter(EditorBalance.account_period_id == accounting_period.id).order_by(
        EditorBalance.id).all()
    if request.method == "POST":
        current_year = datetime.now().year
        name = get_json_field('typeItem')
        cost = get_json_field('price')
        payment_type = get_json_field('typePayment')
        month = get_json_field('month')
        calendar_month = str(current_year) + "-" + str(month)
        day = get_json_field('day')
        day = str(current_year) + "-" + str(month) + "-" + str(day)
        month = datetime.strptime(calendar_month, "%Y-%m")
        day = datetime.strptime(day, "%Y-%m-%d")
        calendar_month = CalendarMonth.query.filter(CalendarMonth.date == month).first()
        calendar_day = CalendarDay.query.filter(CalendarDay.date == day).first()
        payment_type = PaymentTypes.query.filter(PaymentTypes.id == payment_type).first()
        editor_balance = check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
        overhead_add = BookOverhead(name=name, cost=cost, account_period_id=accounting_period.id,
                                    calendar_day=calendar_day.id, payment_type_id=payment_type.id,
                                    calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                    editor_balance_id=editor_balance.id)
        overhead_add.add()
        update_balance_editor()
        return jsonify({
            "msg": "Qoshildi",
            "success": True,
            "book": overhead_add.convert_json(),
            "editor_balance": iterate_models(editor_balances)
        })
    if type_info == "archive":
        overheads = BookOverhead.query.filter(
            or_(BookOverhead.status == False, BookOverhead.status == None)).order_by(
            BookOverhead.id).all()
    else:

        overheads = BookOverhead.query.filter(BookOverhead.account_period_id == accounting_period.id).filter(
            or_(BookOverhead.status == False, BookOverhead.status == None)).order_by(
            BookOverhead.id).all()

    return jsonify({
        "data": {
            "overhead_tools": old_current_dates(),
            "typeOfMoney": "overhead",
            "book": iterate_models(overheads),
            "editor_balance": iterate_models(editor_balances)
        }
    })


@app.route(f'{api}/deleted_book_overhead2/', defaults={"type_info": None})
@app.route(f'{api}/deleted_book_overhead2/<type_info>')
def deleted_book_overhead(type_info):
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()

    if type_info == "archive":
        overheads = BookOverhead.query.filter(BookOverhead.status == True).order_by(
            BookOverhead.id).all()

    else:
        overheads = BookOverhead.query.filter(BookOverhead.account_period_id == accounting_period.id,
                                              BookOverhead.status == True).order_by(
            BookOverhead.id).all()

    return jsonify({
        "data": {
            "typeOfMoney": "overhead",
            "book": iterate_models(overheads)
        }
    })


@app.route(f'{api}/change_overhead_book/<int:overhead>/<type_id>')
@jwt_required()
def change_overhead_book(overhead, type_id):
    """
    change payment_type_id in Overhead table
    :param overhead: Overhead table primary key
    :param type_id: Payment Type table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    payment_type = PaymentTypes.query.filter(PaymentTypes.name == type_id).first()

    EditorBalance.query.filter(EditorBalance.calendar_month == calendar_month.id,
                               EditorBalance.calendar_year == calendar_year.id,
                               EditorBalance.account_period_id == accounting_period.id).all()
    editor_balance = EditorBalance.query.filter(EditorBalance.calendar_month == calendar_month.id,
                                                EditorBalance.calendar_year == calendar_year.id,
                                                EditorBalance.account_period_id == accounting_period.id,
                                                EditorBalance.payment_type_id == payment_type.id).first()
    BookOverhead.query.filter(BookOverhead.id == overhead).update({
        "payment_type_id": payment_type.id,
        "editor_balance_id": editor_balance.id
    })
    db.session.commit()
    editor_balance = EditorBalance.query.filter(EditorBalance.account_period_id == accounting_period.id).order_by(
        EditorBalance.id).all()
    check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
    update_balance_editor()
    return jsonify({
        "success": True,
        "msg": "Xarajat summa turi o'zgartirildi",
        "type": payment_type.name,
        "editor_balance": iterate_models(editor_balance)
    })


@app.route(f'{api}/delete_book_overhead/<overhead_id>', methods=['POST'])
@jwt_required()
def delete_book_overhead(overhead_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    reason = get_json_field('otherReason')
    book_overhead_get = BookOverhead.query.filter(BookOverhead.id == overhead_id).first()
    book_overhead_get.status = True
    book_overhead_get.reason = reason

    db.session.commit()
    payment_type = PaymentTypes.query.filter(PaymentTypes.id == book_overhead_get.payment_type_id).first()
    check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
    update_balance_editor()
    editor_balance = EditorBalance.query.filter(EditorBalance.account_period_id == accounting_period.id).order_by(
        EditorBalance.id).all()
    return jsonify({
        "msg": "Xarajat o'chirildi",
        "success": True,
        "editor_balance": iterate_models(editor_balance)
    })


@app.route(f'{api}/editor_balance_history2')
@jwt_required()
def editor_balance_history():
    editor_balances = EditorBalance.query.order_by(EditorBalance.id).all()
    years = []
    for year in editor_balances:
        if year.year.date.strftime("%Y") not in years:
            years.append(year.year.date.strftime("%Y"))
    return jsonify({
        "data": {
            "years": years,
            "editor_balances": iterate_models(editor_balances)
        }
    })
