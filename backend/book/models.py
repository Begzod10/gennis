from backend.models.models import Column, Integer, ForeignKey, String, Boolean, relationship, db



class Book(db.Model):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    price = Column(Integer)
    img = Column(String)
    img2 = Column(String)
    img3 = Column(String)
    own_price = Column(Integer)
    share_price = Column(Integer)
    orders = relationship('BookOrder', backref="book", order_by="BookOrder.id", lazy="select")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def convert_json(self, entire=False):
        img_list = []
        if self.img:
            info = {
                "index": 0,
                "img": self.img
            }
            img_list.append(info)
        if self.img2:
            info = {
                "index": 1,
                "img": self.img2
            }
            img_list.append(info)
        if self.img3:
            info = {
                "index": 2,
                "img": self.img3
            }
            img_list.append(info)
        price = 0
        if self.price:
            price = int(self.price)

        own_price = 0
        if self.own_price:
            own_price = int(self.own_price)

        share_price = 0
        if self.share_price:
            share_price = int(self.share_price)
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "price": price,
            "images": img_list,
            "own_price": own_price,
            "share_price": share_price
        }

    def show_orders(self):
        info = {
            "book": self.convert_json(),
            "orders": []
        }
        for order in self.orders:
            info['orders'].append(order.convert_json())
        return info


class BookOrder(db.Model):
    __tablename__ = "book_order"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    editor_confirm = Column(Boolean, default=False)
    admin_confirm = Column(Boolean, default=False)
    book_id = Column(Integer, ForeignKey('book.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    accounting_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    center_order = relationship('CenterOrders', uselist=False, lazy="select", backref="order",
                                order_by="CenterOrders.id")
    branch_payment = relationship('BranchPayment', uselist=False, lazy="select", backref="order",
                                  order_by="BranchPayment.id")
    book_payments = relationship("BookPayments", backref="order", uselist=False)
    collected_payments_id = Column(Integer, ForeignKey('collected_book_payments.id'))
    deleted = Column(Boolean, default=False)
    reason = Column(String)
    count = Column(Integer)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        if self.student:
            id = self.student.user.id
            name = self.student.user.name
            surname = self.student.user.surname
            role = "O'quvchi"
        elif self.teacher:
            id = self.teacher.user.id
            name = self.teacher.user.name
            surname = self.teacher.user.surname
            role = "O'qituvchi"
        else:
            id = self.user.id
            name = self.user.name
            surname = self.user.surname
            role = "Ishchi"
        group_id = None
        group_name = None
        if self.group:
            group_id = self.group.id
            group_name = self.group.name
        payment_type = None
        delete_order = False
        if self.collected:
            delete_order = self.collected.status
        if self.branch_payment:
            payment_type = {
                "id": self.branch_payment.payment_type.id,
                "name": self.branch_payment.payment_type.name,
            }
        return {
            "location": {
                "id": self.location.id,
                "name": self.location.name
            },
            "date": self.day.date.strftime("%Y-%m-%d"),
            "id": self.id,
            "user_id": id,
            "name": name,
            "surname": surname,
            "group": {
                "id": group_id,
                "name": group_name,
            },
            "role": role,
            "admin_confirm": self.admin_confirm,
            "editor_confirm": self.editor_confirm,
            "paid": self.admin_confirm,
            "book": self.book.convert_json(),
            "payment_type": payment_type,
            "deleted": self.deleted,
            "reason": self.reason,
            "delete_order": delete_order
        }


class BookOverhead(db.Model):
    __tablename__ = "book_overhead"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cost = Column(Integer)
    payment_type_id = Column(Integer, ForeignKey('paymenttypes.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    editor_balance_id = Column(Integer, ForeignKey('editor_balance.id'))
    status = Column(Boolean, default=False)
    reason = Column(String)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.cost,
            "payment_type": {
                "id": self.payment_type.id,
                "name": self.payment_type.name
            },
            "typePayment": self.payment_type.name,
            "date": self.day.date.strftime("%Y-%m-%d"),
            "calendar_day": self.calendar_day,
            "calendar_month": self.calendar_month,
            "calendar_year": self.calendar_year,
        }

    def add(self):
        db.session.add(self)
        db.session.commit()
