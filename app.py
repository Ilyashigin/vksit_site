import flask
from flask import Flask, render_template, request, redirect
from models import *
from api.uroven_api import level_bp
from api.users_api import user_bp
from api.meropriyatiya_api import event_bp
from api.uchastiya_ped_api import ucastie_ped_bp
from api.uchastiya_stud_api import ucastie_stud_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uchet_meropriyatiy.db'
db.init_app(app)
app.debug = True

app.register_blueprint(level_bp)
app.register_blueprint(user_bp)
app.register_blueprint(event_bp)
app.register_blueprint(ucastie_ped_bp)
app.register_blueprint(ucastie_stud_bp)

@app.route('/')
def enter():
    return f'heloooo'

if __name__ == '__main__':
    app.run(debug=True)