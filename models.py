from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref, lazyload

db = SQLAlchemy()



class Ucastie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rezultat = db.Column(db.String(300), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    id_meropriyatie = db.Column(db.Integer, db.ForeignKey('meropriyatie.id'), nullable=False)

    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_mentor = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', foreign_keys=[id_user], backref='ucastie_main')
    mentor = db.relationship('User', foreign_keys=[id_mentor], backref='ucastie_optional')


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fio = db.Column(db.String(250), nullable=False)
    group = db.Column(db.String(50), nullable=True)


class Meropriyatie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(150), nullable=False)

    id_uroven = db.Column(db.Integer, db.ForeignKey('uroven.id'), nullable=False)

    ucastie = db.relationship('Ucastie', backref='meropriyatie', lazy=True)

class Uroven(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uroven_name = db.Column(db.String(100), nullable=False)

    meropriyatie = db.relationship('Meropriyatie', backref='uroven', lazy=True)
