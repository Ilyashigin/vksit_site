from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

ucastie_stud_bp = Blueprint('ucastie_stud_bp', __name__)

###########STUDENTS######################
@ucastie_stud_bp.route('/api/uchastiya/stud', methods=['GET'])
def stud():
    uchastiya = Ucastie.query.all()
    result = []
    for u in uchastiya:
        item = {
            'id': u.id,
            'rezults': u.rezultat,
            'year': u.year,
            'event_name': u.meropriyatie.name,
            'event_date': u.meropriyatie.date,
            'event_level': u.meropriyatie.uroven.uroven_name,
            'user_name': u.user.fio
        }
        if u.user.group:
            item['group'] = u.user.group
            item['mentor']= u.mentor.fio
            result.append(item)
    return jsonify(result), 200

@ucastie_stud_bp.route('/api/uchastiya/stud/<int:id>', methods=['GET'])
def stud_by_id(id):
    u = Ucastie.query.get_or_404(id)
    item = {
        'id': u.id,
        'rezults': u.rezultat,
        'year': u.year,
        'event_name': u.meropriyatie.name,
        'event_date': u.meropriyatie.date,
        'event_level': u.meropriyatie.uroven.uroven_name,
        'user_name': u.user.fio
    }
    if u.user.group:
        item['group'] = u.user.group
        item['mentor']= u.mentor.fio
        return jsonify(item), 200

@ucastie_stud_bp.route('/api/uchastiya/stud', methods=['POST'])
def stud_add():
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year-5, current_year-4, current_year-3, current_year-2, current_year-1, current_year, current_year+1]

    if request.method == 'POST':
        meropriyatie = data['event_name']
        uroven = data['event_level']
        sroki_provedeniya = data['event_date']
        rezultat = data['rezultat']
        fio = data['fio']
        diplomi = data['diplomi']
        nagradi = data['nagradi']
        year = data['year']
        group = data['group']
        mentor = data['mentor']

        #-----------Провенрки-------------------
        if not mentor or not str(mentor).strip():
            return jsonify({'error': 'Поле Наставник обязательно к заполнению'}), 400
        if not group or not str(group).strip():
            return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400

        if not meropriyatie or not str(meropriyatie).strip():
            return jsonify({'error': 'Поле Мероприятие обязательно к заполнению'}), 400

        if not uroven or not str(uroven).strip():
            return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

        if not sroki_provedeniya or not str(sroki_provedeniya).strip():
            return jsonify({'error': 'Поле Сроки проведения обязательно к заполнению'}), 400

        if not rezultat or not str(rezultat).strip():
            return jsonify({'error': 'Поле Результат обязательно к заполнению'}), 400

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

        if any(char.isdigit() for char in mentor):
            return jsonify({'error': 'Поле Наставник не может содержать цифры'}), 400

        try:
            fio_ls_mentor = mentor.split()
        except:
            return jsonify({'error': 'Поле Наставник не может содержать цифры'}), 400
        if len(fio_ls_mentor) > 4:
            return jsonify({'error': 'Поле Наставник не может содержать больше 4х слов'}), 400
        if len(fio_ls_mentor) < 2:
            return jsonify({'error': 'Поле Наставник не может содержать меньше 2х слов'}), 400
        if any(len(w) < 2 for w in fio_ls_mentor):
            return jsonify({'error': 'Поле Наставник не может быть слишком коротких слов'}), 400

        if not year or not str(year).strip():
            return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
        try:
            int(year)
        except:
            return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
        if int(year) not in allow_years:
            return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[-1]}'}), 400
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        #########проверка на наличие уже в бд№##############
        level = Uroven.query.filter_by(uroven_name=uroven).first()
        if not level:
            level = Uroven(uroven_name=uroven)
            db.session.add(level)
            db.session.commit()

        user = User.query.filter_by(fio=fio, group=group).first()
        if not user:
            user = User(fio=fio, group=group)
            db.session.add(user)
            db.session.commit()

        event = Meropriyatie.query.filter_by(
            name=meropriyatie,
            date=sroki_provedeniya,
            id_uroven=level.id
        ).first()
        if not event:
            event = Meropriyatie(
                name=meropriyatie,
                date=sroki_provedeniya,
                id_uroven=level.id
            )
            db.session.add(event)
            db.session.commit()
        use = User.query.filter_by(fio=mentor).first()
        if use:
            uchastie = Ucastie(
                rezultat=f"{rezultat}, {diplomi}, {nagradi}",
                id_meropriyatie=event.id,
                id_user=user.id,
                id_mentor=use.id,
                year=year
            )
        else:
            us = User(fio=mentor)
            db.session.add(us)
            db.session.commit()
            uchastie = Ucastie(
                rezultat=f"{rezultat}, {diplomi}, {nagradi}",
                id_meropriyatie=event.id,
                id_user=user.id,
                id_mentor = us.id,
                year=year
            )

        db.session.add(uchastie)
        db.session.commit()
    return jsonify([{
        'id': uchastie.id,
        'rezults': uchastie.rezultat,
        'year': uchastie.year,
        'event_name': uchastie.meropriyatie.name,
        'event_date': uchastie.meropriyatie.date,
        'event_level': uchastie.meropriyatie.uroven.uroven_name,
        'user_name': uchastie.user.fio,
        'mentor': uchastie.mentor.fio
    }]), 201

