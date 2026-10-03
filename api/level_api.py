from flask import request, jsonify, Blueprint
from models import db, Level, Event

level_bp = Blueprint('level_bp', __name__, url_prefix='/api/levels')


@level_bp.route('', methods=['GET'])
def list_levels():
    result = [{'id': level.id, 'name': level.name} for level in Level.query.all()]
    return jsonify(result), 200


@level_bp.route('/<int:id>', methods=['GET'])
def get_level(id):
    level = Level.query.get_or_404(id)
    return jsonify({'id': level.id, 'name': level.name}), 200


@level_bp.route('', methods=['POST'])
def create_level():
    data = request.get_json()
    level_name = data.get('name', '')

    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400

    existing = Level.query.filter_by(name=level_name).first()
    if existing:
        return jsonify({'id': existing.id, 'name': existing.name}), 200

    level = Level(name=level_name)
    db.session.add(level)
    db.session.commit()
    return jsonify({'id': level.id, 'name': level.name}), 201


@level_bp.route('/<int:id>', methods=['PUT'])
def update_level(id):
    data = request.get_json()
    level = Level.query.get_or_404(id)
    level_name = data.get('name', '')

    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400

    level.name = level_name
    db.session.commit()
    return jsonify({'id': level.id, 'name': level.name}), 200


@level_bp.route('/<int:id>', methods=['DELETE'])
def delete_level(id):
    level = Level.query.get_or_404(id)
    event = Event.query.filter_by(level_id=level.id).first()
    if event:
        return jsonify({
            'error': (
                f'Нельзя удалить уровень, который записан в мероприятии '
                f'({event.name}, {event.date})'
            )
        }), 400
    db.session.delete(level)
    db.session.commit()
    return jsonify([]), 204
