from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')

@user_bp.route('', methods=['GET'])
def get_users():
    users= User.query.all()
    result = []
    for user in users:
        item = {
            'id': user.id,
            'fio': user.fio
        }
        if user.group:
            item['group'] = user.group
        result.append(item)
    return jsonify(result), 200

@user_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    result= {
        'id': user.id,
        'fio': user.fio
    }
    if user.group:
        result['group'] = user.group
    return jsonify(result), 200

@user_bp.route('', methods=['POST'])
def post_user():
    data = request.get_json()
    if request.method == 'POST':
        fio = data['fio']
        group = None
        try:
            if data['group']:
                group = data['group']
                if not group or not str(group).strip():
                    return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400
        except:
            print('группы нет')
        if not fio or not str(fio).strip():
            return jsonify({'error': 'Поле ФИО обязательно к заполнению'}), 400

        if any(char.isdigit() for char in fio):
            return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400

        try:
            fio_ls = fio.split()
        except:
            return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
        if len(fio_ls) > 4:
            return jsonify({'error': 'Поле ФИО не может содержать больше 4х слов'}), 400
        if len(fio_ls) < 2:
            return jsonify({'error': 'Поле ФИО не может содержать меньше 2х слов'}), 400
        if any(len(w) < 2 for w in fio_ls):
            return jsonify({'error': 'Поле ФИО не может быть слишком коротких слов'}), 400

        if group:
            us = User(fio=fio, group=group)
        else:
            us = User(fio=fio)
        existing = User.query.filter_by(fio=fio).first()
        if not existing:
            db.session.add(us)
            db.session.commit()
            print("Коммит юзера")
        else:
            print("Уже есть:", existing.fio)

        if group:
            result={
                'id': us.id,
                'fio': us.fio,
                'group': us.group
            }
        else:
            result = {
                'id': us.id,
                'fio': us.fio
            }

        return jsonify(result), 201

@user_bp.route('/<int:id>', methods=['PUT'])
def put_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    fio = data['fio']
    group = user.group
    try:
        if data['group']:
            group = data['group']
            if not group or not str(group).strip():
                return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400
    except:
        group = None
    if not fio or not str(fio).strip():
        return jsonify({'error': 'Поле ФИО обязательно к заполнению'}), 400

    if any(char.isdigit() for char in fio):
        return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400

    try:
        fio_ls = fio.split()
    except:
        return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
    if len(fio_ls) > 4:
        return jsonify({'error': 'Поле ФИО не может содержать больше 4х слов'}), 400
    if len(fio_ls) < 2:
        return jsonify({'error': 'Поле ФИО не может содержать меньше 2х слов'}), 400
    if any(len(w) < 2 for w in fio_ls):
        return jsonify({'error': 'Поле ФИО не может быть слишком коротких слов'}), 400

    if group:
        user.fio = data['fio']
        user.group = data['group']
        result = {
            'id': user.id,
            'fio': user.fio,
            'group': user.group
        }
    else:
        user.fio = data['fio']
        result = {
            'id': user.id,
            'fio': user.fio
        }

    db.session.commit()
    return jsonify(result), 200

@user_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user=User.query.get_or_404(id)
    uc = Ucastie.query.filter_by(id_user=user.id).first()
    if uc:
        return jsonify({'error': f'Нельзя удалить пользователя, у которого есть записи об участии ({uc.meropriyatie.name}, {uc.meropriyatie.date})'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify([]), 204