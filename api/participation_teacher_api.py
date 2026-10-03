from flask import request, jsonify, Blueprint

from models import db, Participation
from api.participation_helpers import (
    participation_to_dict,
    validate_full_name,
    get_allow_years,
    parse_event_date_and_year,
    get_or_create_level,
    get_or_create_event,
    get_or_create_user,
    build_result_text,
)

participation_teacher_bp = Blueprint('participation_teacher_bp', __name__)


@participation_teacher_bp.route('/api/participation/teachers', methods=['GET'])
def list_teacher_participations():
    result = []
    for participation in Participation.query.all():
        if participation.user.group is not None:
            continue
        item = participation_to_dict(participation)
        if item:
            result.append(item)
    return jsonify(result), 200


@participation_teacher_bp.route('/api/participation/teachers/<int:id>', methods=['GET'])
def get_teacher_participation(id):
    participation = Participation.query.get_or_404(id)
    item = participation_to_dict(participation)
    return jsonify(item), 200


@participation_teacher_bp.route('/api/participation/teachers', methods=['POST'])
def create_teacher_participation():
    data = request.get_json()
    allow_years = get_allow_years()

    event_name = data.get('event_name', '')
    level_name = data.get('level_name', '')
    event_date = data.get('event_date', '')
    result = data.get('result', '')
    full_name = data.get('full_name', '')
    diplomas = data.get('diplomas', '')
    awards = data.get('awards', '')

    if not event_name or not str(event_name).strip():
        return jsonify({'error': 'Поле Мероприятие обязательно к заполнению'}), 400
    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    stored_date, year1, year2, err = parse_event_date_and_year(event_date, allow_years)
    if err:
        return jsonify({'error': err}), 400

    if not result or not str(result).strip():
        return jsonify({'error': 'Поле Результат обязательно к заполнению'}), 400

    name_err = validate_full_name(full_name)
    if name_err:
        return jsonify({'error': name_err}), 400

    level = get_or_create_level(level_name)
    user = get_or_create_user(full_name)
    event = get_or_create_event(
        event_name, stored_date, level.id, data.get('description'),
    )

    participation = Participation(
        result=build_result_text(result, diplomas, awards),
        event_id=event.id,
        user_id=user.id,
        year1=year1,
        year2=year2,
    )
    db.session.add(participation)
    db.session.commit()

    return jsonify([participation_to_dict(participation)]), 201


@participation_teacher_bp.route('/api/participation/teachers/<int:id>', methods=['PUT'])
def update_teacher_participation(id):
    participation = Participation.query.get_or_404(id)
    data = request.get_json()
    allow_years = get_allow_years()

    event_name = data.get('event_name', '')
    level_name = data.get('level_name', '')
    event_date = data.get('event_date', '')
    result = data.get('result', '')
    full_name = data.get('full_name', '')
    diplomas = data.get('diplomas', '')
    awards = data.get('awards', '')

    if not event_name or not str(event_name).strip():
        return jsonify({'error': 'Поле Мероприятие обязательно к заполнению'}), 400
    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    stored_date, year1, year2, err = parse_event_date_and_year(event_date, allow_years)
    if err:
        return jsonify({'error': err}), 400

    if not result or not str(result).strip():
        return jsonify({'error': 'Поле Результат обязательно к заполнению'}), 400

    name_err = validate_full_name(full_name)
    if name_err:
        return jsonify({'error': name_err}), 400

    level = get_or_create_level(level_name)
    user = get_or_create_user(full_name)
    event = get_or_create_event(
        event_name, stored_date, level.id, data.get('description'),
    )

    participation.result = build_result_text(result, diplomas, awards)
    participation.year1 = year1
    participation.year2 = year2
    participation.event_id = event.id
    participation.user_id = user.id
    db.session.commit()

    return jsonify([participation_to_dict(participation)]), 200


@participation_teacher_bp.route('/api/participation/teachers/<int:id>', methods=['DELETE'])
def delete_teacher_participation(id):
    participation = Participation.query.get_or_404(id)
    db.session.delete(participation)
    db.session.commit()
    return jsonify([]), 204
