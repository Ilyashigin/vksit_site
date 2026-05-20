from flask import Flask, render_template, request, redirect, jsonify
from models import *
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uchet_meropriyatiy.db'
db.init_app(app)
app.debug = True

@app.route('/api', methods=['GET'])
def home_api():
    return jsonify({'hi': 'Helloo!!!'}), 200



@app.route('/api/uchastiya/ped', methods=['GET'])
def ped_rab():
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
        #if u.user.group:
            #item['user_group'] = u.user.group
        result.append(item)
    return jsonify(result), 200

@app.route('/api/uchastiya/ped/<int:id>', methods=['GET'])
def ped_rab_by_id(id):
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
    #if u.user.group:
        #item['user_group'] = u.user.group
    return jsonify(item), 200

@app.route('/api/uchastiya/ped', methods=['POST'])
def ped_rab_add():
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year-2, current_year-1, current_year]

    if request.method == 'POST':
        meropriyatie = data['meropriyatie']
        uroven = data['uroven']
        sroki_provedeniya = data['sroki_provedeniya']
        rezultat = data['rezultat']
        fio = data['fio']
        diplomi = data['diplomi']
        nagradi = data['nagradi']
        year = data['year']

        #-----------Провенрки-------------------
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
        try:
            fio_ls = fio.split()
        except:
            return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
        if len(fio_ls) > 4:
            return jsonify({'error': 'Поле ФИО не может содержать больще 4х слов'}), 400

        if not year or not str(year).strip():
            return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
        try:
            int(year)
        except:
            return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
        if int(year) not in allow_years:
            return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[2]}'}), 400
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        #########проверка на наличие уже в бд№##############

        ur = Uroven(uroven_name=uroven)
        existing = Uroven.query.filter_by(uroven_name=uroven).first()
        if not existing:
            db.session.add(ur)
            db.session.commit()
            print("Комит уровень")
        else:
            print("Уже есть:", existing.uroven_name)

        us = User(fio=fio)
        existing = User.query.filter_by(fio=fio).first()
        if not existing:
            db.session.add(us)
            db.session.commit()
            print("Комит юзера")
        else:
            print("Уже есть:", existing.fio)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        mer = Meropriyatie(name=meropriyatie, date=sroki_provedeniya, uroven=ur)
        db.session.add(mer)
        db.session.commit()

        uchastie = Ucastie(rezultat=f"{rezultat}, {diplomi}, {nagradi}", meropriyatie=mer, user=us, year=year)
        db.session.add(uchastie)
        db.session.commit()
    return jsonify([{
        'id': uchastie.id,
        'rezults': uchastie.rezultat,
        'year': uchastie.year,
        'event_name': uchastie.meropriyatie.name,
        'event_date': uchastie.meropriyatie.date,
        'event_level': uchastie.meropriyatie.uroven.uroven_name,
        'user_name': uchastie.user.fio
    }]), 201

