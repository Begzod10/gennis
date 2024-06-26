def user_photo_folder():
    folder = "frontend/build/static/img_folder"
    return folder


def advantages_photo_folder():
    folder = "frontend/build/static/advantages"
    return folder


def news_photo_folder():
    folder = "frontend/build/static/news"
    return folder


def gallery_folder():
    folder = "frontend/build/static/gallery"
    return folder


def user_contract_folder():
    folder = "frontend/build/static/contract_pdf"
    return folder


def home_design():
    folder = "frontend/build/static/home_design"
    return folder


def certificate():
    folder = "frontend/build/static/certificates"
    return folder


def link_img():
    folder = "frontend/build/static/link_img"
    return folder


def teacher_certificate():
    folder = "frontend/build/static/teacher_certificate"
    return folder


def room_images():
    folder = "frontend/build/static/room"
    return folder


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'svg'}


def checkFile(filename):
    value = '.' in filename
    type_file = filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return value and type_file
