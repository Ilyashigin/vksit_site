from venv import create

from flask import Flask, render_template, request, redirect
from models import Rabotnik, Student, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uchet_meropriyatiy.db'
db.init_app(app)
app.debug = True

@app.route('/')
def index():
    return redirect('/rabotniki')

@app.route('/rabotniki')
def ped_rab():
    rabotniki = Rabotnik.query.all()
    return render_template('ped_rab.html', rabotniki = rabotniki)

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
        rabotnik =Rabotnik(meropriyatie=meropriyatie, uroven=uroven, sroki_provedeniya=sroki_provedeniya, rezultat=rezultat, fio=fio, diplomi=diplomi, nagradi=nagradi)
        db.session.add(rabotnik)
        db.session.commit()
        return redirect('/rabotniki')
    return render_template('ped_rab_add.html')


@app.route('/rabotniki/edit/<int:id>', methods=['GET','POST'])
def ped_rab_edit(id):
    rabotnik =Rabotnik.query.get_or_404(id)
    if request.method == 'POST':
        rabotnik.meropriyatie = request.form['meropriyatie']
        rabotnik.uroven = request.form['uroven']
        rabotnik.sroki_provedeniya = request.form['sroki_provedeniya']
        rabotnik.rezultat = request.form['rezultat']
        rabotnik.fio = request.form['fio']
        rabotnik.diplomi = request.form['diplomi']
        rabotnik.nagradi = request.form['nagradi']
        db.session.commit()
        return redirect('/rabotniki')
    return render_template('ped_rab_edit.html', rabotnik=rabotnik)


@app.route('/rabotniki/delete/<int:id>', methods=['POST'])
def ped_rab_del(id):
    rabotnik =Rabotnik.query.get_or_404(id)
    db.session.delete(rabotnik)
    db.session.commit()
    return redirect('/')


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
    return redirect('/rabotniki')
