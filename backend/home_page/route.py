import json
import os
from datetime import date

from flask_jwt_extended import jwt_required

from app import app, api, jsonify, db, request, secure_filename, classroom_server
from backend.functions.small_info import advantages_photo_folder, news_photo_folder, checkFile, gallery_folder, \
    home_design, teacher_certificate, link_img
from backend.models.models import Advantages, CommentLikes, HomeVideo, HomeDesign, Comments, Users, NewsLink, News, \
    Gallery, NewsImg, StudentCertificate, Groups, Teachers, TeacherData, Subjects, Link, Locations
import requests
from pprint import pprint
from backend.functions.utils import get_json_field


@app.route(f'{api}/change_locations/<int:location_id>', methods=['POST'])
# @jwt_required()
def change_locations(location_id):
    req = request.get_json()
    number = req['number']
    location_name = req['location']
    link = req['link']
    location = Locations.query.filter(Locations.id == location_id).first()
    location.number_location = number
    location.location = location_name
    location.link = link
    db.session.commit()
    info = {
        "id": location.id,
        "name": location.name,
        "number": location.number_location,
        "location": location.location,
        "link": location.link,
    }
    return jsonify({
        "msg": "Ma'lumotlar o'zgartirildi",
        'location': info,
        "success": True,
    })


@app.route(f'{api}/advantage_img/<int:advantage_id>', methods=['POST'])
@jwt_required()
def advantage_img(advantage_id):
    if 'file' in request.files:
        photo = request.files['file']
    else:
        photo = None

    app.config['UPLOAD_FOLDER'] = advantages_photo_folder()

    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "advantages" + "/" + photo_filename
        advantage = Advantages.query.filter(Advantages.id == advantage_id).first()
        if os.path.exists(f'frontend/build/{advantage.img}'):
            os.remove(f'frontend/build/{advantage.img}')
        Advantages.query.filter(Advantages.id == advantage_id).update({
            "img": url
        })
        db.session.commit()

        return jsonify({
            "msg": "Ma'lumotlar o'zgartirildi",
            "img": advantage.img,
            "success": True
        })
    else:
        return jsonify({
            "success": False,
            "msg": "rasm formati tog'ri kelmadi"
        })


@app.route(f'{api}/change_advantage/<int:advantage_id>', methods=['POST'])
@jwt_required()
def change_advantage(advantage_id):
    pprint(request.get_json())
    advantage = Advantages.query.filter(Advantages.id == advantage_id).first()

    advantage.name = get_json_field('name')
    advantage.text = get_json_field('text')
    db.session.commit()
    return jsonify({
        "msg": "Ma'lumotlar o'zgartirildi",
        "success": True,
        "advantage": advantage.convert_json()
    })


@app.route(f'{api}/change_link', methods=['POST'])
@jwt_required()
def change_link():
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    req = eval(data['res'])
    files = request.files
    link_id = req['id']
    name = req['name']
    link_name = req['link']
    link = Link.query.filter(Link.id == link_id).first()
    if 'img' in files:
        img = request.files['img']
        link.name = name
        link.link = link_name
        app.config['UPLOAD_FOLDER'] = link_img()
        if checkFile(img.filename):
            if os.path.exists(f'frontend/build/{link.img}'):
                os.remove(f'frontend/build/{link.img}')
            photo_filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "link_img" + "/" + photo_filename
            link.img = url
        db.session.commit()
    else:
        link.name = name
        link.link = link_name
        db.session.commit()
    return jsonify({
        'status': True
    })


