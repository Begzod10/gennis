import requests
from app import app
from backend.models.models import CollectedBookPayments, CenterBalance, CenterBalanceOverhead, Book, \
    BookOrder, BookOverhead, EditorBalance, UserBooks, BranchPayment
import os


def transfer_user_book():
    with app.app_context():
        user_books = UserBooks.query.order_by(UserBooks.id).all()
        for user_book in user_books:
            info = {
                "user": user_book.user_id,
                "book_order": user_book.book_order_id,
                "branch": user_book.location_id,
                "teacher_salary": user_book.salary_location_id,
                "user_salary": user_book.salary_id,
                "date": user_book.day.date.strftime("%Y-%m-%d"),
                "payment_sum": user_book.payment_sum,
                'old_id': user_book.id
            }
            url = 'http://localhost:8000/Transfer/books/create_user_book/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_book_overhead(token):
    with app.app_context():
        editor_balance_url = 'http://localhost:8000/Books/editor_balance_list/'
        y = requests.get(url=editor_balance_url, headers={'Authorization': f"JWT {token}"})
        payment_types_url = 'http://localhost:8000/Payments/payment-types/'
        z = requests.get(url=payment_types_url, headers={'Authorization': f"JWT {token}"})
        book_overheads = BookOverhead.query.order_by(BookOverhead.id).all()
        for book_overhead in book_overheads:
            info = {
                "editor_balance": next((editor_balance['id'] for editor_balance in y.json()['editorbalances'] if
                                        editor_balance['old_id'] == book_overhead.editor_balance_id), 0),
                "payment_type": next((payment_type['id'] for payment_type in z.json()['paymenttypes'] if
                                      payment_type['old_id'] == book_overhead.payment_type_id), 0),
                "price": book_overhead,
                "name": book_overhead,
                "deleted_reason": book_overhead,
                "old_id": book_overhead.id
            }
            url = 'http://localhost:8000/Books/book_overhead_create/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_branch_payment():
    with app.app_context():
        branch_payments = BranchPayment.query.order_by(BranchPayment.id).all()
        for branch_payment in branch_payments:
            info = {
                "book_order": branch_payment.book_order_id,
                "editor_balance": branch_payment.editor_balance_id,
                "branch": branch_payment.location_id,
                "payment_type": branch_payment.payment_type_id,
                "payment_sum": branch_payment.payment_sum,
                "old_id": branch_payment.id
            }
            url = 'http://localhost:8000/Transfer/books/create_branch_payment/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_editor_balance():
    with app.app_context():
        editor_balances = EditorBalance.query.order_by(EditorBalance.id).all()
        for editor_balance in editor_balances:
            info = {
                "payment_type": editor_balance.payment_type_id,
                "balance": editor_balance.balance,
                "payment_sum": editor_balance.payments_sum,
                "overhead_sum": editor_balance.overheads_sum,
                "old_id": editor_balance.id
            }
            url = 'http://localhost:8000/Transfer/books/create_editor_balance/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_balance_overhead():
    with app.app_context():
        balance_overheads = CenterBalanceOverhead.query.order_by(CenterBalanceOverhead.id).all()
        for balance_overhead in balance_overheads:
            info = {
                "balance": balance_overhead.balance_id,
                "branch": balance_overhead.location_id,
                "payment_type": balance_overhead.payment_type_id,
                "overhead_sum": balance_overhead.payment_sum,
                "reason": balance_overhead.reason,
                "deleted": balance_overhead.deleted,
                "day": balance_overhead.day.date.strftime("%Y-%m-%d"),
                "old_id": balance_overhead.id
            }
            url = 'http://localhost:8000/Transfer/books/create_balance_overhead/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_center_balance():
    with app.app_context():
        center_balances = CenterBalance.query.order_by(CenterBalance.id).all()
        for center_balance in center_balances:
            info = {
                "branch": center_balance.location_id,
                "total_money": center_balance.total_money,
                "remaining_money": center_balance.exist_money,
                "taken_money": center_balance.taken_money,
                "month_date": center_balance.month.date.strftime("%Y-%m-%d"),
                "old_id": center_balance.id
            }
            url = 'http://localhost:8000/Transfer/books/create_center_balance/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_book_order():
    with app.app_context():
        book_orders = BookOrder.query.order_by(BookOrder.id).all()
        for book_order in book_orders:
            info = {
                "user": book_order.user_id,
                "student": book_order.student_id,
                "teacher": book_order.teacher_id,
                "group": book_order.group_id,
                "book": book_order.book_id,
                "branch": book_order.location_id,
                "collected_payment": book_order.collected_payments_id,
                "count": book_order.count,
                "admin_status": book_order.admin_confirm,
                "editor_status": book_order.editor_confirm,
                "deleted": book_order.deleted,
                "reason": book_order.reason,
                "old_id": book_order.id
            }
            url = 'http://localhost:8000/Transfer/books/create_book_ordert/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_collected_book_payment():
    with app.app_context():
        collected_book_payments = CollectedBookPayments.query.order_by(CollectedBookPayments.id).all()
        for collected_book_payment in collected_book_payments:
            info = {
                "branch": collected_book_payment.location_id,
                "payment_type": collected_book_payment.payment_type_id,
                "total_debt": collected_book_payment.debt,
                "month_date": collected_book_payment.month.date.strftime("%Y-%m-%d"),
                "created_date": collected_book_payment.created.date.strftime("%Y-%m-%d"),
                "received_date": collected_book_payment.received.date.strftime("%Y-%m-%d"),
                "status": collected_book_payment.status,
                "old_id": collected_book_payment.id

            }
            url = 'http://localhost:8000/Transfer/books/create_collected_book_payment/'
            x = requests.post(url, json=info)
            if x.status_code != 201:
                print(x.text)
        return True


def transfer_book():
    with app.app_context():
        books = Book.query.order_by(Book.id).all()
        for book in books:
            info = {
                "old_id": book.id,
                "name": book.name,
                "desc": book.desc,
                "price": book.price,
                "own_price": book.own_price,
                "share_price": book.share_price
            }
            url = 'http://localhost:8000/Books/books/'
            x = requests.post(url, json=info)
            if x.status_code != 200:
                print(x.text)
            id = x.json()['id']
            img_url = 'http://localhost:8000/Books/book_images_create/'
            data = {
                "book": id,
            }
            if os.path.isfile(f'../../{book.img}'):
                file_path = book.img
                img_name = file_path.replace('static/img_folder/', '')
                files = [
                    ('image', (img_name, open(f'../../{book.img}', 'rb'), 'image/jpeg'))
                ]
                response = requests.post(img_url, data=data, files=files)
                if response.status_code != 201:
                    print(response.text)
        return True
