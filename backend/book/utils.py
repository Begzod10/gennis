from app import request, jsonify, db, app
from backend.functions.utils import get_json_field, iterate_models
from backend.functions.small_info import checkFile, user_photo_folder
from backend.models.models import Book
from werkzeug.utils import secure_filename
import os
import json
from pprint import pprint


def handle_post_request():
    info = json.loads(request.form.get('info'))

    images = [request.files.get(f'file-{i}') for i in range(3)]
    img_urls = [save_image(img, i) for i, img in enumerate(images) if img and checkFile(img.filename)]
    book_data = {
        "name": info.get('name'),
        "desc": info.get('desc'),
        "price": int(info.get('eductionShare', 0)) + int(info.get('editorShare', 0)),
        "img": img_urls[0] if len(img_urls) > 0 else '',
        "img2": img_urls[1] if len(img_urls) > 1 else '',
        "img3": img_urls[2] if len(img_urls) > 2 else '',
        "own_price": info.get('editorShare'),
        "share_price": info.get('eductionShare')
    }

    book_record = Book(**book_data)
    book_record.add()

    return jsonify({
        "msg": "qoshildi",
        "success": True,
        "book": book_record.convert_json()
    })


def handle_get_request():
    books = Book.query.order_by(Book.id).all()
    return jsonify({
        "books": iterate_models(books)  # Assuming this is a function that formats books for JSON response
    })


def delete_book_images(book):
    for img_attr in ['img', 'img2', 'img3']:
        img_path = getattr(book, img_attr)
        if img_path and os.path.isfile(f'frontend/build/{img_path}'):
            os.remove(f'frontend/build/{img_path}')


def update_book(book):

    info = json.loads(request.form.get('info'))
    book.name = info.get('name', book.name)
    book.desc = info.get('desc', book.desc)
    book.own_price = info.get('editorShare', book.own_price)
    book.share_price = info.get('eductionShare', book.share_price)
    book.price = int(book.own_price) + int(book.share_price)
    db.session.commit()
    update_images(book)


def update_images(book):
    app.config['UPLOAD_FOLDER'] = user_photo_folder()
    for i in range(3):

        img_file = request.files.get(f'file-{i}')
        if img_file and checkFile(img_file.filename):
            save_image(img_file, i, book)


def save_image(img, i=None, book=None):
    photo_filename = secure_filename(img.filename)
    app.config['UPLOAD_FOLDER'] = user_photo_folder()
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
    img_url = os.path.join("static", "img_folder", photo_filename)
    if img and book:
        # Assign the image URL to the first empty slot
        setattr(book, ['img', 'img2', 'img3'][i], img_url)
        db.session.commit()
    else:
        return img_url
