from flask import Blueprint, redirect, render_template

main_view_bp = Blueprint('main_view_bp', __name__)


@main_view_bp.route('/')
def index():
    return redirect('/teachers')


@main_view_bp.route('/rabotniki')
def legacy_teachers_page():
    return redirect('/teachers')


@main_view_bp.route('/teachers')
def teachers_page():
    return render_template(
        'participation.html',
        user_type='teacher',
        title='Педагогические работники',
    )


@main_view_bp.route('/students')
def students_page():
    return render_template(
        'participation.html',
        user_type='student',
        title='Студенты',
    )


@main_view_bp.route('/users')
def users_page():
    return render_template('users_view.html')


@main_view_bp.route('/levels')
def levels_page():
    return render_template('level_view.html')


@main_view_bp.route('/events')
def events_page():
    return render_template('event_view.html')
