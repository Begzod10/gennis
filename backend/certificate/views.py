from app import *
from backend.models.models import *
from PyPDF2 import *
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import shutil
from pprint import pprint
import zipfile
import shutil
import os.path
from datetime import datetime


def clear_directory(folder):
    """
    delete data and folder
    :param folder: folder name
    :return:
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


@app.route(f"{api}/add_certificate_level/", methods=['POST'])
def add_certificate_level():
    """
    add data CertificateLevels table
    :return: CertificateLevels data
    """
    value = request.get_json()['value']
    add = CertificateLevels(name=value)
    db.session.add(add)
    db.session.commit()
    levels = CertificateLevels.query.order_by(CertificateLevels.id).all()
    level_list = []
    for level in levels:
        info = {
            "id": level.id,
            "name": level.name
        }
        level_list.append(info)
    return jsonify({
        "levels": level_list
    })


@app.route(f"{api}/get_teachers_by_subject/", methods=['POST'])
def get_teachers_by_subject():
    """
    query all data in Teachers table
    :return: Teachers data
    """
    subject_id = request.get_json()['subject_id']
    location_id = request.get_json()['location_id']
    teachers = db.session.query(Teachers).join(Teachers.subject).options(contains_eager(Teachers.subject)).filter(
        Subjects.id == subject_id, Teachers.group != None).join(Teachers.user).options(
        contains_eager(Teachers.user)).filter(
        Users.location_id == location_id).all()
    teacher_list = []
    for teacher in teachers:
        if teacher.group:
            info = {
                "teacher_id": teacher.id,
                "teacher_name": teacher.user.name.capitalize(),
                "teacher_surname": teacher.user.surname.capitalize(),
            }
            teacher_list.append(info)
    return jsonify({
        "teachers": teacher_list
    })


@app.route(f"{api}/get_groups_by_teacher/", methods=['POST'])
def get_groups_by_teacher():
    """
    get Group data by Teacher primary key
    :return: Groups data
    """
    teacher_id = request.get_json()['teacher_id']
    teacher = Teachers.query.filter(Teachers.id == teacher_id).first()
    group_list = []
    for group in teacher.group:
        if group.deleted == False and group.status == True:
            info = {
                "id": group.id,
                "name": group.name.capitalize()
            }
            group_list.append(info)
    return jsonify({
        "groups": group_list
    })


@app.route(f"{api}/get_students_by_group/", methods=['POST'])
def get_students_by_group():
    """
    get Student data by Group primary key
    :return:
    """
    group_id = int(request.get_json()['group_id'])
    students = db.session.query(Students).join(Students.group).options(contains_eager(Students.group)).filter(
        Groups.id == group_id).order_by(Students.id).all()
    students_list = []
    for st in students:
        info = {
            "id": st.id,
            "name": st.user.name.capitalize(),
            "surname": st.user.surname.capitalize(),
            "ball": 0
        }
        students_list.append(info)
    return jsonify({
        "students": students_list
    })


@app.route(f"{api}/download_certificates2/<int:group_id>")
def download_certificates(group_id):
    """

    :param group_id: Group primary key
    :return: certificate file
    """
    group = Groups.query.filter(Groups.id == group_id).first()
    return send_file(f"{group.certificate_url}",
                     as_attachment=True)


@app.route(f"{api}/create_certificate", methods=['POST'])
def create_certificate():
    """
    create certificate by Student table and User table data
    :return:
    """
    folder = 'frontend/build/static/certificates'
    clear_directory(folder)
    student_list = request.get_json()['student_list']
    date = request.get_json()['date']
    course_id = request.get_json()['level']
    group_id = request.get_json()['group_id']
    certificate_id = 0
    group = Groups.query.filter(Groups.id == group_id).first()
    date = datetime.strptime(date, "%Y-%m-%d")
    zip_file_link = ''
    for st in student_list:
        student = Students.query.filter(Students.id == st['id']).first()
        teacher = db.session.query(Teachers).join(Teachers.group).options(contains_eager(Teachers.group)).filter(
            Groups.id == group.id).first()
        course = CertificateLevels.query.filter(CertificateLevels.id == course_id).first()

        certificate_id += 1
        max_number = 8
        number_of_0 = max_number - len(str(certificate_id))
        number_of_0 = number_of_0 * "0"
        exists_certificate = Certificate.query.filter(Certificate.student_id == student.id,
                                                      Certificate.ball == st['ball'], Certificate.date == date).first()
        if not exists_certificate:
            exists_certificate = Certificate(student_id=student.id, teacher_id=teacher.id,
                                             certificate_id_number=certificate_id,
                                             level_id=course.id, ball=st["ball"], date=date)
            db.session.add(exists_certificate)
            db.session.commit()

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColorRGB(0, 0, 0)
        can.setFont("Times-Roman", 12)
        can.drawString(100, 416, f"{date.strftime('%Y-%m-%d')}")
        can.setFont("Times-Roman", 28)
        can.drawString(55, 385, f"{student.user.name.capitalize()} {student.user.surname.capitalize()}")
        can.setFont("Times-Roman", 20)
        can.drawString(55, 330, f"{course.name.capitalize()} Course")
        can.setFont("Times-Roman", 15)
        can.drawString(175, 291, f"{number_of_0}{certificate_id}")
        can.setFont("Times-Roman", 15)
        can.drawString(125, 73, f"{teacher.user.name.capitalize()} {teacher.user.surname.capitalize()}")
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open("backend/certificate/certificate_empty.pdf", "rb"))
        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        id = uuid.uuid1()
        user_id = id.hex[0:15]
        output_stream = open(
            f"frontend/build/static/certificates/{student.user.name.capitalize()} {student.user.surname.capitalize()} {course.name} {user_id}.pdf",
            "wb")
        output.write(output_stream)
        output_stream.close()
        Certificate.query.filter(Certificate.id == exists_certificate.id).update({
            "link": f"frontend/build/static/certificates/{student.user.name.capitalize()} {student.user.surname.capitalize()} {course.name} {user_id}.pdf"
        })
        db.session.commit()

        archived = shutil.make_archive(f'frontend/build/static/zip_directory/{group.name.capitalize()}', 'zip',
                                       'frontend/build/static/certificates')

        if os.path.exists(f'frontend/build/static/zip_directory/{group.name.capitalize()}'):
            print(archived)
        else:
            print("ZIP file not created")
        zip_file_link = f'frontend/build/static/zip_directory/{group.name.capitalize()}.zip'
    certificate_link = CertificateLinks(link=zip_file_link, group_id=group.id)
    db.session.add(certificate_link)
    db.session.commit()
    Groups.query.filter(Groups.id == group.id).update({
        "certificate_url": zip_file_link
    })
    db.session.commit()
    return jsonify({
        "success": True
    })


@app.route(f"{api}/certificate2", methods=["GET", "POST"])
def certificate():
    """

    :return: Subjects, Locations, CertificateLevels, CalendarDay datas
    """
    subjects = Subjects.query.order_by(Subjects.id).all()
    locations = Locations.query.order_by(Locations.id).all()
    certificate_levels = CertificateLevels.query.order_by(CertificateLevels.id).all()
    refreshdatas()
    calendar_year = CalendarYear.query.filter(CalendarYear.date == new_year()).first()

    calendar_month = CalendarMonth.query.filter(CalendarMonth.date == new_month(),
                                                CalendarMonth.year_id == calendar_year.id).first()
    calendar_day = CalendarDay.query.filter(CalendarDay.date == new_today(),
                                            CalendarDay.month_id == calendar_month.id).first()

    return render_template("certificate.html", subjects=subjects, locations=locations,
                           certificate_levels=certificate_levels, calendar_day=calendar_day)
