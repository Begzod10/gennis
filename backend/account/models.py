from backend.models.models import Column, Integer, ForeignKey, String, Boolean, relationship, DateTime, db, \
    contains_eager, BigInteger, JSON
from backend.group.models import Groups
from backend.student.models import Students
from backend.models.models import func


class Category(db.Model):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    img = Column(String)
    number_category = Column(String)
    capitals = relationship("Capital", backref="capital_category", order_by="Capital.id", lazy="select")

    def convert_json(self, location_id=None):
        addition_categories = ConnectedCategory.query.filter(
            ConnectedCategory.main_category_id == self.id).order_by(ConnectedCategory.id).all()
        addition_categories2 = ConnectedCategory.query.filter(
            ConnectedCategory.addition_category_id == self.id).order_by(ConnectedCategory.id).all()
        all_capex_down = \
            db.session.query(func.sum(Capital.total_down_cost).filter(Capital.category_id == self.id,
                                                                      Capital.location_id == location_id,
                                                                      Capital.deleted != True)).first()[0]
        info = {
            "id": self.id,
            'name': self.name,
            "img": self.img,
            "is_delete": True if not addition_categories or not addition_categories2 else False,
            "number_category": self.number_category,
            "is_sub": True if addition_categories2 else False,
            'addition_categories': [addition_category.convert_json() for addition_category in addition_categories],
            "capitals": [],
            "total_down_cost": all_capex_down
        }
        for capital in self.capitals:
            if not capital.deleted:
                info['capitals'].append(capital.convert_json(location_id=location_id))
        return info


class ConnectedCategory(db.Model):
    __tablename__ = "connected_category"
    id = Column(Integer, primary_key=True)
    addition_category_id = Column(Integer, ForeignKey('category.id'))
    main_category_id = Column(Integer, ForeignKey('category.id'))
    first = db.relationship("Category", foreign_keys=[addition_category_id])
    second = db.relationship("Category", foreign_keys=[main_category_id])

    def convert_json(self):
        addition_categories = ConnectedCategory.query.filter(
            ConnectedCategory.main_category_id == self.addition_category_id).order_by(ConnectedCategory.id).all()
        info = {
            "id": self.first.id,
            'name': self.first.name,
            'number_category': self.first.number_category,
            "img": self.first.img,
            "is_delete": True if not self.first else False,
            "is_sub": True if self.second else False,
            'addition_categories': [addition_category.convert_json() for addition_category in addition_categories]
        }
        return info


class PaymentTypes(db.Model):
    __tablename__ = "paymenttypes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    student_payments = relationship('StudentPayments', backref="payment_type", order_by="StudentPayments.id")
    teacher_salaries = relationship('TeacherSalaries', backref="payment_type", order_by="TeacherSalaries.id")
    overhead_data = relationship('Overhead', backref="payment_type", order_by="Overhead.id")
    accounting = relationship("AccountingInfo", backref="payment_type", order_by="AccountingInfo.id")
    staff_salaries = relationship("StaffSalaries", backref="payment_type", order_by="StaffSalaries.id")
    capital = relationship("CapitalExpenditure", backref="payment_type", order_by="CapitalExpenditure.id")
    deleted_payments = relationship("DeletedStudentPayments", backref="payment_type")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="payment_type")
    deleted_capital = relationship("DeletedCapitalExpenditure", backref="payment_type")
    deleted_overhead = relationship("DeletedOverhead", backref="payment_type")
    deleted_staff_salaries = relationship("DeletedStaffSalaries", backref="payment_type")
    old_id = Column(Integer)
    center_balances_overheads = relationship("CenterBalanceOverhead", backref="payment_type", lazy="select",
                                             order_by="CenterBalanceOverhead.id")
    book_overhead = relationship("BookOverhead", backref="payment_type", order_by="BookOverhead.id", lazy="select")
    branch_payments = relationship("BranchPayment", backref="payment_type", order_by="BranchPayment.id", lazy="select")
    editor_balance = relationship("EditorBalance", backref="payment_type", order_by="EditorBalance.id", lazy="select")
    collected_payment = relationship("CollectedBookPayments", backref="payment_type",
                                     order_by="CollectedBookPayments.id",
                                     lazy="select")
    capitals = relationship("Capital", backref="payment_type", order_by="Capital.id", lazy="select")


