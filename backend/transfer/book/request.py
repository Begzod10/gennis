import requests
from flask import send_from_directory
from app import app
from backend.models.models import BookPayments, CollectedBookPayments, CenterBalance, CenterBalanceOverhead, Book, \
    BookOrder, BookOverhead, EditorBalance, UserBooks


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
            print(x.text)
        return True
