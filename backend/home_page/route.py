import json
import os
from datetime import date

from flask_jwt_extended import jwt_required

from app import app, api, jsonify, db, request, secure_filename
from backend.functions.small_info import advantages_photo_folder, news_photo_folder, checkFile, gallery_folder, \
    certificate_folder
from backend.models.models import Advantages, CommentLikes, HomeVideo, HomeDesign, Comments, Users, Links, News, \
    Gallery, NewsImg, StudentCertificate, Groups, Teachers, TeacherData


@app.route(f'{api}/get_teacher_data/<int:teacher_id>', methods=['GET'])
def get_teacher_data(teacher_id):
    data = TeacherData.query.filter(TeacherData.teacher_id == teacher_id).first()
    list = []
    for item in StudentCertificate.query.filter(StudentCertificate.teacher_id == teacher_id).order_by(
            StudentCertificate.id).all():
        list.append(item.json())
    if data:
        return jsonify({
            'data': data.json(),
            'list': list,
            'status': True
        })
    else:
        return jsonify({
            'status': False,
            'list': list,
        })


@app.route(f'{api}/change_teacher_data', methods=['POST'])
def change_teacher_data():
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    req = eval(data['res'])
    photo = request.files['img']
    teacher_id = req['teacher_id']
    text = req['text']
    telegram = req['telegram']
    instagram = req['instagram']
    facebook = req['facebook']
    data = TeacherData.query.filter(TeacherData.teacher_id == teacher_id).first()
    if data:
        data.text = text
        data.telegram = telegram
        data.instagram = instagram
        data.facebook = facebook
        app.config['UPLOAD_FOLDER'] = certificate_folder()
        if photo and checkFile(photo.filename):
            if os.path.exists(f'frontend/build/{data.img}'):
                os.remove(f'frontend/build/{data.img}')
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "certificates" + "/" + photo_filename
            data.img = url
        db.session.commit()
        return jsonify({
            "msg": "Nigga",
            'data': data.json(),
            "success": True
        })
    else:
        app.config['UPLOAD_FOLDER'] = certificate_folder()
        if photo and checkFile(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "certificates" + "/" + photo_filename
            new = TeacherData(teacher_id=teacher_id, text=text, telegram=telegram, instagram=instagram,
                              facebook=facebook, img=url)
            db.session.add(new)
            db.session.commit()
        else:
            new = TeacherData(teacher_id=teacher_id, text=text, telegram=telegram, instagram=instagram,
                              facebook=facebook)
            db.session.add(new)
            db.session.commit()
        return jsonify({
            "msg": "Nigga",
            'data': new.json(),
            "success": True
        })


@app.route(f'{api}/get_groups/<int:teacher_id>', methods=['GET'])
def get_groups(teacher_id):
    teacher = Teachers.query.filter(Teachers.id == teacher_id).first()
    list = []
    print(teacher.group)
    for group in teacher.group:
        info = {
            'name': group.name,
            'id': group.id
        }
        list.append(info)
    return jsonify({
        'groups': list,
    })


@app.route(f'{api}/get_student_in_group/<int:group_id>', methods=['GET'])
def get_student_in_group(group_id):
    group = Groups.query.filter(Groups.id == group_id).first()
    list = []
    print(group.student)
    for student in group.student:
        info = {
            'name': student.user.name,
            'id': student.id
        }
        list.append(info)

    return jsonify({
        'students': list,
    })


@app.route(f'{api}/add_student_certificate', methods=['POST'])
def add_student_certificate():
    form = json.dumps(dict(request.form))
    data = json.loads(form)
    res = eval(data['res'])
    text = res.get('text')
    teacher_id = res['teacher_id']
    student_id = res['student_id']
    today = date.today()
    group_id = res['group_id']
    photo = request.files['img']
    app.config['UPLOAD_FOLDER'] = certificate_folder()
    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "certificates" + "/" + photo_filename
        new = StudentCertificate(teacher_id=teacher_id, group_id=group_id, student_id=student_id, text=text, date=today,
                                 img=url)
        db.session.add(new)
        db.session.commit()
        return jsonify({
            "msg": "Nigga",
            "success": True
        })


@app.route(f'{api}/get_home_info', methods=['GET'])
def get_home_info():
    design = HomeDesign.query.order_by(HomeDesign.id).all()
    for item in design:
        design = item
    video = HomeVideo.query.order_by(HomeVideo.id).all()
    for item in video:
        video = item
    today = date.today()

    news = News.query.filter(News.date >= today).order_by(News.id).all()
    list = []
    for new in news:
        list.append(new.json())
    if design and video:
        return jsonify({
            'design': design.json(),
            'video': video.json(),
            'news': list,
            "success": True
        })
    else:
        return jsonify({
            "success": False
        })


@app.route(f'{api}/add_home_design', methods=['POST'])
def add_home_design():
    name = eval(request.form.get('name'))
    text = eval(request.form.get('text'))
    photo = request.files['file']
    app.config['UPLOAD_FOLDER'] = gallery_folder()
    if photo and checkFile(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        url = "static" + "/" + "gallery" + "/" + photo_filename
        new_design = HomeDesign(name=name, text=text, img=url)
        db.session.add(new_design)
        db.session.commit()
        return jsonify({
            "msg": "Nigga",
            'design': new_design.json(),
            "success": True
        })


@app.route(f'{api}/add_home_video', methods=['POST'])
def add_home_video():
    req = request.get_json()
    name = req['name']
    text = req['text']
    video = req['link']
    new_video = HomeVideo(name=name, text=text, url=video)
    db.session.add(new_video)
    db.session.commit()
    return jsonify({
        "msg": "Nigga",
        "success": True,
        'video': new_video.json()
    })


@app.route(f'{api}/add_advantages', methods=['POST'])
@jwt_required()
def add_advantages():
    name = request.get_json()['name']
    add = Advantages(name=name)
    db.session.add(add)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": add.id
    })


