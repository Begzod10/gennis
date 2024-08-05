from app import app, jsonify
from backend.functions.utils import api
from backend.transfer.group.request import transfer_course_types
from backend.transfer.payments.request import transfer_payment_types
from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
from backend.transfer.branch_location.reuqest import transfer_location
token = ''

transfer_location()
# @app.route(f'{api}/transfer', methods=['GET'])
# def transfer():
#     request = ''
#     # status_transfer_course_types = transfer_course_types()
#     # request += status_transfer_course_types
#     # status_transfer_payment_types = transfer_payment_types()
#     # request += status_transfer_payment_types
#     # status_transfer_subjects = transfer_subjects()
#     # request += status_transfer_subjects
#     status_transfer_subject_levels = transfer_subject_levels()
#     request += status_transfer_subject_levels
#     return jsonify({
#         'request': request
#     })
