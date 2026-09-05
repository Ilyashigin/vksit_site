from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

event_bp = Blueprint('event_bp', __name__, url_prefix='/api/mer')

@event_bp.route('', methods=['GET'])
def event_get():
    events = Meropriyatie.query.all()
    result = []
    for event in events:
        item = {
            'id': event.id,
            'event_name': event.name,
            'event_date': event.date,
            'event_level': event.uroven.uroven_name if event.uroven else None
        }
        result.append(item)
    return jsonify(result), 200

@event_bp.route('/<int:id>', methods=['GET'])
def event_get_by_id(id):
    event = Meropriyatie.query.get_or_404(id)
    item = {
        'id': event.id,
        'event_name': event.name,
        'event_date': event.date,
        'event_level': event.uroven.uroven_name if event.uroven else None
    }
    return jsonify(item), 200

@event_bp.route('', methods=['POST'])
def event_add():
    data = request.get_json()
    if request.method == 'POST':
        event_name = data['event_name']
        event_date = data['event_date']
        level_name = data['event_level']

        #-----проверки----
        if not event_name or not str(event_name).strip():
            return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400
        if not event_date or not str(event_date).strip():
            return jsonify({'error': 'Поле Дата обязательно к заполнению'}), 400
        if not level_name or not str(level_name).strip():
            return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

        level = Uroven.query.filter_by(uroven_name=level_name).first()
        if not level:
            level = Uroven(uroven_name=level_name)
            db.session.add(level)
            db.session.commit()
        #---проверка в бд
        event = Meropriyatie.query.filter_by(
            name=event_name,
            date=event_date,
            id_uroven=level.id
        ).first()
        if not event:
            event = Meropriyatie(
                name=event_name,
                date=event_date,
                id_uroven=level.id  # ← передаём id, а не объект
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({
                'id': event.id,
                'event_name': event.name,
                'event_date': event.date,
                'event_level': event.uroven.uroven_name
            }), 200
        else:
            print("Уже есть:", event.uroven.uroven_name)
            return jsonify({
                'id': event.id,
                'event_name': event.name,
                'event_date': event.date,
                'event_level': event.uroven.uroven_name
            }), 200

@event_bp.route('/<int:id>', methods=['PUT'])
def event_edit(id):
    data = request.get_json()
    event = Meropriyatie.query.get_or_404(id)
    event_name = data['event_name']
    event_date = data['event_date']
    level_name = data['event_level']

    #-----проверки----
    if not event_name or not str(event_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400
    if not event_date or not str(event_date).strip():
        return jsonify({'error': 'Поле Дата обязательно к заполнению'}), 400
    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    level = Uroven.query.filter_by(uroven_name=level_name).first()
    if not level:
        level = Uroven(uroven_name=level_name)
        db.session.add(level)
        db.session.commit()

        event.id_uroven = level.id
        db.session.commit()



    event.name = event_name
    event.date = event_date
    event.id_uroven = level.id
    db.session.commit()

    return jsonify({
        'id': event.id,
        'event_name': event_name,
        'event_date': event_date,
        'event_level': event.uroven.uroven_name
    }), 200

@event_bp.route('/<int:id>', methods=['DELETE'])
def event_delete(id):
    event = Meropriyatie.query.get_or_404(id)
    uc = Ucastie.query.filter_by(id_meropriyatie=event.id).first()
    if uc:
        return jsonify({'error': f'Нельзя удалить Мероприятие, которое записано в участии ({uc.meropriyatie.name}, {uc.meropriyatie.date})'}), 400
    db.session.delete(event)
    db.session.commit()
    return jsonify([]), 204