from app import app, db, jsonify, contains_eager, request, desc

from backend.models.models import Overhead, CapitalExpenditure, AccountingPeriod, PaymentTypes, DeletedOverhead, \
    CalendarMonth, CalendarDay, DeletedCapitalExpenditure, Capital, CapitalCategory
from flask_jwt_extended import jwt_required
from backend.functions.utils import get_json_field, find_calendar_date, api, iterate_models
from datetime import datetime
import docx
from .utils import update_capital
import uuid
from docx import Document
from docx.shared import Inches


@app.route(f'{api}/add_overhead/<int:location_id>', methods=['POST'])
@jwt_required()
def add_overhead(location_id):
    """
    add data to Overhead table
    :param location_id: Location table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    account_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    current_year = datetime.now().year
    old_year = datetime.now().year - 1
    month = str(datetime.now().month)
    month_get = get_json_field('month')
    day = get_json_field('day')
    if month_get == "12" and month == "01":
        current_year = old_year
    if not month_get:
        month_get = month

    date_day = str(current_year) + "-" + str(month_get) + "-" + str(day)
    date_month = str(current_year) + "-" + str(month_get)
    date_year = str(current_year)
    date_day = datetime.strptime(date_day, "%Y-%m-%d")
    date_month = datetime.strptime(date_month, "%Y-%m")
    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == date_month).first()
    calendar_day = CalendarDay.query.filter(CalendarDay.date == date_day).first()
    type_of_data = get_json_field('typePayment')
    sum = int(get_json_field('price'))
    name_item = get_json_field('typeItem')
    payment_type = PaymentTypes.query.filter(PaymentTypes.id == type_of_data).first()

    add = Overhead(item_sum=sum, item_name=name_item, payment_type_id=payment_type.id, location_id=location_id,
                   calendar_day=calendar_day.id, calendar_month=calendar_month.id, calendar_year=calendar_year.id,
                   account_period_id=account_period.id)
    db.session.add(add)
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Qo'shimcha xarajat qo'shildi"
    })


@app.route(f'{api}/delete_overhead/<overhead_id>', methods=["POST"])
@jwt_required()
def delete_overhead(overhead_id):
    """
    delete data from Overhead table
    :param overhead_id: Overhead table primary key
    :return:
    """
    reason = get_json_field('otherReason')
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    overhead = Overhead.query.filter(Overhead.id == overhead_id).first()

    deleted_overhead = DeletedOverhead(item_sum=overhead.item_sum, item_name=overhead.item_name,
                                       payment_type_id=overhead.payment_type_id, location_id=overhead.location_id,
                                       calendar_day=overhead.calendar_day, calendar_month=overhead.calendar_month,
                                       calendar_year=overhead.calendar_year,
                                       account_period_id=overhead.account_period_id, deleted_date=calendar_day.date,
                                       reason=reason)
    db.session.add(deleted_overhead)
    db.session.commit()
    db.session.delete(overhead)
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Xarajat o'chirildi"
    })


@app.route(f'{api}/change_overhead/<int:overhead>/<type_id>')
@jwt_required()
def change_overhead(overhead, type_id):
    """
    change payment_type_id in Overhead table
    :param overhead: Overhead table primary key
    :param type_id: Payment Type table primary key
    :return:
    """
    payment_type = PaymentTypes.query.filter(PaymentTypes.name == type_id).first()
    overhead_get = Overhead.query.filter(Overhead.id == overhead).first()

    Overhead.query.filter(Overhead.id == overhead_get.id).update({
        "payment_type_id": payment_type.id
    })
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Xarajat summa turi o'zgartirildi"
    })


@app.route(f'{api}/add_capital/<int:location_id>', methods=["GET", 'POST'])
@jwt_required()
def add_capital(location_id):
    """
    add tada to CapitalExpenditure table
    :param location_id: Location table primary key
    :return:
    """
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    if request.method == "POST":
        account_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
            contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
        current_year = datetime.now().year
        month = get_json_field('month')
        calendar_month = str(current_year) + "-" + str(month)
        day = get_json_field('day')
        day = str(current_year) + "-" + str(month) + "-" + str(day)
        type_of_data = get_json_field('typePayment')
        sum = int(get_json_field('price'))
        name_item = get_json_field('typeItem')
        payment_type = PaymentTypes.query.filter(PaymentTypes.id == type_of_data).first()
        month = datetime.strptime(calendar_month, "%Y-%m")
        day = datetime.strptime(day, "%Y-%m-%d")
        calendar_month = CalendarMonth.query.filter(CalendarMonth.date == month).first()
        calendar_day = CalendarDay.query.filter(CalendarDay.date == day).first()
        add = CapitalExpenditure(item_sum=sum, item_name=name_item, payment_type_id=payment_type.id,
                                 location_id=location_id,
                                 calendar_day=calendar_day.id, calendar_month=calendar_month.id,
                                 calendar_year=calendar_year.id,
                                 account_period_id=account_period.id)
        db.session.add(add)
        db.session.commit()
        return jsonify({
            "success": True,
            "msg": "Qo'shimcha xarajat qo'shildi"
        })


@app.route(f'{api}/delete_capital/<overhead_id>', methods=["POST"])
@jwt_required()
def delete_capital(overhead_id):
    """
    delete data from CapitalExpenditure table
    :param overhead_id: CapitalExpenditure table primary key
    :return:
    """
    reason = get_json_field('otherReason')
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    capital = CapitalExpenditure.query.filter(CapitalExpenditure.id == overhead_id).first()

    deleted_capital = DeletedCapitalExpenditure(item_sum=capital.item_sum, item_name=capital.item_name,
                                                payment_type_id=capital.payment_type_id,
                                                location_id=capital.location_id,
                                                calendar_day=capital.calendar_day,
                                                calendar_month=capital.calendar_month,
                                                calendar_year=capital.calendar_year,
                                                account_period_id=capital.account_period_id,
                                                deleted_date=calendar_day.date,
                                                reason=reason)
    db.session.add(deleted_capital)
    db.session.commit()
    db.session.delete(capital)
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Xarajat o'chirildi"
    })


@app.route(f'{api}/change_capital/<int:overhead>/<type_id>')
@jwt_required()
def change_capital(overhead, type_id):
    """
    change payment_type_id in Overhead table
    :param overhead: CapitalExpenditure table primary key
    :param type_id: Payment Type table primary key
    :return:
    """
    payment_type = PaymentTypes.query.filter(PaymentTypes.name == type_id).first()
    capital_get = CapitalExpenditure.query.filter(CapitalExpenditure.id == overhead).first()

    CapitalExpenditure.query.filter(CapitalExpenditure.id == capital_get.id).update({
        "payment_type_id": payment_type.id
    })
    db.session.commit()

    return jsonify({
        "success": True,
        "msg": "Xarajat summa turi o'zgartirildi"
    })

# @app.route(f'{api}/add_capital_category', methods=['POST'])
# def add_capital_category():
#     category = {
#         "name": get_json_field('name'),
#         "number": get_json_field('number')
#     }
#     capital_category = CapitalCategory(**category)
#     capital_category.add()
#     return jsonify({
#         "msg": f"{get_json_field('name')} kategoriyasi yaratildi",
#         "success": True
#     })
#
#
# @app.route(f'{api}/add_capital/<location_id>', methods=['POST'])
# def add_capital(location_id):
#     calendar_year, calendar_month, calendar_day = find_calendar_date()
#     accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
#         contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
#     capital = {
#         "name": get_json_field('name'),
#         "number": get_json_field('number'),
#         "price": get_json_field('price'),
#         "term": get_json_field('term'),
#         "category_id": get_json_field('category_id'),
#         "location_id": location_id,
#         "calendar_day": calendar_day.id,
#         "account_period_id": accounting_period.id,
#         "payment_type_id": get_json_field('payment_type_id'),
#         "calendar_month": calendar_month.id
#
#     }
#     capital_add = Capital(**capital)
#     capital_add.add()
#     return jsonify({
#         "msg": f"{get_json_field('name')} ro'yxatga qo'shildi",
#         "success": True
#     })
#
#
# @app.route(f'{api}/capitals_info/<int:location_id>')
# def capitals_info(location_id):
#     accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
#         contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
#     update_capital(location_id)
#     capitals = Capital.query.filter(Capital.location_id == location_id,
#                                     Capital.account_period_id == accounting_period.id).order_by(Capital.id).all()
#
#     return jsonify({
#         "capital_list": iterate_models(capitals)
#     })
#
#
# @app.route(f'{api}/get_capital_numbers', methods=['POST'])
# def get_capital_numbers():
#     capital_id_list = get_json_field('capitals')
#     category_id = get_json_field('category_id')
#     category = CapitalCategory.query.filter(CapitalCategory.id == category_id).first()
#     capitals = Capital.query.filter(Capital.id.in_([capital for capital in capital_id_list])).order_by(Capital.id).all()
#     # doc = docx.Document('frontend/build/static/contract_folder/zzz.docx')
#     # id = uuid.uuid1()
#     # user_id = id.hex[0:15]
#     # doc.paragraphs[0].text = f"{category.number}"
#     # print(doc.paragraphs[1])
#     # num = 1
#     # for capital in capitals:
#     #     num += 1
#     #     doc.paragraphs[num].text = f"{capital.number}"
#     #     print(capital)
#     # doc.save(
#     #     f"frontend/build/static/contract_folder/{category.name}.docx")
#
#     document = Document()
#
#     document.add_heading(f'{category.name} ga kiruvchi buyumlar:', 0)
#
#     table = document.add_table(rows=len(capital_id_list) - 1, cols=2)
#     hdr_cells = table.rows[0].cells
#     hdr_cells[0].text = 'Name'
#     hdr_cells[1].text = 'Number'
#     num = 0
#     for capital in capitals:
#         row_cells = table.add_row().cells
#         row_cells[0].text = capital.name
#         row_cells[1].text = capital.number
#     document.add_page_break()
#
#     document.save('frontend/build/static/contract_folder/demo.docx')
#     return jsonify({
#         "msg": "Fayl yaratildi",
#         "file": "frontend/build/static/contract_folder/{category.name}.docx"
#     })
