from flask import request, jsonify, Blueprint
from models import Ucastie

search_sort_bp = Blueprint('search_sort_bp', __name__, url_prefix='/api')


def _is_student(u):
    return bool(u.user.group and str(u.user.group).strip())


def _build_item(u, user_type=None):
    is_stud = _is_student(u)
    if user_type == 'ped' and is_stud:
        return None
    if user_type == 'stud' and not is_stud:
        return None

    item = {
        'id': u.id,
        'rezults': u.rezultat,
        'year': f'{u.year1}-{u.year2}',
        'event_name': u.meropriyatie.name,
        'event_date': u.meropriyatie.date,
        'event_level': u.meropriyatie.uroven.uroven_name,
        'user_name': u.user.fio,
    }
    if is_stud:
        item['group'] = u.user.group
        item['mentor'] = u.mentor.fio if u.mentor else ''
    return item


def _parse_period(period):
    try:
        year1, year2 = period.split('-')
        return int(year1), int(year2)
    except (ValueError, AttributeError):
        return None, None


@search_sort_bp.route('/search')
def search_event():
    event = request.args.get('event', '').strip()
    ev = [i for i in event]
    usr_name = request.args.get('fio', '').strip()
    us_nm = [i for i in usr_name]
    user_type = request.args.get('user_type', '').strip() or None

    result = []
    seen_ids = set()

    for u in Ucastie.query.all():
        item = _build_item(u, user_type)
        if not item:
            continue

        goal = item['event_name']
        goal_fio = item['user_name']
        if item.get('group'):
            goal_fio = f"{item['user_name']}({item['group']})"

        matched = False
        if event:
            count_ev = sum(1 for i in goal if i in ev)
            if count_ev >= 3:
                matched = True

        if usr_name:
            count_us = sum(1 for i in goal_fio if i in us_nm)
            if count_us >= 3:
                matched = True

        if (event or usr_name) and matched and item['id'] not in seen_ids:
            result.append(item)
            seen_ids.add(item['id'])

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404


@search_sort_bp.route('/sort_by_year')
def sort_by_year():
    period = request.args.get('year', '').strip()
    user_type = request.args.get('user_type', '').strip() or None
    year1, year2 = _parse_period(period)

    if year1 is None:
        return jsonify([{'error': 'Укажите период в формате XXXX-XXXX'}]), 400

    result = []
    for u in Ucastie.query.filter_by(year1=year1, year2=year2).order_by(Ucastie.id).all():
        item = _build_item(u, user_type)
        if item:
            result.append(item)

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404


@search_sort_bp.route('/sort_by_id')
def sort_by_id():
    user_type = request.args.get('user_type', '').strip() or None
    result = []

    for u in Ucastie.query.order_by(Ucastie.id).all():
        item = _build_item(u, user_type)
        if item:
            result.append(item)

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404
