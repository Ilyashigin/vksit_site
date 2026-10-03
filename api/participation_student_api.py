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

participation_student_bp = Blueprint('participation_student_bp', __name__)


@participation_student_bp.route('/api/participation/students', methods=['GET'])
def list_student_participations():
    result = []
    for participation in Participation.query.all():
        item = participation_to_dict(participation, user_type='student')
        if item:
            result.append(item)
    return jsonify(result), 200


@participation_student_bp.route('/api/participation/students/<int:id>', methods=['GET'])
def get_student_participation(id):
    participation = Participation.query.get_or_404(id)
    item = participation_to_dict(participation, user_type='student')
    return jsonify(item), 200


@participation_student_bp.route('/api/participation/students', methods=['POST'])
def create_student_participation():
    data = request.get_json()
    allow_years = get_allow_years()

    event_name = data.get('event_name', '')
    level_name = data.get('level_name', '')
    event_date = data.get('event_date', '')
    result = data.get('result', '')
    full_name = data.get('full_name', '')
    diplomas = data.get('diplomas', '')
    awards = data.get('awards', '')
    group = data.get('group', '')
    mentor_name = data.get('mentor', '')

    if not mentor_name or not str(mentor_name).strip():
        return jsonify({'error': 'Поле Наставник обязательно к заполнению'}), 400
    if not group or not str(group).strip():
        return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400
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

    mentor_err = validate_full_name(mentor_name, field_label='Наставник')
    if mentor_err:
        return jsonify({'error': mentor_err}), 400

    level = get_or_create_level(level_name)
    user = get_or_create_user(full_name, group=group)
    event = get_or_create_event(
        event_name, stored_date, level.id, data.get('description'),
    )
    mentor = get_or_create_user(mentor_name)

    participation = Participation(
        result=build_result_text(result, diplomas, awards),
        event_id=event.id,
        user_id=user.id,
        mentor_id=mentor.id,
        year1=year1,
        year2=year2,
    )
    db.session.add(participation)
    db.session.commit()

    return jsonify([participation_to_dict(participation, user_type='student')]), 201


@participation_student_bp.route('/api/participation/students/<int:id>', methods=['PUT'])
def update_student_participation(id):
    participation = Participation.query.get_or_404(id)
    data = request.get_json()
    allow_years = get_allow_years(offset_before=2, offset_after=0)

    event_name = data.get('event_name', '')
    level_name = data.get('level_name', '')
    event_date = data.get('event_date', '')
    result = data.get('result', '')
    full_name = data.get('full_name', '')
    diplomas = data.get('diplomas', '')
    awards = data.get('awards', '')
    group = data.get('group', '')
    mentor_name = data.get('mentor', '')

    if not mentor_name or not str(mentor_name).strip():
        return jsonify({'error': 'Поле Наставник обязательно к заполнению'}), 400
    if not group or not str(group).strip():
        return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400
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

    mentor_err = validate_full_name(mentor_name, field_label='Наставник')
    if mentor_err:
        return jsonify({'error': mentor_err}), 400

    level = get_or_create_level(level_name)
    user = get_or_create_user(full_name, group=group)
    event = get_or_create_event(
        event_name, stored_date, level.id, data.get('description'),
    )
    mentor = get_or_create_user(mentor_name)

    participation.result = build_result_text(result, diplomas, awards)
    participation.year1 = year1
    participation.year2 = year2
    participation.event_id = event.id
    participation.user_id = user.id
    participation.mentor_id = mentor.id
    db.session.commit()

    return jsonify([participation_to_dict(participation, user_type='student')]), 200


@participation_student_bp.route('/api/participation/students/<int:id>', methods=['DELETE'])
def delete_student_participation(id):
    participation = Participation.query.get_or_404(id)
    db.session.delete(participation)
    db.session.commit()
    return jsonify([]), 204
