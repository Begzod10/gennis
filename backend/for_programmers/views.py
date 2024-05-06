from flask_jwt_extended import get_jwt_identity, jwt_required

from app import app, api, or_, db, contains_eager, extract, jsonify, request
import os
from backend.functions.small_info import checkFile, news_photo_folder
from backend.for_programmers.models import PlatformNews
from werkzeug.utils import secure_filename

from backend.models.models import Users


@app.route('/creat_platform_news', methods=["POST", "GET"])
@jwt_required()
def creat_platform_news():
    identity = get_jwt_identity()
    user = Users.query.filter_by(user_id=identity).first()
    news = request.get_json()['news']
    photo = request.files['photo']
    folder = news_photo_folder()
    if photo and checkFile(photo.filename):
        photo_file = secure_filename(photo.filename)
        photo_url = "/" + folder + "/" + photo_file
        app.config['UPLOAD_FOLDER'] = folder
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        add = PlatformNews(img=photo_url, text=news["text"], teachers=bool(news["teachers"]), staff=bool(news["staff"]),
                           students=bool(news["students"]), user_id=user.id)
        db.session.add(add)
        db.session.commit()
    else:
        add = PlatformNews(text=news["text"], teachers=bool(news["teachers"]), staff=bool(news["staff"]),
                           students=bool(news["students"]), user_id=user.id)
        db.session.add(add)
        db.session.commit()
    return jsonify({"info": True})


@app.route('/platform_new_edit/<int:news_id>', methods=["POST", "GET"])
def platform_new_edit(news_id):
    photo = request.files['photo']
    news = request.get_json()['news']
    folder = news_photo_folder()
    if photo and checkFile(photo.filename):
        photo_file = secure_filename(photo.filename)
        photo_url = "/" + folder + "/" + photo_file
        app.config['UPLOAD_FOLDER'] = folder
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        PlatformNews.query.filter(PlatformNews.id == news_id).update({
            "text": news["text"],
            "img": photo_url,
            "teachers": bool(news["teachers"]),
            "students": bool(news["students"]),
            "staff": bool(news["staff"])
        })
        db.session.commit()
    else:
        PlatformNews.query.filter(PlatformNews.id == news_id).update({
            "text": news["text"],
            "teachers": bool(news["teachers"]),
            "students": bool(news["students"]),
            "staff": bool(news["staff"])
        })
        db.session.commit()
    return jsonify({"info": "true"})
