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

@main_view_bp.route('/levels')
def level_page():
    return render_template('level_view.html')

@main_view_bp.route('/events')
def event_page():
    return render_template('event_view.html')