@app.route(f'{api}/get_student_in_group/<int:group_id>', methods=['GET'])
@jwt_required()
def get_student_in_group(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    list = []
    for student in group.student:
        info = {
            'name': student.user.name,
            'id': student.id
        }
        list.append(info)

    return jsonify({
        'students': list,
    })


@app.route(f'{api}/get_home_info', methods=['GET'])
def get_home_info():
    response = requests.get(f"{classroom_server}/api/classroom_subjects", headers={
        'Content-Type': 'application/json'
    })
    design = HomeDesign.query.first()
    video = HomeVideo.query.first()
    subjects = Subjects.query.order_by(Subjects.id).all()
    subject_list = []
    for subject in subjects:
        info = {
            'img': None,
            'name': subject.name
        }
        subject_list.append(info)
    certificates = StudentCertificate.query.order_by()
    certificate_list = []
    for certificate in certificates:
        info = {
            'text': certificate.text,
            'certificate': certificate.img,
            'student_img': certificate.student.user.photo_profile,
            'student': certificate.student.user.surname + ' ' + certificate.student.user.name,
            'teacher': certificate.teacher.user.surname + ' ' + certificate.teacher.user.name
        }
        certificate_list.append(info)
    today = date.today()
    news = News.query.filter(News.date >= today).order_by(News.id).all()
    list = []
    for new in news:
        list.append(new.convert_json())

    teacher_list = []
    teachers = Teachers.query.filter(Teachers.deleted == None).order_by(Teachers.id).all()
    for teacher in teachers:
        data = TeacherData.query.filter(TeacherData.teacher_id == teacher.id).first()
        teacher_subjects = []
        for subject in teacher.subject:
            teacher_subjects.append(subject.name)
        if data:
            info = {
                'full_name': teacher.user.surname + ' ' + teacher.user.name,
                'subjects': teacher_subjects,
                'id': teacher.user.id,
                'teacher_img': teacher.user.photo_profile,
                'text': data.text,
                'links': data.json2(),
            }
        else:
            info = {
                'full_name': teacher.user.surname + ' ' + teacher.user.name,
                'subjects': teacher_subjects,
                'id': teacher.user.id,
                'teacher_img': teacher.user.photo_profile,
                'text': None,
                'links': None,
            }
        teacher_list.append(info)
    links = []
    all_links = Link.query.order_by(Link.id).all()
    for link in all_links:
        links.append(link.convert_json())

    advantages = Advantages.query.order_by(Advantages.id).all()
    advantages_list = [{
        "id": advantage.id,
        "name": advantage.name,
        "text": advantage.text,
        "img": advantage.img
    } for advantage in advantages]

    locations = Locations.query.order_by(Locations.id).all()
    locations_list = [{
        "id": location.id,
        "name": location.name,
        "number": location.number_location,
        "location": location.location,
        "link": location.link,
    } for location in locations]
    return jsonify({
        'design': design.convert_json() if design else {},
        'video': video.convert_json() if video else {},
        'news': list,
        'subjects': response.json()['subjects'],
        'teachers': teacher_list,
        'certificates': certificate_list,
        'advantages': advantages_list,
        'locations': locations_list,
        'links': links,
        "success": True
    })


@app.route(f'{api}/add_home_design', methods=['POST'])
def add_home_design():
    name = request.form.get('name')
    text = request.form.get('text')

    if 'file' in request.files:
        photo = request.files['file']
    else:
        photo = False
    app.config['UPLOAD_FOLDER'] = home_design()
    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "home_design" + "/" + photo_filename
        design = HomeDesign.query.first()
        if design:
            if os.path.exists(f'frontend/build/{design.img}'):
                os.remove(f'frontend/build/{design.img}')
            design.name = name
            design.text = text
            design.img = url
            db.session.commit()
        else:
            new = HomeDesign(name=name, text=text, img=url)
            db.session.add(new)
            db.session.commit()
    else:
        design = HomeDesign.query.first()
        if design:
            design.name = name
            design.text = text
            db.session.commit()
        else:
            new = HomeDesign(name=name, text=text)
            db.session.add(new)
            db.session.commit()
    design = HomeDesign.query.first()
    return jsonify({
        "msg": "Nigga",
        'design': design.convert_json(),
        "success": True
    })


@app.route(f'{api}/add_home_video', methods=['POST'])
def add_home_video():
    req = request.get_json()
    name = req['name']
    text = req['text']
    video_link = req['link']

    video = HomeVideo.query.first()
    if not video:
        video = HomeVideo(name=name, text=text, url=video_link)
        db.session.add(video)
        db.session.commit()
    video.name = name
    video.text = text
    video.url = video_link
    db.session.commit()
    return jsonify({
        "msg": "Nigga",
        "success": True,
        'video': video.convert_json()
    })


def get_comments():
    comments = Comments.query.order_by(Comments.id).all()
    comments_list = [{
        "id": comment.id,
        "user_id": comment.user_id,
        "name": comment.user.name,
        'surname': comment.user.surname,
        'img': comment.user.photo_profile,
        "comment": comment.comment,
        "likes": len(comment.likes),
        "likes_info": [{"user_id": like.user_id for like in comment.likes}]
    } for comment in comments]

    return comments_list


@app.route(f'{api}/add_comment', methods=['POST'])
@jwt_required()
def add_comment():
    comment = request.get_json()['comment']
    user_id = request.get_json()['id']
    add = Comments(comment=comment, user_id=user_id)
    db.session.add(add)
    db.session.commit()

    return jsonify({
        "comments": get_comments()
    })


@app.route(f'{api}/home_comments')
def home_comments():
    return jsonify({
        "comments": get_comments()
    })


@app.route(f'{api}/like_comment/<int:user_id>/<comment_id>')
@jwt_required()
def like_comment(user_id, comment_id):
    user = Users.query.filter(Users.id == user_id).first()
    comment = Comments.query.filter(Comments.id == comment_id).first()
    like = CommentLikes.query.filter(CommentLikes.user_id == user.id, CommentLikes.comment_id == comment_id).first()
    if not like:
        like = CommentLikes(user_id=user.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
    else:
        db.session.delete(like)
        db.session.commit()
    return jsonify({
        "success": True,
        "comments": get_comments()
    })


@app.route(f'{api}/delete_comment/<int:comment_id>')
@jwt_required()
def delete_comment(comment_id):
    likes = CommentLikes.query.filter(CommentLikes.comment_id == comment_id).all()
    for like in likes:
        CommentLikes.query.filter(CommentLikes.id == like.id).delete()
        db.session.commit()

    Comments.query.filter(Comments.id == comment_id).delete()
    db.session.commit()
    return jsonify({
        "success": True,
        "msg": "Comment o'chirildi"
    })


@app.route(f'{api}/add_news', methods=['POST'])
def add_news():
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    req = eval(data['res'])
    title = req['title']
    date = req['date']
    desc = req['text']
    links = req['links']
    files = request.files
    add = News(title=title, description=desc, date=date)
    db.session.add(add)
    db.session.commit()
    for link in links:
        link_base = NewsLink(name=link['type'], link=link['link'], news_id=add.id)
        db.session.add(link_base)
        db.session.commit()
    list = []
    if 'image_1' in files:
        list.append(files['image_1'])
    if 'image_2' in files:
        list.append(files['image_2'])
    if 'image_3' in files:
        list.append(files['image_3'])
    if 'image_4' in files:
        list.append(files['image_4'])
    app.config['UPLOAD_FOLDER'] = news_photo_folder()
    for file in list:
        if checkFile(file.filename):
            img_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
            url = "static" + "/" + "news" + "/" + img_name
            img = NewsImg(url=url, new_id=add.id)
            db.session.add(img)
            db.session.commit()
    return jsonify({
        'new': add.convert_json(),
    })


@app.route(f'{api}/change_news/<int:news_id>', methods=['PUT'])
def change_news(news_id):
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    req = eval(data['res'])
    desc = req['text']
    title = req['title']
    date = req['date']
    links = req['links']
    files = request.files
    list = []
    if 'image_1' in files:
        list.append(files['image_1'])
    if 'image_2' in files:
        list.append(files['image_2'])
    if 'image_3' in files:
        list.append(files['image_3'])
    if 'image_4' in files:
        list.append(files['image_4'])
    news = News.query.filter(News.id == news_id).first()
    news.title = title
    news.description = desc
    news.date = date

    db.session.commit()
    for link in links:
        if 'link_id' in link:
            NewsLink.query.filter(NewsLink.id == link['link_id']).update({
                "name": link['type'],
                'link': link['link']
            })
            db.session.commit()
        else:
            add = NewsLink(name=link['type'], link=link['link'], news_id=news_id)
            db.session.add(add)
            db.session.commit()
    app.config['UPLOAD_FOLDER'] = news_photo_folder()
    if 'list' in req:
        new_list = req['list']
    else:
        new_list = []
    for id in new_list:
        NewsImg.query.filter(NewsImg.id == id).delete()
        db.session.commit()

    for file in list:
        if checkFile(file.filename):
            img_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
            url = "static" + "/" + "news" + "/" + img_name
            exist_img = NewsImg.query.filter(NewsImg.new_id == news_id, NewsImg.url == url).first()

            if not exist_img:
                img = NewsImg(url=url, new_id=news.id)
                db.session.add(img)
                db.session.commit()
    return jsonify({
        'msg': "Yangilik o'zgartirildi",
        'success': True,
        "news": news.convert_json()
    })


@app.route(f'{api}/home_news')
def home_news():
    news = News.query.order_by(News.id).all()
    news_list = []
    for new in news:
        info = {
            "id": new.id,
            'title': new.title,
            'desc': new.description,
            'img': new.img,
            'links': []
        }
        for link in new.links:
            link_info = {
                'type': link.name,
                'link': link.link,
                "link_id": link.id
            }
            info['links'].append(link_info)
        news_list.append(info)
    return jsonify({
        "news": news_list
    })


@app.route(f'{api}/delete_news/<int:news_id>')
def delete_news(news_id):
    links = NewsLink.query.filter(NewsLink.news_id == news_id).all()
    for link in links:
        NewsLink.query.filter(NewsLink.id == link.id).delete()
        db.session.commit()
    news = News.query.filter(News.id == news_id).first()
    if os.path.exists(f'frontend/build{news.img}'):
        os.remove(f'frontend/build{news.img}')
    db.session.delete(news)
    db.session.commit()
    return jsonify({
        'msg': "Yangilik o'chirildi",
        'success': True
    })


@app.route(f'{api}/add_gallery/<img_id>', methods=['POST'])
@jwt_required()
def add_gallery(img_id):
    photo = request.files['file']
    app.config['UPLOAD_FOLDER'] = gallery_folder()
    gallery = Gallery.query.filter(Gallery.id == img_id).first()

    if gallery:
        if photo and checkFile(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "gallery" + "/" + photo_filename
            if os.path.exists(f'frontend/build{gallery.img}'):
                os.remove(f'frontend/build{gallery.img}')
            Gallery.query.filter(Gallery.id == img_id).update({
                "img": url
            })
            db.session.commit()
    else:
        if photo and checkFile(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "gallery" + "/" + photo_filename
            add = Gallery(id=img_id, img=url)
            db.session.add(add)
            db.session.commit()

    return jsonify({
        'msg': 'rasm yuklandi',
        'success': True,
        'gallery': get_gallery()
    })


def get_gallery():
    imgs = [{"id": i, "img": None, "localImg": None} for i in range(1, 9)]

    gallery = Gallery.query.order_by(Gallery.id).all()
    gallery_list = [{'id': img.id, 'img': img.img, "localImg": None} for img in gallery]

    for img in imgs:
        if not any(existing_img['id'] == img['id'] for existing_img in gallery_list):
            gallery_list.append(img)
    unique_gallery = {}

    # Loop through each item in gallery_list.
    for gr in gallery_list:
        # If the id is not in unique_gallery, add the item to the dictionary.
        unique_gallery[gr['id']] = gr
    filtered_gallery = list(unique_gallery.values())
    return filtered_gallery


@app.route(f'{api}/gallery')
def gallery():
    return jsonify({
        'gallery': get_gallery()
    })
