from app import app, jsonify, db, desc, contains_eager, CenterOrders, CalendarMonth, BookOrder, request
from backend.models.models import Users, CenterBalance, CenterBalanceOverhead, PaymentTypes, AccountingPeriod, \
    BranchPayment, CollectedBookPayments, CalendarYear

from .class_model import check_editor_balance, OrderFunctions, update_balance_editor
from backend.functions.utils import get_json_field, api, iterate_models, find_calendar_date
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/campus_account/<type_balance>/', defaults={"location_id": None})
@app.route(f'{api}/campus_account/<type_balance>/<int:location_id>')
@jwt_required()
def campus_account(type_balance, location_id):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    if user.role_info.type_role == "admin":
        balance_list = CenterBalance.query.filter(CenterBalance.location_id == user.location_id,
                                                  CenterBalance.type_income == type_balance).order_by(
            CenterBalance.id).all()

        return jsonify({
            "data": iterate_models(balance_list, entire=False)
        })
    else:
        balance_list = CenterBalance.query.filter(CenterBalance.location_id == location_id,
                                                  CenterBalance.type_income == type_balance).order_by(
            CenterBalance.id).all()
        return jsonify({
            "data": iterate_models(balance_list, entire=False)
        })


@app.route(f'{api}/campus_account_inside/<int:balance_id>')
@jwt_required()
def campus_account_inside(balance_id):
    balance = CenterBalance.query.filter(CenterBalance.id == balance_id).first()
    balance_overheads = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.balance_id == balance_id,
                                                           CenterBalanceOverhead.deleted == False).order_by(
        CenterBalanceOverhead.id).all()
    balance_overheads_deleted = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.balance_id == balance_id,
                                                                   CenterBalanceOverhead.deleted == True).order_by(
        CenterBalanceOverhead.id).all()
    return jsonify({
        "data": {
            "month_balance": balance.convert_json(),
            "balance_overheads": iterate_models(balance_overheads),
            "balance_overheads_deleted": iterate_models(balance_overheads_deleted)
        }
    })


@app.route(f'{api}/campus_money/<int:balance_id>', methods=['POST'])
@jwt_required()
def campus_money(balance_id):
    money = int(get_json_field('payment'))
    reason = get_json_field('reason')
    payment_type = int(get_json_field('typePayment'))
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    add = CenterBalanceOverhead(calendar_day=calendar_day.id, calendar_month=calendar_month.id, balance_id=balance_id,
                                calendar_year=calendar_year.id, payment_type_id=payment_type, payment_sum=money,
                                reason=reason, account_period_id=accounting_period.id, location_id=user.location_id)
    add.add()
    order_function = OrderFunctions(balance_id)
    order_function.update_balance()

    return jsonify({
        "msg": "Pul olindi",
        "success": True
    })


@app.route(f'{api}/delete_campus_money/<int:overhead_id>', methods=['POST'])
@jwt_required()
def delete_campus_money(overhead_id):
    reason = get_json_field('otherReason')
    balance_overhead = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.id == overhead_id).first()
    balance_overhead.deleted = True
    balance_overhead.reason = reason
    db.session.commit()
    order_function = OrderFunctions(balance_overhead.balance_id)
    order_function.update_balance()
    return jsonify({
        "msg": "Pul O'chirildi",
        "success": True
    })


@app.route(f'{api}/change_campus_money2/<overhead_id>/<payment_type_id>')
@jwt_required()
def change_campus_money(overhead_id, payment_type_id):
    over = CenterBalanceOverhead.query.filter(CenterBalanceOverhead.id == overhead_id).first()
    over.payment_type_id = payment_type_id
    db.session.commit()
    return jsonify({
        "msg": "Summa turi o'zgartirildi",
        "success": True
    })


