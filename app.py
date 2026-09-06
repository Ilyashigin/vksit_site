import flask
from flask import Flask, render_template, request, redirect, jsonify
from models import *
from api.uroven_api import level_bp
from api.users_api import user_bp
from api.meropriyatiya_api import event_bp
from api.uchastiya_ped_api import ucastie_ped_bp
from api.uchastiya_stud_api import ucastie_stud_bp
from api.search_sort import search_sort_bp
from api.report_api import report_bp
from view.main_view import main_view_bp


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uchet_meropriyatiy.db'
db.init_app(app)
app.debug = True

#api
app.register_blueprint(level_bp)
app.register_blueprint(user_bp)
app.register_blueprint(event_bp)
app.register_blueprint(ucastie_ped_bp)
app.register_blueprint(ucastie_stud_bp)
app.register_blueprint(search_sort_bp)
app.register_blueprint(report_bp)

#view
app.register_blueprint(main_view_bp)

@app.route('/')
def enter():
    return f'heloooo'

@app.route('/api/options', methods=['GET'])
def get_options():
    groups = list(set([u.group for u in User.query.all() if u.group and u.group.strip()]))

    users = [{'fio': u.fio, 'group': u.group} for u in User.query.all()]
    events = [{'name': m.name, 'date': m.date, 'level': m.uroven.uroven_name} for m in Meropriyatie.query.all()]
    levels = [{'name': l.uroven_name} for l in Uroven.query.all()]
    periods = (
        db.session.query(Ucastie.year1, Ucastie.year2)
        .distinct()
        .order_by(Ucastie.year1.desc(), Ucastie.year2.desc())
        .all()
    )
    years = [f'{y1}-{y2}' for y1, y2 in periods]

    return jsonify({
        'users': users,
        'events': events,
        'levels': levels,
        'groups': [{'name': g} for g in groups],
        'years': years,
    })

if __name__ == '__main__':
    app.run(debug=True)