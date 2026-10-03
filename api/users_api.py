from flask import request, jsonify, Blueprint
from models import db, User, Participation

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/users')


def _user_to_dict(user):
    item = {'id': user.id, 'full_name': user.full_name}
    if user.group:
        item['group'] = user.group
    return item


def _validate_full_name(full_name):
    if not full_name or not str(full_name).strip():
        return 'Поле ФИО обязательно к заполнению'
    if any(char.isdigit() for char in full_name):
        return 'Поле ФИО не может содержать цифры'
    parts = full_name.split()
    if len(parts) > 4:
        return 'Поле ФИО не может содержать больше 4х слов'
    if len(parts) < 2:
        return 'Поле ФИО не может содержать меньше 2х слов'
    if any(len(word) < 2 for word in parts):
        return 'Поле ФИО не может быть слишком коротких слов'
    return None


@user_bp.route('', methods=['GET'])
def list_users():
    return jsonify([_user_to_dict(user) for user in User.query.all()]), 200


@user_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(_user_to_dict(user)), 200


@user_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    full_name = data.get('full_name', '')
    group = data.get('group') or None

    if group is not None and (not group or not str(group).strip()):
        return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400

    name_err = _validate_full_name(full_name)
    if name_err:
        return jsonify({'error': name_err}), 400

    existing = User.query.filter_by(full_name=full_name).first()
    if existing:
        return jsonify(_user_to_dict(existing)), 201

    user = User(full_name=full_name, group=group)
    db.session.add(user)
    db.session.commit()
    return jsonify(_user_to_dict(user)), 201


@user_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    full_name = data.get('full_name', '')
    group = data.get('group') if 'group' in data else user.group

    if group is not None and (not group or not str(group).strip()):
        return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400

    name_err = _validate_full_name(full_name)
    if name_err:
        return jsonify({'error': name_err}), 400

    user.full_name = full_name
    user.group = group
    db.session.commit()
    return jsonify(_user_to_dict(user)), 200


@user_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    participation = Participation.query.filter_by(user_id=user.id).first()
    if participation:
        return jsonify({
            'error': (
                f'Нельзя удалить пользователя, у которого есть записи об участии '
                f'({participation.event.name}, {participation.event.date})'
            )
        }), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify([]), 204
