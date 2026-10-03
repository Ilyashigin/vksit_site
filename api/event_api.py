from flask import request, jsonify, Blueprint
from models import db, Event, Level, Participation
from api.date_utils import parse_and_format_event_period
from api.participation_helpers import normalize_description

event_bp = Blueprint('event_bp', __name__, url_prefix='/api/events')


def _event_to_dict(event):
    return {
        'id': event.id,
        'name': event.name,
        'date': event.date,
        'description': event.description or '',
        'level_name': event.level.name if event.level else None,
    }


@event_bp.route('', methods=['GET'])
def list_events():
    return jsonify([_event_to_dict(event) for event in Event.query.all()]), 200


@event_bp.route('/<int:id>', methods=['GET'])
def get_event(id):
    event = Event.query.get_or_404(id)
    return jsonify(_event_to_dict(event)), 200


@event_bp.route('', methods=['POST'])
def create_event():
    data = request.get_json()
    event_name = data.get('name', '')
    event_date = data.get('date', '')
    level_name = data.get('level_name', '')
    description = normalize_description(data.get('description'))

    if not event_name or not str(event_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400

    stored_date, _, date_err = parse_and_format_event_period(event_date)
    if date_err:
        return jsonify({'error': date_err}), 400

    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    level = Level.query.filter_by(name=level_name).first()
    if not level:
        level = Level(name=level_name)
        db.session.add(level)
        db.session.commit()

    event = Event.query.filter_by(
        name=event_name,
        date=stored_date,
        level_id=level.id,
    ).first()
    if not event:
        event = Event(
            name=event_name,
            date=stored_date,
            level_id=level.id,
            description=description,
        )
        db.session.add(event)
        db.session.commit()
    else:
        event.description = description
        db.session.commit()

    return jsonify(_event_to_dict(event)), 200


@event_bp.route('/<int:id>', methods=['PUT'])
def update_event(id):
    data = request.get_json()
    event = Event.query.get_or_404(id)
    event_name = data.get('name', '')
    event_date = data.get('date', '')
    level_name = data.get('level_name', '')

    if not event_name or not str(event_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400

    stored_date, _, date_err = parse_and_format_event_period(event_date)
    if date_err:
        return jsonify({'error': date_err}), 400

    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    level = Level.query.filter_by(name=level_name).first()
    if not level:
        level = Level(name=level_name)
        db.session.add(level)
        db.session.commit()

    event.name = event_name
    event.date = stored_date
    event.level_id = level.id
    event.description = normalize_description(data.get('description'))
    db.session.commit()

    return jsonify(_event_to_dict(event)), 200


@event_bp.route('/<int:id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    participation = Participation.query.filter_by(event_id=event.id).first()
    if participation:
        return jsonify({
            'error': (
                f'Нельзя удалить мероприятие, которое записано в участии '
                f'({participation.event.name}, {participation.event.date})'
            )
        }), 400
    db.session.delete(event)
    db.session.commit()
    return jsonify([]), 204
