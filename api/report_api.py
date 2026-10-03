import io
import os

from flask import Blueprint, request, send_file

from models import Participation, Event, Level
from api.participation_helpers import is_student

report_bp = Blueprint('report_bp', __name__, url_prefix='/api/report')

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'templates',
    'report_template.docx',
)

PED_TITLE = (
    'Участие педагогических работников в конференциях, семинарах, конкурсах '
    'профессионального мастерства регионального, федерального уровней в {period} уч году'
)
STUD_TITLE = (
    'Участие студентов в конференциях, олимпиадах, соревнованиях, конкурсах '
    'профессионального мастерства регионального, всероссийского, международного '
    'уровней в {period} уч. году'
)
TABLE_HEADERS = [
    '№',
    'Наименование мероприятия',
    'Уровень мероприятия',
    'Сроки проведения',
    'Результат ФИО участника Дипломы, награды',
]


def _parse_period(period):
    year1, year2 = period.split('-')
    return int(year1), int(year2)


def _format_result_column(participation, student):
    parts = [part.strip() for part in (participation.result or '').split(',')]
    result = parts[0] if parts else ''
    diplomas = parts[1] if len(parts) > 1 else ''
    awards = parts[2] if len(parts) > 2 else ''

    chunks = []
    if student and participation.user.group:
        chunks.append(f'{participation.user.full_name} ({participation.user.group})')
    else:
        chunks.append(participation.user.full_name)

    if result:
        chunks.append(result)
    if diplomas:
        chunks.append(diplomas)
    if awards:
        chunks.append(awards)

    if student and participation.mentor:
        chunks.append(f'(наставник {participation.mentor.full_name})')

    return ' '.join(chunks).strip()


def _group_rows(rows):
    grouped = {}
    order = []

    for row in rows:
        key = row['event_key']
        if key not in grouped:
            grouped[key] = {
                'event_name': row['event_name'],
                'level_name': row['level_name'],
                'event_date': row['event_date'],
                'result_parts': [],
            }
            order.append(key)
        grouped[key]['result_parts'].append(row['result_col'])

    result = []
    for key in order:
        item = grouped[key]
        parts = [part for part in item['result_parts'] if part]
        result.append({
            'event_name': item['event_name'],
            'level_name': item['level_name'],
            'event_date': item['event_date'],
            'result_col': '\n'.join(parts),
        })
    return result


def _fetch_records(year1, year2, report_type, sort, user_id=None):
    query = Participation.query.filter_by(year1=year1, year2=year2)
    if user_id:
        query = query.filter_by(user_id=user_id)

    if sort == 'id':
        query = query.order_by(Participation.id)
    elif sort == 'level':
        query = query.join(Participation.event).join(Event.level).order_by(Level.name, Participation.id)
    else:
        query = query.join(Participation.event).order_by(Event.date, Participation.id)

    teacher_rows = []
    student_rows = []

    for participation in query.all():
        student = is_student(participation.user)
        row = {
            'event_key': participation.event_id,
            'event_name': participation.event.name,
            'level_name': participation.event.level.name,
            'event_date': participation.event.date,
            'result_col': _format_result_column(participation, student),
        }
        if student:
            student_rows.append(row)
        else:
            teacher_rows.append(row)

    if report_type == 'teacher':
        student_rows = []
    elif report_type == 'student':
        teacher_rows = []

    return _group_rows(teacher_rows), _group_rows(student_rows)


def _set_cell_text(cell, text, bold=False):
    cell.text = ''
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(str(text))
    run.bold = bold


def _fill_table(table, rows):
    while len(table.rows) > 1:
        table._tbl.remove(table.rows[-1]._tr)

    for idx, row in enumerate(rows, start=1):
        cells = table.add_row().cells
        _set_cell_text(cells[0], idx)
        _set_cell_text(cells[1], row['event_name'])
        _set_cell_text(cells[2], row['level_name'])
        _set_cell_text(cells[3], row['event_date'])
        _set_cell_text(cells[4], row['result_col'])


def _replace_title_paragraph(doc, old_fragment, new_text):
    for paragraph in doc.paragraphs:
        if old_fragment in paragraph.text:
            paragraph.text = new_text
            return True
    return False


def _generate_report(year1, year2, report_type, sort, user_id=None):
    from docx import Document

    period = f'{year1}-{year2}'
    teacher_rows, student_rows = _fetch_records(year1, year2, report_type, sort, user_id)

    if not teacher_rows and not student_rows:
        return None

    doc = Document(TEMPLATE_PATH)

    _replace_title_paragraph(
        doc,
        'Участие педагогических работников',
        PED_TITLE.format(period=period),
    )
    _replace_title_paragraph(
        doc,
        'Участие студентов',
        STUD_TITLE.format(period=period),
    )

    if len(doc.tables) >= 1 and teacher_rows:
        _fill_table(doc.tables[0], teacher_rows)
    elif len(doc.tables) >= 1:
        _fill_table(doc.tables[0], [])

    if len(doc.tables) >= 2 and student_rows:
        _fill_table(doc.tables[1], student_rows)
    elif len(doc.tables) >= 2:
        _fill_table(doc.tables[1], [])

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def _generate_report_from_scratch(year1, year2, report_type, sort, user_id=None):
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    period = f'{year1}-{year2}'
    teacher_rows, student_rows = _fetch_records(year1, year2, report_type, sort, user_id)

    if not teacher_rows and not student_rows:
        return None

    doc = Document()

    header = doc.add_paragraph('АПОУ ВО «ВКСиИТ»')
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.runs[0].bold = True
    header.runs[0].font.size = Pt(14)

    def add_section(title, rows):
        if not rows:
            return

        paragraph = doc.add_paragraph(title)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.bold = True
            run.font.size = Pt(12)

        table = doc.add_table(rows=1, cols=5)
        table.style = 'Table Grid'
        header_cells = table.rows[0].cells
        for index, name in enumerate(TABLE_HEADERS):
            _set_cell_text(header_cells[index], name, bold=True)

        _fill_table(table, rows)
        doc.add_paragraph('')

    if teacher_rows:
        add_section(PED_TITLE.format(period=period), teacher_rows)
    if student_rows:
        add_section(STUD_TITLE.format(period=period), student_rows)

    for section in doc.sections:
        section.left_margin = Cm(1.5)
        section.right_margin = Cm(1.5)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


@report_bp.route('/download')
def download_report():
    period = request.args.get('year', '').strip()
    report_type = request.args.get('type', 'all').strip()
    sort = request.args.get('sort', 'id').strip()
    user_id = request.args.get('user_id', '').strip()
    user_id = int(user_id) if user_id.isdigit() else None

    if report_type not in ('all', 'teacher', 'student'):
        return {'error': 'Неверный тип отчета'}, 400
    if sort not in ('id', 'date', 'level'):
        return {'error': 'Неверный тип сортировки'}, 400

    try:
        year1, year2 = _parse_period(period)
    except ValueError:
        return {'error': 'Период должен быть в формате XXXX-XXXX'}, 400

    try:
        if report_type == 'all' and os.path.exists(TEMPLATE_PATH) and not user_id:
            buffer = _generate_report(year1, year2, report_type, sort, user_id)
        else:
            buffer = _generate_report_from_scratch(year1, year2, report_type, sort, user_id)
    except ImportError:
        return {'error': 'Установите python-docx: pip install python-docx'}, 500

    if buffer is None:
        return {'error': 'Нет данных за выбранный период'}, 404

    filename = f'report_{period}_{report_type}.docx'
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            'application/vnd.openxmlformats-officedocument'
            '.wordprocessingml.document'
        ),
    )