@app.route(f'{api}/home_advantages')
def home_advantages():
    advantages = Advantages.query.order_by(Advantages.id).all()
    advantages_list = [{
        "id": advantage.id,
        "name": advantage.name,
        "img": advantage.img
    } for advantage in advantages]

    return jsonify({
        "advantages": advantages_list
    })


@app.route(f'{api}/advantage_img/<int:advantage_id>', methods=['POST'])
@jwt_required()
def advantage_img(advantage_id):
    photo = request.files['file']

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
            "msg": "",
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
    Advantages.query.filter(Advantages.id == advantage_id).update({
        "name": request.get_json()['name']
    })
    db.session.commit()
    return jsonify({
        "msg": "",
        "success": True,
        "id": advantage_id
    })


@app.route(f'{api}/delete_advantage/<int:advantage_id>')
@jwt_required()
def delete_advantage(advantage_id):
    advantage = Advantages.query.filter(Advantages.id == advantage_id).first()
    if os.path.exists(f'frontend/build/{advantage.img}'):
        os.remove(f'frontend/build/{advantage.img}')
    Advantages.query.filter(Advantages.id == advantage_id).delete()
    db.session.commit()
    return jsonify({
        "msg": "",
        "success": True
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
        link_base = Links(name=link['type'], link=link['link'], news_id=add.id)
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
            print(file)
            img_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
            url = "static" + "/" + "news" + "/" + img_name
            img = NewsImg(url=url, new_id=add.id)
            db.session.add(img)
            db.session.commit()
    print(add)
    return jsonify({
        'new': add.json(),
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
    print(links)
    for link in links:
        if 'link_id' in link:
            Links.query.filter(Links.id == link['link_id']).update({
                "name": link['type'],
                'link': link['link']
            })
            db.session.commit()
        else:
            add = Links(name=link['type'], link=link['link'], news_id=news_id)
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
            img = NewsImg(url=url, new_id=news.id)
            db.session.add(img)
            db.session.commit()
    return jsonify({
        'msg': "Yangilik o'zgartirildi",
        'success': True,
        "news": news.json()
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
    links = Links.query.filter(Links.news_id == news_id).all()
    for link in links:
        Links.query.filter(Links.id == link.id).delete()
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