@app.route('/api/uchastiya/ped/<int:id>', methods=['PUT'])
def ped_rab_edit(id):
    uchastiya =Ucastie.query.get_or_404(id)
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year - 2, current_year - 1, current_year]

    meropriyatie = data['meropriyatie']
    uroven = data['uroven']
    sroki_provedeniya = data['sroki_provedeniya']
    rezultat = data['rezultat']
    fio = data['fio']
    diplomi = data['diplomi']
    nagradi = data['nagradi']
    year = data['year']

    # -----------Провенрки-------------------
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
    try:
        fio_ls = fio.split()
    except:
        return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
    if len(fio_ls) > 4:
        return jsonify({'error': 'Поле ФИО не может содержать больще 4х слов'}), 400

    if not year or not str(year).strip():
        return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
    try:
        int(year)
    except:
        return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
    if int(year) not in allow_years:
        return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[2]}'}), 400
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #########проверка на наличие уже в бд№##############

    ur = Uroven(uroven_name=uroven)
    existing = Uroven.query.filter_by(uroven_name=uroven).first()
    if not existing:
        db.session.add(ur)
        db.session.commit()
        print("Комит уровень")
    else:
        print("Уже есть:", existing.uroven_name)

    us = User(fio=fio)
    existing = User.query.filter_by(fio=fio).first()
    if not existing:
        db.session.add(us)
        db.session.commit()
        print("Комит юзера")
    else:
        print("Уже есть:", existing.fio)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    uchastiya.meropriyatie.name = meropriyatie
    uchastiya.meropriyatie.uroven.uroven_name = uroven
    uchastiya.meropriyatie.date = sroki_provedeniya
    rezultat = rezultat
    diplomi = diplomi
    nagradi = nagradi
    uchastiya.rezultat = f'{rezultat}, {diplomi}, {nagradi}'
    uchastiya.user.fio = fio
    uchastiya.year = year
    db.session.commit()
    return jsonify([{
        'id': uchastiya.id,
        'rezults': uchastiya.rezultat,
        'year': uchastiya.year,
        'event_name': uchastiya.meropriyatie.name,
        'event_date': uchastiya.meropriyatie.date,
        'event_level': uchastiya.meropriyatie.uroven.uroven_name,
        'user_name': uchastiya.user.fio
    }]), 200

@app.route('/api/uchastiya/ped/<int:id>', methods=['DELETE'])
def ped_rab_del(id):
    uchastiya = Ucastie.query.get_or_404(id)
    db.session.delete(uchastiya)
    db.session.commit()
    return jsonify([]), 204


###########STUDENTS######################
@app.route('/api/uchastiya/stud', methods=['GET'])
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
            item['user_group'] = u.user.group
            result.append(item)
    return jsonify(result), 200

@app.route('/api/uchastiya/stud/<int:id>', methods=['GET'])
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
        item['user_group'] = u.user.group
        return jsonify(item), 200

@app.route('/api/uchastiya/stud', methods=['POST'])
def stud_add():
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year-2, current_year-1, current_year]

    if request.method == 'POST':
        meropriyatie = data['meropriyatie']
        uroven = data['uroven']
        sroki_provedeniya = data['sroki_provedeniya']
        rezultat = data['rezultat']
        fio = data['fio']
        diplomi = data['diplomi']
        nagradi = data['nagradi']
        year = data['year']
        group = data['group']

        #-----------Провенрки-------------------
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
        try:
            fio_ls = fio.split()
        except:
            return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
        if len(fio_ls) > 4:
            return jsonify({'error': 'Поле ФИО не может содержать больще 4х слов'}), 400

        if not year or not str(year).strip():
            return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
        try:
            int(year)
        except:
            return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
        if int(year) not in allow_years:
            return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[2]}'}), 400
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        #########проверка на наличие уже в бд№##############
        ur = Uroven(uroven_name=uroven)
        existing = Uroven.query.filter_by(uroven_name=uroven).first()
        if not existing:
            db.session.add(ur)
            db.session.commit()
            print("Комит уровень")
        else:
            print("Уже есть:", existing.uroven_name)

        us = User(fio=fio, group=group)
        existing = User.query.filter_by(fio=fio).first()
        if not existing:
            db.session.add(us)
            db.session.commit()
            print("Комит юзера")
        else:
            print("Уже есть:", existing.fio)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        mer = Meropriyatie(name=meropriyatie, date=sroki_provedeniya, uroven=ur)
        db.session.add(mer)
        db.session.commit()
        uchastie = Ucastie(rezultat=f"{rezultat}, {diplomi}, {nagradi}", meropriyatie=mer, user=us, year=year)
        db.session.add(uchastie)
        db.session.commit()
    return jsonify([{
        'id': uchastie.id,
        'rezults': uchastie.rezultat,
        'year': uchastie.year,
        'event_name': uchastie.meropriyatie.name,
        'event_date': uchastie.meropriyatie.date,
        'event_level': uchastie.meropriyatie.uroven.uroven_name,
        'user_name': uchastie.user.fio
    }]), 201