class StudentPayments(db.Model):
    __tablename__ = "studentpayments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    payment_sum = Column(Integer)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    payment = Column(Boolean)
    by_who = Column(Integer, ForeignKey("users.id"))
    payment_data = Column(DateTime)
    old_id = Column(Integer)


class StudentCharity(db.Model):
    __tablename__ = "studentcharity"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    discount = Column(Integer)
    group_id = Column(Integer, ForeignKey('groups.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    old_id = Column(Integer)


class BookPayments(db.Model):
    __tablename__ = "book_payments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    payment_sum = Column(Integer)
    book_order_id = Column(Integer, ForeignKey('book_order.id'))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()


class UserBooks(db.Model):
    __tablename__ = "user_books"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    payment_sum = Column(Integer)
    book_order_id = Column(Integer, ForeignKey('book_order.id'))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    salary_location_id = Column(Integer, ForeignKey("teachersalary.id"))
    salary_id = Column(Integer, ForeignKey('staffsalary.id'))

    def convert_json(self):
        return {
            "id": self.id,
            "salary": self.payment_sum,
            "reason": "kitobga",
            "date": self.day.date.strftime("%Y-%m-%d"),
            "status": True
        }

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CenterBalance(db.Model):
    __tablename__ = "center_balance"
    id = Column(Integer, primary_key=True)
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    exist_money = Column(Integer)
    taken_money = Column(Integer)
    total_money = Column(Integer)
    type_income = Column(String)
    orders = relationship("CenterOrders", lazy="select", backref="balance", order_by="CenterOrders.id")
    overheads = relationship("CenterBalanceOverhead", lazy="select", backref="balance",
                             order_by="CenterBalanceOverhead.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "month": self.month.date.strftime("%Y-%m"),
            "year": self.year.date.strftime("%Y"),
            "location": self.location.convert_json(),
            "exist_money": self.exist_money,
            "taken_money": self.taken_money,
            "total_money": self.total_money,
            "type_income": self.type_income,
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class EditorBalance(db.Model):
    __tablename__ = "editor_balance"
    id = Column(Integer, primary_key=True)
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    balance = Column(Integer, default=0)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    payments_sum = Column(Integer)
    overheads_sum = Column(Integer)
    payments = relationship("BranchPayment", lazy="select", backref="editor_balance", order_by="BranchPayment.id")
    overheads = relationship("BookOverhead", lazy="select", backref="editor_balance", order_by="BookOverhead.id")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "balance": self.balance,
            "id": self.id,
            "payment_type": {
                "id": self.payment_type.id,
                "name": self.payment_type.name
            },
            "payments_sum": self.payments_sum,
            "overheads_sum": self.overheads_sum,
            "year": self.year.date.strftime("%Y"),
            "month": self.month.date.strftime("%m"),
        }


class BranchPayment(db.Model):
    __tablename__ = "branch_payment"
    id = Column(Integer, primary_key=True)
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    editor_balance_id = Column(Integer, ForeignKey('editor_balance.id'))
    book_order_id = Column(Integer, ForeignKey('book_order.id'))
    payment_sum = Column(Integer)

    def add(self):
        db.session.add(self)
        db.session.commit()


class CenterOrders(db.Model):
    __tablename__ = "center_orders"
    id = Column(Integer, primary_key=True)
    balance_id = Column(Integer, ForeignKey('center_balance.id'))
    order_id = Column(Integer, ForeignKey('book_order.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CollectedBookPayments(db.Model):
    __tablename__ = "collected_book_payments"
    id = Column(Integer, primary_key=True)
    book_orders = db.relationship("BookOrder", backref="collected", order_by="BookOrder.id", lazy="select")
    debt = Column(Integer, default=0)
    location_id = Column(Integer, ForeignKey('locations.id'))
    status = Column(Boolean, default=False)
    created_date = Column(Integer, ForeignKey('calendarday.id'))
    received_date = Column(Integer, ForeignKey('calendarday.id'))
    created = relationship("CalendarDay", foreign_keys=[created_date])
    received = relationship("CalendarDay", foreign_keys=[received_date])
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))

    def convert_json(self, entire=False):
        received = None
        if self.received:
            received = self.received.date.strftime("%Y-%m-%d")
        payment = None
        if self.payment_type:
            payment = {
                "id": self.payment_type.id,
                "name": self.payment_type.name,
            }

        return {
            "id": self.id,
            "debt": self.debt,
            "status": self.status,
            "created": self.created.date.strftime("%Y-%m-%d"),
            "received": received,
            "month": self.month.date.strftime("%Y-%m"),
            "year": self.year.date.strftime("%Y"),
            "payment_type": payment
        }

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CenterBalanceOverhead(db.Model):
    __tablename__ = "center_balance_overhead"
    id = Column(Integer, primary_key=True)
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    balance_id = Column(Integer, ForeignKey('center_balance.id'))
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    payment_sum = Column(Integer)
    reason = Column(String)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted = Column(Boolean, default=False)
    location_id = Column(Integer, ForeignKey('locations.id'))

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "day": self.day.date.strftime("%Y-%m-%d"),
            "payment_type": {
                "id": self.payment_type.id,
                "name": self.payment_type.name,
            },
            "payment_sum": self.payment_sum,
            "reason": self.reason

        }

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class DeletedBookPayments(db.Model):
    __tablename__ = "deleted_book_payments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    payment_sum = Column(Integer)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))


class DeletedStudentPayments(db.Model):
    __tablename__ = "deletedstudentpayments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    payment_sum = Column(Integer)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    payment = Column(Boolean)
    deleted_date = Column(DateTime)
    reason = Column(String)


class TeacherSalaries(db.Model):
    __tablename__ = "teachersalaries"
    id = Column(Integer, primary_key=True)
    payment_sum = Column(Integer)
    reason = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    salary_location_id = Column(Integer, ForeignKey("teachersalary.id"))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    by_who = Column(Integer, ForeignKey("users.id"))
    old_id = Column(Integer)
    order_id = Column(Integer, ForeignKey('book_order.id'))


class DeletedTeacherSalaries(db.Model):
    __tablename__ = "deletedteachersalaries"
    id = Column(Integer, primary_key=True)
    payment_sum = Column(Integer)
    reason = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    group_id = Column(Integer, ForeignKey("groups.id"))
    salary_location_id = Column(Integer, ForeignKey("teachersalary.id"))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted_date = Column(DateTime)
    reason_deleted = Column(String)


class StaffSalaries(db.Model):
    __tablename__ = "staffsalaries"
    id = Column(Integer, primary_key=True)
    payment_sum = Column(Integer)
    reason = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    salary_id = Column(Integer, ForeignKey('staffsalary.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    profession_id = Column(Integer, ForeignKey("professions.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    by_who = Column(Integer, ForeignKey("users.id"))
    old_id = Column(Integer)
    order_id = Column(Integer, ForeignKey('book_order.id'))


class DeletedStaffSalaries(db.Model):
    __tablename__ = "deletedstaffsalaries"
    id = Column(Integer, primary_key=True)
    payment_sum = Column(Integer)
    reason = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    salary_id = Column(Integer, ForeignKey('staffsalary.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    profession_id = Column(Integer, ForeignKey("professions.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted_date = Column(DateTime)
    reason_deleted = Column(String)


class Overhead(db.Model):
    __tablename__ = "overhead"
    id = Column(Integer, primary_key=True)
    item_sum = Column(Integer)
    item_name = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    by_who = Column(Integer, ForeignKey("users.id"))
    old_id = Column(Integer)


class DeletedOverhead(db.Model):
    __tablename__ = "deletedoverhead"
    id = Column(Integer, primary_key=True)
    item_sum = Column(Integer)
    item_name = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted_date = Column(DateTime)
    reason = Column(String)


class CapitalCategory(db.Model):
    __tablename__ = "capital_category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)

    def convert_json(self, entire=False):
        info = {
            "name": self.name,
            "number": self.number,
            "capitals": []
        }
        for capital in self.capitals:
            info['capitals'].append(capital.convert_json())
        return info

    def add(self):
        db.session.add(self)
        db.session.commit()


class Capital(db.Model):
    __tablename__ = "capital"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(String)
    price = Column(BigInteger)
    term = Column(Integer)
    img = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    total_down_cost = Column(BigInteger)
    deleted = Column(Boolean, default=False)
    term_info = relationship("CapitalTerm", backref="capital", order_by="CapitalTerm.id", lazy="select")

    def convert_json(self, entire=False, location_id=None):

        if location_id and self.location_id == location_id:
            return {
                "id": self.id,
                "name": self.name,
                "number": self.number,
                "price": self.price,
                "term": self.term,
                "category": {
                    "id": self.capital_category.id,
                    "name": self.capital_category.name,

                },
                "total_down_cost": self.total_down_cost,
                "img": self.img,
                "day": self.day.date.strftime("%d"),
                "month": self.day.date.strftime("%m"),
                "year": self.day.date.strftime("%Y"),
                "payment_type": {
                    "id": self.payment_type.id,
                    "name": self.payment_type.name,
                }

            }
        else:
            return

    def add(self):
        db.session.add(self)
        db.session.commit()


class CapitalTerm(db.Model):
    __tablename__ = "capital_term"
    id = Column(Integer, primary_key=True)
    capital_id = Column(Integer, ForeignKey('capital.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    down_cost = Column(Integer)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "capital": self.capital.convert_json(),
            "date": self.month.date.strftime("%Y-%m"),
            "down_cost": -self.down_cost,
            "id": self.id
        }


class CapitalExpenditure(db.Model):
    __tablename__ = "capital_expenditure"
    id = Column(Integer, primary_key=True)
    item_sum = Column(Integer)
    item_name = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    by_who = Column(Integer, ForeignKey("users.id"))
    old_id = Column(Integer)


class DeletedCapitalExpenditure(db.Model):
    __tablename__ = "deleted_capital"
    id = Column(Integer, primary_key=True)
    item_sum = Column(Integer)
    item_name = Column(String)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted_date = Column(DateTime)
    reason = Column(String)


class AccountingInfo(db.Model):
    __tablename__ = "accountinginfo"
    id = Column(Integer, primary_key=True)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    location_id = Column(Integer, ForeignKey('locations.id'))
    all_payments = Column(Integer, default=0)
    all_teacher_salaries = Column(Integer, default=0)
    all_staff_salaries = Column(Integer, default=0)
    all_overhead = Column(Integer, default=0)
    all_capital = Column(Integer, default=0)
    all_charity = Column(Integer, default=0)
    current_cash = Column(Integer, default=0)
    old_cash = Column(Integer, default=0)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()


class OtherInfo(db.Model):
    __tablename__ = "other_info"
    id = Column(Integer, primary_key=True)
    all_discount = Column(Integer, default=0)
    debtors_red_num = Column(Integer, default=0)
    debtors_yel_num = Column(Integer, default=0)
    registered_students = Column(Integer, default=0)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    location_id = Column(Integer, ForeignKey('locations.id'))

    def add(self):
        db.session.add(self)
        db.session.commit()


class TeacherSalary(db.Model):
    __tablename__ = "teachersalary"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    total_salary = Column(Integer)
    remaining_salary = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    status = Column(Boolean, default=False)

    teacher_cash = relationship('TeacherSalaries', backref="salary", order_by="TeacherSalaries.id")
    deleted_teacher_salary = relationship("DeletedTeacherSalaries", backref="salary",
                                          order_by="DeletedTeacherSalaries.id")
    taken_money = Column(Integer)
    old_id = Column(Integer)


class TeacherBlackSalary(db.Model):
    __tablename__ = "teacher_black_salary"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    total_salary = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    salary_id = Column(Integer, ForeignKey('teachersalary.id'))
    payment_id = Column(Integer, ForeignKey('studentpayments.id'))
    status = Column(Boolean, default=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        student = Students.query.filter(Students.id == self.student_id).first()
        for gr in student.group:
            if gr.teacher_id == self.teacher_id:
                group_name = gr.name
        group = Groups.query.filter(Groups.teacher_id == self.teacher_id).first()
        return {
            "id": self.id,
            "total_salary": self.total_salary,
            "student_name": self.student.user.name,
            "student_surname": self.student.user.surname,
            "student_id": self.student.id,
            "group_name": [gr.name if gr.teacher_id == group.teacher_id else "" for gr in student.group],
            "month": self.month.date.strftime("%Y-%m")

        }


class StaffSalary(db.Model):
    __tablename__ = "staffsalary"
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id'))
    total_salary = Column(Integer)
    remaining_salary = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    status = Column(Boolean, default=False)
    taken_money = Column(Integer)
    staff_given_salary = relationship("StaffSalaries", backref="staff_salary", order_by="StaffSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="staff_salary",
                                        order_by="DeletedStaffSalaries.id")
    old_id = Column(Integer)
