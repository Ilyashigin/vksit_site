

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
        db.session.add(ur)
        db.session.commit()

        us = User(fio=fio)
        db.session.add(us)
        db.session.commit()

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

'''
#############СТУДЕНТЫ№№№№№№№№№№№№№№№№№№№№№№№№

@app.route('/students')
def students():
    students = Student.query.all()
    return render_template('students.html', students = students)

@app.route('/students/add', methods=['GET','POST'])
def students_add():
    if request.method == 'POST':
        meropriyatie = request.form['meropriyatie']
        uroven = request.form['uroven']
        sroki_provedeniya = request.form['sroki_provedeniya']
        rezultat = request.form['rezultat']
        fio = request.form['fio']
        diplomi = request.form['diplomi']
        nagradi =request.form['nagradi']
        fio_nastavnika =request.form['fio_nastavnika']
        student =Student(meropriyatie=meropriyatie, uroven=uroven, sroki_provedeniya=sroki_provedeniya, rezultat=rezultat, fio=fio, diplomi=diplomi, nagradi=nagradi, fio_nastavnika=fio_nastavnika)
        db.session.add(student)
        db.session.commit()
        return redirect('/students')
    return render_template('students_add.html')


@app.route('/students/edit/<int:id>', methods=['GET','POST'])
def students_edit(id):
    student =Student.query.get_or_404(id)
    if request.method == 'POST':
        student.meropriyatie = request.form['meropriyatie']
        student.uroven = request.form['uroven']
        student.sroki_provedeniya = request.form['sroki_provedeniya']
        student.rezultat = request.form['rezultat']
        student.fio = request.form['fio']
        student.diplomi = request.form['diplomi']
        student.nagradi = request.form['nagradi']
        student.fio_nastavnika = request.form['fio_nastavnika']
        db.session.commit()
        return redirect('/students')
    return render_template('students_edit.html', student=student)


@app.route('/students/delete/<int:id>', methods=['POST'])
def students_del(id):
    student =Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect('/students')



####################ОТЧЕТ№№№№№№№№№№№№№№№№№№№№№№№№

@app.route('/rabotniki/download')
def ped_rab_download():
    rabs = Rabotnik.query.all()
    with open("otchet.txt", "w", encoding="utf8") as file:
        for rab in rabs:
            file.write(f"№ { rab.id } Мероприятие: { rab.meropriyatie } Уровень: { rab.uroven } Сроки проведения: { rab.sroki_provedeniya } Результаты: { rab.rezultat } ФИО: { rab.fio } Дипломы: { rab.diplomi } Награды: { rab.nagradi }\n" )

    print("Файл записан")
    return redirect('/rabotniki')'''