@app.route(f'{api}/send_campus_money', methods=['POST'])
@jwt_required()
def send_campus_money():
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    request_get = request.get_json()

    payment_sum = 0
    collected_books = CollectedBookPayments.query.filter(CollectedBookPayments.location_id == user.location_id,
                                                         CollectedBookPayments.status == False).first()
    if not collected_books:
        collected_books = CollectedBookPayments(location_id=user.location_id, created_date=calendar_day.id,
                                                calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                                account_period_id=accounting_period.id)
        collected_books.add()

    book_order = BookOrder.query.filter(BookOrder.id == request_get['order_id']).first()
    book_order.admin_confirm = request_get['admin_confirm']
    db.session.commit()
    if not book_order.admin_confirm:
        if book_order in collected_books.book_orders:
            collected_books.book_orders.remove(book_order)
    else:
        if book_order not in collected_books.book_orders:
            collected_books.book_orders.append(book_order)
            db.session.commit()

    for order in collected_books.book_orders:
        payment_sum += order.book.own_price
    collected_books.debt = -payment_sum
    db.session.commit()
    book_orders = BookOrder.query.filter(BookOrder.location_id == user.location_id,
                                         BookOrder.admin_confirm == True).order_by(BookOrder.id).all()

    return jsonify({
        "msg": "Pul o'tkazildi",
        "success": True,
        "order": iterate_models(book_orders)
    })


@app.route(f'{api}/delete_branch_payment2/<int:payment_id>')
@jwt_required()
def delete_branch_payment(payment_id):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    book_order = BookOrder.query.filter(BookOrder.id == payment_id).first()
    book_order.admin_confirm = False
    collected_books = CollectedBookPayments.query.filter(CollectedBookPayments.location_id == user.location_id,
                                                         CollectedBookPayments.status == False).first()
    if book_order in collected_books.book_orders:
        collected_books.book_orders.remove(book_order)
    # center_order = CenterOrders.query.filter(CenterOrders.order_id == book_order.id).first()
    # center_order_id = center_order.balance_id
    # branch_payment = BranchPayment.query.filter(BranchPayment.book_order_id == payment_id).first()
    #
    # db.session.delete(center_order)
    # db.session.delete(branch_payment)
    # db.session.commit()
    # payment_type = PaymentTypes.query.filter(PaymentTypes.id == branch_payment.payment_type_id).first()
    # order_function = OrderFunctions(center_order_id)
    # order_function.update_balance()
    # check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
    # update_balance_editor()
    return jsonify({
        "msg": "Pul o'chirildi",
        "success": True,
        "order": [book_order.convert_json()]
    })


