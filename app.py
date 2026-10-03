from flask import Flask, jsonify

from models import db, User, Event, Level, Participation
from api.level_api import level_bp
from api.users_api import user_bp
from api.event_api import event_bp
from api.participation_teacher_api import participation_teacher_bp
from api.participation_student_api import participation_student_bp
from api.search_sort import search_sort_bp
from api.report_api import report_bp
from view.main_view import main_view_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_participation.db'
db.init_app(app)
app.debug = True

app.register_blueprint(level_bp)
app.register_blueprint(user_bp)
app.register_blueprint(event_bp)
app.register_blueprint(participation_teacher_bp)
app.register_blueprint(participation_student_bp)
app.register_blueprint(search_sort_bp)
app.register_blueprint(report_bp)
app.register_blueprint(main_view_bp)


@app.route('/api/options', methods=['GET'])
def get_options():
    groups = list({
        user.group for user in User.query.all()
        if user.group and user.group.strip()
    })

    users = [
        {'id': user.id, 'full_name': user.full_name, 'group': user.group}
        for user in User.query.all()
    ]
    events = [
        {
            'name': event.name,
            'date': event.date,
            'description': event.description or '',
            'level_name': event.level.name,
        }
        for event in Event.query.all()
    ]
    levels = [{'name': level.name} for level in Level.query.all()]
    periods = (
        db.session.query(Participation.year1, Participation.year2)
        .distinct()
        .order_by(Participation.year1.desc(), Participation.year2.desc())
        .all()
    )
    years = [f'{year1}-{year2}' for year1, year2 in periods]

    return jsonify({
        'users': users,
        'events': events,
        'levels': levels,
        'groups': [{'name': group} for group in groups],
        'years': years,
    })


if __name__ == '__main__':
    app.run(debug=True)
