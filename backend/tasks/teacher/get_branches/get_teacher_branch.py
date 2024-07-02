from app import app, jsonify
from backend.models.models import Users, Teachers

from backend.functions.utils import api
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route(f'{api}/get_branches', methods=["GET"])
@jwt_required()
def get_branches():
    user = Users.query.filter(Users.user_id == get_jwt_identity()).first()
    teacher = Teachers.query.filter(Teachers.user_id == user.id).first()
    branches = [{'name': location.name, 'id': location.id} for location in teacher.locations]
    return jsonify({'locations': branches})
