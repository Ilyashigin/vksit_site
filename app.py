from tokenize import group

import flask
from flask import Flask, render_template, request, redirect
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uchet_meropriyatiy.db'
db.init_app(app)
app.debug = True

@app.route('/')
def index():
    return redirect('/rabotniki')

@app.route('/rabotniki')
def ped_rab():
    uchastiya = Ucastie.query.all()
    return render_template('ped_rab.html', uchastiya = uchastiya)

@app.route('/rabotniki/add', methods=['GET','POST'])
def ped_rab_add():
    if request.method == 'POST':
        meropriyatie = request.form['meropriyatie']
        uroven = request.form['uroven']
        sroki_provedeniya = request.form['sroki_provedeniya']
        rezultat = request.form['rezultat']
        fio = request.form['fio']
        diplomi = request.form['diplomi']
        nagradi =request.form['nagradi']


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

        mer = Meropriyatie(name=meropriyatie, date=sroki_provedeniya, uroven=ur)
        db.session.add(mer)
        db.session.commit()

        uchastie = Ucastie(rezultat=f"{rezultat}, {diplomi}, {nagradi}", meropriyatie=mer, user=us)
        db.session.add(uchastie)
        db.session.commit()
        return redirect('/rabotniki')
    return render_template('ped_rab_add.html')


@app.route('/rabotniki/edit/<int:id>', methods=['GET','POST'])
def ped_rab_edit(id):
    uchastiya =Ucastie.query.get_or_404(id)
    if request.method == 'POST':
        uchastiya.meropriyatie.name = request.form['meropriyatie']
        uchastiya.meropriyatie.uroven.uroven_name = request.form['uroven']
        uchastiya.meropriyatie.date = request.form['sroki_provedeniya']
        rezultat = request.form['rezultat']
        diplomi = request.form['diplomi']
        nagradi = request.form['nagradi']
        uchastiya.rezultat = f'{rezultat}, {diplomi}, {nagradi}'
        uchastiya.user.fio = request.form['fio']
        db.session.commit()
        return redirect('/rabotniki')
    return render_template('ped_rab_edit.html', uchastiya=uchastiya)


@app.route('/rabotniki/delete/<int:id>', methods=['POST'])
def ped_rab_del(id):
    uchastiya =Ucastie.query.get_or_404(id)
    db.session.delete(uchastiya)
    db.session.commit()
    return redirect('/')


#############СТУДЕНТЫ№№№№№№№№№№№№№№№№№№№№№№№№

@app.route('/students')
def students():
    uchastiya = Ucastie.query.all()
    return render_template('students.html', uchastiya = uchastiya)

@app.route('/students/add', methods=['GET','POST'])
def students_add():
    if request.method == 'POST':
        meropriyatie = request.form['meropriyatie']
        uroven = request.form['uroven']
        sroki_provedeniya = request.form['sroki_provedeniya']
        rezultat = request.form['rezultat']
        fio = request.form['fio']
        diplomi = request.form['diplomi']
        nagradi = request.form['nagradi']
        group = request.form['group']
        fio_nastavnika = request.form['fio_nastavnika']

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

        us_null = User(fio=fio_nastavnika)
        existing = User.query.filter_by(fio=fio_nastavnika).first()
        if not existing:
            db.session.add(us)
            db.session.commit()
            print("Комит юзера")
        else:
            print("Уже есть:", existing.fio)

        mer = Meropriyatie(name=meropriyatie, date=sroki_provedeniya, uroven=ur)
        db.session.add(mer)
        db.session.commit()


        uchastie = Ucastie(rezultat=f"{rezultat}, {diplomi}, {nagradi}", meropriyatie=mer, user=us, user_null=us_null)
        db.session.add(uchastie)
        db.session.commit()
        return redirect('/students')
    return render_template('students_add.html')


@app.route('/students/edit/<int:id>', methods=['GET','POST'])
def students_edit(id):
    uchastiya = Ucastie.query.get_or_404(id)
    if request.method == 'POST':
        uchastiya.meropriyatie.name = request.form['meropriyatie']
        uchastiya.meropriyatie.uroven.uroven_name = request.form['uroven']
        uchastiya.meropriyatie.date = request.form['sroki_provedeniya']
        rezultat = request.form['rezultat']
        diplomi = request.form['diplomi']
        nagradi = request.form['nagradi']
        uchastiya.rezultat = f'{rezultat}, {diplomi}, {nagradi}'
        uchastiya.user.fio = request.form['fio']
        uchastiya.user.group = request.form['group']
        uchastiya.user_null.fio = request.form['fio_nastavnika']
        db.session.commit()
        return redirect('/students')
    return render_template('students_edit.html', uchastiya=uchastiya)


@app.route('/students/delete/<int:id>', methods=['POST'])
def students_del(id):
    uchastiya =Ucastie.query.get_or_404(id)
    db.session.delete(uchastiya)
    db.session.commit()
    return redirect('/students')


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/user_stud_add', methods=['POST', 'GET'])
def user_stud_add():
    if request.method == 'POST':
        fio = request.form['fio']
        group = request.form['group']
        existing = User.query.filter_by(fio=fio).first()
        if not existing:
            us = User(fio=fio, group=group)
            db.session.add(us)
            db.session.commit()
            print("Комит юзера")
        else:
            print("Уже есть:", existing.fio)
        return redirect('/users')
    return render_template('user_stud_add.html')

@app.route('/user_ped_add', methods=['POST', 'GET'])
def user_ped_add():
    if request.method == 'POST':
        fio = request.form['fio']
        existing = User.query.filter_by(fio=fio).first()
        if not existing:
            us = User(fio=fio)
            db.session.add(us)
            db.session.commit()
            print("Комит юзера")
        else:
            print("Уже есть:", existing.fio)
        return redirect('/users')
    return render_template('user_ped_add.html')

@app.route('/user_edit/<int:id>', methods=['GET','POST'])
def user_edit(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        if user.group == None:
            user.fio = request.form['fio']
        else:
            user.fio = request.form['fio']
            user.group = request.form['group']
        db.session.commit()
        return redirect('/users')
    return render_template('user_edit.html', user = user)

@app.route('/user_del/<int:id>', methods=['POST'])
def user_del(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')





'''
####################ОТЧЕТ№№№№№№№№№№№№№№№№№№№№№№№№

@app.route('/rabotniki/download')
def ped_rab_download():
    rabs = Rabotnik.query.all()
    with open("otchet.txt", "w", encoding="utf8") as file:
        for rab in rabs:
            file.write(f"№ { rab.id } Мероприятие: { rab.meropriyatie } Уровень: { rab.uroven } Сроки проведения: { rab.sroki_provedeniya } Результаты: { rab.rezultat } ФИО: { rab.fio } Дипломы: { rab.diplomi } Награды: { rab.nagradi }\n" )

    print("Файл записан")
    return redirect('/rabotniki')'''
