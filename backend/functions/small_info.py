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


def room_images():
    folder = "frontend/build/static/room"
    return folder


def certificate_folder():
    return "fronted/build/static/certificates"


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def checkFile(filename):
    value = '.' in filename
    type_file = filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return value and type_file
