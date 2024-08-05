from app import app, jsonify
from backend.functions.utils import api
from backend.transfer.group.request import transfer_course_types


@app.route(f'{api}/transfer', methods=['GET'])
def transfer():
    request = ''
    status_transfer_course_types = transfer_course_types()
    request += status_transfer_course_types
    return jsonify({
        'request': request
    })
