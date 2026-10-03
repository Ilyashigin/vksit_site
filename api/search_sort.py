from flask import request, jsonify, Blueprint

from models import Participation
from api.participation_helpers import participation_to_dict

search_sort_bp = Blueprint('search_sort_bp', __name__, url_prefix='/api')


def _parse_period(period):
    try:
        year1, year2 = period.split('-')
        return int(year1), int(year2)
    except (ValueError, AttributeError):
        return None, None


def _contains(value, query):
    if not query:
        return True
    if not value:
        return False
    return query.lower() in str(value).lower()


@search_sort_bp.route('/filter')
def filter_participations():
    user_type = request.args.get('user_type', '').strip() or None
    period = request.args.get('year', '').strip()
    level = request.args.get('level', '').strip()
    event = request.args.get('event', '').strip()
    full_name = request.args.get('full_name', '').strip()
    mentor = request.args.get('mentor', '').strip()
    group = request.args.get('group', '').strip()

    year1, year2 = _parse_period(period) if period else (None, None)
    if period and year1 is None:
        return jsonify([{'error': 'Укажите период в формате XXXX-XXXX'}]), 400

    has_filter = any([period, level, event, full_name, mentor, group])
    if not has_filter:
        return jsonify([{'error': 'Укажите хотя бы один параметр фильтра'}]), 400

    query = Participation.query
    if year1 is not None:
        query = query.filter_by(year1=year1, year2=year2)

    result = []
    for participation in query.order_by(Participation.id).all():
        item = participation_to_dict(participation, user_type)
        if not item:
            continue

        if not _contains(item['level_name'], level):
            continue
        if not _contains(item['event_name'], event):
            continue
        if not _contains(item['participant_name'], full_name):
            continue
        if user_type == 'student':
            if not _contains(item.get('mentor', ''), mentor):
                continue
            if not _contains(item.get('group', ''), group):
                continue

        result.append(item)

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404


@search_sort_bp.route('/search')
def search_participations():
    event = request.args.get('event', '').strip()
    event_chars = [char for char in event]
    full_name = request.args.get('full_name', '').strip()
    name_chars = [char for char in full_name]
    user_type = request.args.get('user_type', '').strip() or None

    result = []
    seen_ids = set()

    for participation in Participation.query.all():
        item = participation_to_dict(participation, user_type)
        if not item:
            continue

        event_name = item['event_name']
        participant_label = item['participant_name']
        if item.get('group'):
            participant_label = f"{item['participant_name']}({item['group']})"

        matched = False
        if event:
            count_event = sum(1 for char in event_name if char in event_chars)
            if count_event >= 3:
                matched = True

        if full_name:
            count_name = sum(1 for char in participant_label if char in name_chars)
            if count_name >= 3:
                matched = True

        if (event or full_name) and matched and item['id'] not in seen_ids:
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
    for participation in Participation.query.filter_by(year1=year1, year2=year2).order_by(Participation.id).all():
        item = participation_to_dict(participation, user_type)
        if item:
            result.append(item)

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404


@search_sort_bp.route('/sort_by_id')
def sort_by_id():
    user_type = request.args.get('user_type', '').strip() or None
    result = []

    for participation in Participation.query.order_by(Participation.id).all():
        item = participation_to_dict(participation, user_type)
        if item:
            result.append(item)

    if result:
        return jsonify(result), 200
    return jsonify([{'error': 'ничего не найдено'}]), 404
