from backend.models.models import CenterBalance, CalendarMonth, EditorBalance, AccountingPeriod
from app import db, contains_eager, desc
from backend.functions.utils import find_calendar_date


class OrderFunctions:
    def __init__(self, balance_id):
        self.balance_id = balance_id

    def update_balance(self):
        center_balance = CenterBalance.query.filter(CenterBalance.id == self.balance_id).first()
        balance = 0
        overhead = 0
        for book_order in center_balance.orders:
            if book_order.order.deleted == False:
                if book_order.order.count:
                    share_price = book_order.order.count * book_order.order.book.share_price
                else:
                    share_price = book_order.order.book.share_price
                balance += share_price
        for balance_overhead in center_balance.overheads:
            if balance_overhead.deleted == False:
                overhead += balance_overhead.payment_sum
        center_balance.total_money = balance
        center_balance.taken_money = overhead
        center_balance.exist_money = balance - overhead
        db.session.commit()


def update_balance_editor():
    calendar_year, calendar_month, calendar_day = find_calendar_date()

    accounting_period = db.session.query(AccountingPeriod).join(AccountingPeriod.month).options(
        contains_eager(AccountingPeriod.month)).order_by(desc(CalendarMonth.id)).first()
    editor_balances = EditorBalance.query.filter(EditorBalance.calendar_month == calendar_month.id,
                                                 EditorBalance.calendar_year == calendar_year.id,
                                                 EditorBalance.account_period_id == accounting_period.id).all()

    for editor_balance in editor_balances:
        balance = 0
        overhead = 0
        for payment in editor_balance.payments:
            balance += int(payment.order.book.own_price)

        for editor_overhead in editor_balance.overheads:
            if editor_overhead.status == False:
                overhead += editor_overhead.cost
        editor_balance.balance = balance - overhead
        editor_balance.payments_sum = balance
        editor_balance.overheads_sum = overhead
        db.session.commit()


def check_editor_balance(calendar_month, calendar_year, accounting_period, payment_type):
    editor_balance = EditorBalance.query.filter(EditorBalance.calendar_month == calendar_month.id,
                                                EditorBalance.calendar_year == calendar_year.id,
                                                EditorBalance.account_period_id == accounting_period.id,
                                                EditorBalance.payment_type_id == payment_type.id).first()

    if not editor_balance:
        editor_balance = EditorBalance(calendar_month=calendar_month.id,
                                       calendar_year=calendar_year.id,
                                       account_period_id=accounting_period.id,
                                       payment_type_id=payment_type.id)
        editor_balance.add()

    return editor_balance
