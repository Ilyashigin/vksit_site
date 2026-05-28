from flask import Flask, render_template, request, redirect, jsonify, Blueprint
from models import *
from datetime import date

search_sort_bp = Blueprint('search_sort_bp', __name__, url_prefix='/api')

@search_sort_bp.route('/search')
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
        if u.user.group:
            item['user_name'] = f"{u.user.fio}({u.user.group})"

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


@search_sort_bp.route('/sort')
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
        if u.user.group:
            item['user_name'] = f"{u.user.fio}({u.user.group})"
        if int(item['year']) == int(by_year):
            result.append(item)
    if result:
        return jsonify(result)
    else:
        return jsonify([{'error': 'ничего не найдено'}]), 404