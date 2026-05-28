from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

level_bp = Blueprint('level_bp', __name__, url_prefix='/api/ur')

@level_bp.route('', methods=['GET'])
def level_get():
    urovni = Uroven.query.all()
    result = []
    for uroven in urovni:
        item = {
            'id': uroven.id,
            'event_level': uroven.uroven_name
        }
        result.append(item)
    return jsonify(result), 200

@level_bp.route('/<int:id>', methods=['GET'])
def level_get_by_id(id):
    uroven = Uroven.query.get_or_404(id)
    item = {
        'id': uroven.id,
        'event_level': uroven.uroven_name
    }
    return jsonify(item), 200

@level_bp.route('', methods=['POST'])
def level_add():
    data = request.get_json()
    if request.method == 'POST':
        level_name = data['event_level']

        #-----проверки----
        if not level_name or not str(level_name).strip():
            return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400

        #---проверка в бд
        level = Uroven(uroven_name=level_name)
        existing = Uroven.query.filter_by(uroven_name=level_name).first()
        if not existing:
            db.session.add(level)
            db.session.commit()
            print("Комит Уровня")
            return jsonify({
                'id': level.id,
                'event_level': level.uroven_name
            }), 201
        else:
            print("Уже есть:", existing.uroven_name)
            return jsonify({
                'id': existing.id,
                'event_level': existing.uroven_name
            }), 200

@level_bp.route('/<int:id>', methods=['PUT'])
def uroven_edit(id):
    data = request.get_json(id)
    level = Uroven.query.get_or_404(id)
    level_name = data['event_level']

    #-----проверки----
    if not level_name or not str(level_name).strip():
        return jsonify({'error': 'Поле Название обязательно к заполнению'}), 400


    level.uroven_name = level_name
    db.session.commit()

    return jsonify({
        'id': level.id,
        'event_name': level_name
    }), 200

@level_bp.route('/<int:id>', methods=['DELETE'])
def uroven_delete(id):
    level = Uroven.query.get_or_404(id)
    event = Meropriyatie.query.filter_by(id_uroven=level.id).first()
    if event:
        return jsonify({'error': f'Нельзя удалить уровень, который записан в мероприятии ({event.name}, {event.date})'}), 400
    db.session.delete(level)
    db.session.commit()
    return jsonify([]), 204