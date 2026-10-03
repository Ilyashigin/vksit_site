import re
from datetime import datetime


def _parse_single_date(value):
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y'):
        try:
            return datetime.strptime(value.strip(), fmt).date(), None
        except ValueError:
            continue
    return None, 'Дата должна быть в формате ДД.ММ.ГГГГ'


def parse_and_format_event_period(date_str):
    if not date_str or not str(date_str).strip():
        return None, None, 'Поле Сроки проведения обязательно к заполнению'

    value = str(date_str).strip()
    range_match = re.match(
        r'^(\d{1,2}\.\d{1,2}\.\d{4})-(\d{1,2}\.\d{1,2}\.\d{4})$',
        value,
    )

    if range_match:
        start, err = _parse_single_date(range_match.group(1))
        if err:
            return None, None, err
        end, err = _parse_single_date(range_match.group(2))
        if err:
            return None, None, err
        if end < start:
            return None, None, 'Дата окончания не может быть раньше даты начала'
        stored = (
            f'{start.strftime("%d.%m.%Y")}-{end.strftime("%d.%m.%Y")}'
        )
        return stored, start, None

    start, err = _parse_single_date(value)
    if err:
        return None, None, err
    return start.strftime('%d.%m.%Y'), start, None


def academic_year_from_date(d):
    if d.month >= 9:
        year1 = d.year
    else:
        year1 = d.year - 1
    return year1, year1 + 1


def validate_academic_year(year1, year2, allow_years):
    if int(year1) not in allow_years:
        return (
            f'Учебный Год не может быть меньше {allow_years[0]} '
            f'и больше {allow_years[-1]}'
        ), 400
    if int(year2) not in allow_years:
        return (
            f'Учебный Год не может быть меньше {allow_years[0]} '
            f'и больше {allow_years[-1]}'
        ), 400
    if (int(year2) - int(year1)) != 1:
        return 'Недопустимый учебный период', 400
    return None, None