@ucastie_stud_bp.route('/api/uchastiya/stud/<int:id>', methods=['PUT'])
def stud_edit(id):
    uchastiya =Ucastie.query.get_or_404(id)
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year - 2, current_year - 1, current_year]

    meropriyatie = data['event_name']
    uroven = data['event_level']
    sroki_provedeniya = data['event_date']
    rezultat = data['rezultat']
    fio = data['fio']
    diplomi = data['diplomi']
    nagradi = data['nagradi']
    year = data['year']
    group = data['group']
    mentor = data['mentor']

    # -----------Провенрки-------------------
    if not mentor or not str(mentor).strip():
        return jsonify({'error': 'Поле Наставник обязательно к заполнению'}), 400

    if not group or not str(group).strip():
        return jsonify({'error': 'Поле Группа обязательно к заполнению'}), 400

    if not meropriyatie or not str(meropriyatie).strip():
        return jsonify({'error': 'Поле Мероприятие обязательно к заполнению'}), 400

    if not uroven or not str(uroven).strip():
        return jsonify({'error': 'Поле Уровень обязательно к заполнению'}), 400

    if not sroki_provedeniya or not str(sroki_provedeniya).strip():
        return jsonify({'error': 'Поле Сроки проведения обязательно к заполнению'}), 400

    if not rezultat or not str(rezultat).strip():
        return jsonify({'error': 'Поле Результат обязательно к заполнению'}), 400

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

    if any(char.isdigit() for char in mentor):
        return jsonify({'error': 'Поле Наставник не может содержать цифры'}), 400

    try:
        fio_ls_mentor = mentor.split()
    except:
        return jsonify({'error': 'Поле Наставник не может содержать цифры'}), 400
    if len(fio_ls_mentor) > 4:
        return jsonify({'error': 'Поле Наставник не может содержать больше 4х слов'}), 400
    if len(fio_ls_mentor) < 2:
        return jsonify({'error': 'Поле Наставник не может содержать меньше 2х слов'}), 400
    if any(len(w) < 2 for w in fio_ls_mentor):
        return jsonify({'error': 'Поле Наставник не может быть слишком коротких слов'}), 400

    if not year or not str(year).strip():
        return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
    try:
        int(year)
    except:
        return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
    if int(year) not in allow_years:
        return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[-1]}'}), 400
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #########проверка на наличие уже в бд№##############
    level = Uroven.query.filter_by(uroven_name=uroven).first()
    if not level:
        level = Uroven(uroven_name=uroven)
        db.session.add(level)
        db.session.commit()

    user = User.query.filter_by(fio=fio, group=group).first()
    if not user:
        user = User(fio=fio, group=group)
        db.session.add(user)
        db.session.commit()

    event = Meropriyatie.query.filter_by(
        name=meropriyatie,
        date=sroki_provedeniya,
        id_uroven=level.id
    ).first()
    if not event:
        event = Meropriyatie(
            name=meropriyatie,
            date=sroki_provedeniya,
            id_uroven=level.id
        )
        db.session.add(event)
        db.session.commit()
    user_mentor = User.query.filter_by(fio=mentor).first()
    if not user_mentor:
        user_mentor = User(fio=mentor)
        db.session.add(user_mentor)
        db.session.commit()

    uchastiya.rezultat = f'{rezultat}, {diplomi}, {nagradi}'
    uchastiya.year = year
    uchastiya.id_meropriyatie = event.id
    uchastiya.id_user = user.id
    uchastiya.id_mentor = user_mentor.id

    db.session.commit()


    return jsonify([{
        'id': uchastiya.id,
        'rezults': uchastiya.rezultat,
        'year': uchastiya.year,
        'event_name': uchastiya.meropriyatie.name,
        'event_date': uchastiya.meropriyatie.date,
        'event_level': uchastiya.meropriyatie.uroven.uroven_name,
        'user_name': uchastiya.user.fio,
        'group': uchastiya.user.group
    }]), 200

@ucastie_stud_bp.route('/api/uchastiya/stud/<int:id>', methods=['DELETE'])
def stud_del(id):
    uchastiya = Ucastie.query.get_or_404(id)
    db.session.delete(uchastiya)
    db.session.commit()
    return jsonify([]), 204
###############################################