@app.route('/api/uchastiya/stud/<int:id>', methods=['PUT'])
def stud_edit(id):
    uchastiya =Ucastie.query.get_or_404(id)
    data = request.get_json()
    current_date = date.today()
    current_year = current_date.year
    allow_years = [current_year - 2, current_year - 1, current_year]

    meropriyatie = data['meropriyatie']
    uroven = data['uroven']
    sroki_provedeniya = data['sroki_provedeniya']
    rezultat = data['rezultat']
    fio = data['fio']
    diplomi = data['diplomi']
    nagradi = data['nagradi']
    year = data['year']
    group = data['group']

    # -----------Провенрки-------------------
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
    try:
        fio_ls = fio.split()
    except:
        return jsonify({'error': 'Поле ФИО не может содержать цифры'}), 400
    if len(fio_ls) > 4:
        return jsonify({'error': 'Поле ФИО не может содержать больще 4х слов'}), 400

    if not year or not str(year).strip():
        return jsonify({'error': 'Поле Учебный Год обязательно к заполнению'}), 400
    try:
        int(year)
    except:
        return jsonify({'error': 'Поле Учебный Год должно быть числовым'}), 400
    if int(year) not in allow_years:
        return jsonify({'error': f'Учебный Год не может быть меньше {allow_years[0]} и больше {allow_years[2]}'}), 400
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #########проверка на наличие уже в бд№##############
    ur = Uroven(uroven_name=uroven)
    existing = Uroven.query.filter_by(uroven_name=uroven).first()
    if not existing:
        db.session.add(ur)
        db.session.commit()
        print("Комит уровень")
    else:
        print("Уже есть:", existing.uroven_name)

    us = User(fio=fio, group=group)
    existing = User.query.filter_by(fio=fio).first()
    if not existing:
        db.session.add(us)
        db.session.commit()
        print("Комит юзера")
    else:
        print("Уже есть:", existing.fio)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    uchastiya.meropriyatie.name = meropriyatie
    uchastiya.meropriyatie.uroven.uroven_name = uroven
    uchastiya.meropriyatie.date = sroki_provedeniya
    rezultat = rezultat
    diplomi = diplomi
    nagradi = nagradi
    uchastiya.rezultat = f'{rezultat}, {diplomi}, {nagradi}'
    uchastiya.user.fio = fio
    uchastiya.user.group = group
    uchastiya.year = year
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

@app.route('/api/uchastiya/stud/<int:id>', methods=['DELETE'])
def stud_del(id):
    uchastiya = Ucastie.query.get_or_404(id)
    db.session.delete(uchastiya)
    db.session.commit()
    return jsonify([]), 204
###############################################



#------------------sotr i poisk ---------------------------------
#________________________________________________________________
@app.route('/api/uchastiya/ped/search')
def search_event():
    event = request.args.get('event', '').strip()
    ev = [i for i in event]
    usr_name = request.args.get('fio', '').strip()
    us_nm = [i for i in usr_name]
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
        # if u.user.group:
        # item['user_group'] = u.user.group

        goal = item['event_name']
        goal_fio = item['user_name']

        count_ev = 0
        if event:
            for i in goal:
                if i in ev:
                    count_ev += 1
            if count_ev >= 3:
                result.append(item)

        count_us = 0
        if usr_name:
            for i in goal_fio:
                if i in us_nm:
                    count_us += 1
            if count_us >= 3:
                result.append(item)


    if result:
        return jsonify(result), 200
    else:
        return jsonify([{'error': 'ничего не найдено'}]), 404


@app.route('/api/uchastiya/ped/sort')
def sort():
    by_year = request.args.get('year', '').strip()
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
        if int(item['year']) == int(by_year):
            result.append(item)
    if result:
        return jsonify(result)
    else:
        return jsonify([{'error': 'ничего не найдено'}]), 404



if __name__ == '__main__':
    app.debug = True
    app.run()