from datetime import date

from models import db, Level, Event, User, Participation
from api.date_utils import (
    parse_and_format_event_period,
    academic_year_from_date,
    validate_academic_year,
)


def is_student(user):
    return bool(user.group and str(user.group).strip())


def participation_to_dict(participation, user_type=None):
    student = is_student(participation.user)
    if user_type == 'teacher' and student:
        return None
    if user_type == 'student' and not student:
        return None

    item = {
        'id': participation.id,
        'results': participation.result,
        'year': f'{participation.year1}-{participation.year2}',
        'event_name': participation.event.name,
        'event_date': participation.event.date,
        'description': participation.event.description or '',
        'level_name': participation.event.level.name,
        'participant_name': participation.user.full_name,
    }
    if student:
        item['group'] = participation.user.group
        item['mentor'] = participation.mentor.full_name if participation.mentor else ''
    return item


def validate_full_name(full_name, field_label='ФИО'):
    if not full_name or not str(full_name).strip():
        return f'Поле {field_label} обязательно к заполнению'
    if any(char.isdigit() for char in full_name):
        return f'Поле {field_label} не может содержать цифры'
    parts = full_name.split()
    if len(parts) > 4:
        return f'Поле {field_label} не может содержать больше 4х слов'
    if len(parts) < 2:
        return f'Поле {field_label} не может содержать меньше 2х слов'
    if any(len(word) < 2 for word in parts):
        return f'Поле {field_label} не может быть слишком коротких слов'
    return None


def get_allow_years(offset_before=5, offset_after=1):
    current_year = date.today().year
    return [
        current_year - offset_before + i
        for i in range(offset_before + offset_after + 1)
    ]


def parse_event_date_and_year(event_date, allow_years):
    stored_date, event_date_obj, date_err = parse_and_format_event_period(event_date)
    if date_err:
        return None, None, None, date_err
    year1, year2 = academic_year_from_date(event_date_obj)
    year_err, year_code = validate_academic_year(year1, year2, allow_years)
    if year_err:
        return None, None, None, year_err
    return stored_date, year1, year2, None


def get_or_create_level(level_name):
    level = Level.query.filter_by(name=level_name).first()
    if not level:
        level = Level(name=level_name)
        db.session.add(level)
        db.session.commit()
    return level


def normalize_description(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def get_or_create_event(event_name, event_date, level_id, description=None):
    normalized_description = normalize_description(description)
    event = Event.query.filter_by(name=event_name, date=event_date, level_id=level_id).first()
    if not event:
        event = Event(
            name=event_name,
            date=event_date,
            level_id=level_id,
            description=normalized_description,
        )
        db.session.add(event)
        db.session.commit()
    else:
        event.description = normalized_description
        db.session.commit()
    return event


def get_or_create_user(full_name, group=None):
    if group:
        user = User.query.filter_by(full_name=full_name, group=group).first()
        if not user:
            user = User(full_name=full_name, group=group)
            db.session.add(user)
            db.session.commit()
        return user

    user = User.query.filter_by(full_name=full_name).first()
    if not user:
        user = User(full_name=full_name)
        db.session.add(user)
        db.session.commit()
    return user


def build_result_text(result, diplomas, awards):
    return f'{result}, {diplomas}, {awards}'