@app.route(f'{api}/change_branch_money/<payment_id>/<payment_type_id>')
@jwt_required()
def change_branch_money(payment_id, payment_type_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    order = BookOrder.query.filter(BookOrder.id == payment_id).first()
    branch_payment = BranchPayment.query.filter(BranchPayment.book_order_id == order.id).first()
    branch_payment.payment_type_id = payment_type_id

    db.session.commit()
    payment_type = PaymentTypes.query.filter(PaymentTypes.id == branch_payment.payment_type_id).first()
    check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
    update_balance_editor()
    return jsonify({
        "msg": "Summa turi o'zgartirildi",
        "success": True,
        "order": [order.convert_json()]
    })


@app.route(f'{api}/collected_book_payments/<location_id>')
@jwt_required()
def collected_book_payments(location_id):
    book_debts = CollectedBookPayments.query.filter(CollectedBookPayments.location_id == location_id).order_by(
        CollectedBookPayments.id).all()
    month_list = []
    payments_list = []
    for month in book_debts:
        month_list.append(month.calendar_month)
    month_list = list(dict.fromkeys(month_list))
    debt = 0

    for month in month_list:
        book_debt = CollectedBookPayments.query.filter(CollectedBookPayments.calendar_month == month,
                                                       CollectedBookPayments.location_id == location_id,
                                                       ).first()
        calendar_month = CalendarMonth.query.filter(CalendarMonth.id == month).first()
        debt += book_debt.debt
        info = {
            "month": calendar_month.date.strftime("%Y-%m-%d"),
            "month_id": calendar_month.id,
            "debt": debt
        }
        payments_list.append(info)

    return jsonify({
        "data": {
            "debts": payments_list
        }
    })


@app.route(f'{api}/collected_by_month/<int:month_id>')
@jwt_required()
def collected_by_month(month_id):
    book_debts = CollectedBookPayments.query.filter(CollectedBookPayments.calendar_month == month_id).order_by(
        CollectedBookPayments.id).all()

    return jsonify({
        "data": {
            "debt": iterate_models(book_debts)
        }
    })


@app.route(f'{api}/get_center_money/<primary_key>', methods=['POST'])
@jwt_required()
def get_center_money(primary_key):
    identity = get_jwt_identity()
    user = Users.query.filter(Users.user_id == identity).first()
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    book_debts = CollectedBookPayments.query.filter(CollectedBookPayments.id == primary_key).first()
    payment_type_id = get_json_field('typePayment')
    book_debts.status = True
    book_debts.received_date = calendar_day.id
    book_debts.payment_type_id = payment_type_id
    db.session.commit()
    payment_type = PaymentTypes.query.filter(PaymentTypes.id == payment_type_id).first()

    center_balance = CenterBalance.query.filter(CenterBalance.location_id == user.location_id,
                                                CenterBalance.account_period_id == accounting_period.id,
                                                CenterBalance.calendar_month == calendar_month.id,
                                                CenterBalance.calendar_year == calendar_year.id,
                                                CenterBalance.type_income == "book").first()
    if not center_balance:
        center_balance = CenterBalance(location_id=book_debts.location_id,
                                       account_period_id=accounting_period.id,
                                       calendar_month=calendar_month.id,
                                       calendar_year=calendar_year.id,
                                       type_income="book")
        center_balance.add()

    editor_balance = check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
    for order in book_debts.book_orders:
        book_order = BookOrder.query.filter(BookOrder.id == order.id).first()
        payment_branch = BranchPayment.query.filter(BranchPayment.book_order_id == book_order.id).first()
        if book_order.count:
            payment_sum = book_order.count * book_order.book.own_price
        else:
            payment_sum = book_order.book.own_price
        if not payment_branch:
            payment_branch = BranchPayment(calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                                           account_period_id=accounting_period.id, payment_type_id=payment_type_id,
                                           calendar_day=calendar_day.id, location_id=book_order.location_id,
                                           editor_balance_id=editor_balance.id, book_order_id=book_order.id,
                                           payment_sum=payment_sum)
            payment_branch.add()

        center_orders = CenterOrders.query.filter(CenterOrders.balance_id == center_balance.id,
                                                  CenterOrders.order_id == book_order.id).first()
        if not center_orders:
            center_orders = CenterOrders(balance_id=center_balance.id,
                                         order_id=book_order.id)
            center_orders.add()

        order_function = OrderFunctions(center_balance.id)
        order_function.update_balance()

        update_balance_editor()

    return jsonify({
        "msg": "Pul olindi",
        "success": True
    })


@app.route(f'{api}/change_collected_money2/<int:primary_key>/<int:payment_type_id>')
@jwt_required()
def change_collected_money(primary_key, payment_type_id):
    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    book_debts = CollectedBookPayments.query.filter(CollectedBookPayments.id == primary_key).first()
    book_debts.payment_type_id = payment_type_id
    db.session.commit()
    payment_type = PaymentTypes.query.filter(PaymentTypes.id == payment_type_id).first()

    for order in book_debts.book_orders:
        branch_payment = BranchPayment.query.filter(BranchPayment.book_order_id == order.id).first()
        calendar_month = CalendarMonth.query.filter(CalendarMonth.id == branch_payment.calendar_month,
                                                    ).first()
        calendar_year = CalendarYear.query.filter(CalendarYear.id == branch_payment.calendar_year).first()
        editor_balance = check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type)
        branch_payment.payment_type_id = payment_type_id
        branch_payment.editor_balance_id = editor_balance.id
        db.session.commit()

        update_balance_editor()
    return jsonify({
        "success": True,
        "msg": "Xarajat summa turi o'zgartirildi",
        "data": book_debts.convert_json()
    })
