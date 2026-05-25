from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

main_view_bp = Blueprint('main_view_bp', __name__)

@main_view_bp.route('/')
def index():
    return redirect('/rabotniki')

@main_view_bp.route('/rabotniki')
def ped_rab_page():
    return render_template('uchastiya.html', user_type='ped', title='Пед. работники')

@main_view_bp.route('/students')
def stud_page():
    return render_template('uchastiya.html', user_type='stud', title='Студенты')

@main_view_bp.route('/users')
def user_page():
    return render_template('users_view.html')

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
