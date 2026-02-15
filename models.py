from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rabotnik(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    meropriyatie = db.Column(db.String(200), nullable=False)
    uroven = db.Column(db.String(100), nullable=False)
    sroki_provedeniya = db.Column(db.String(50), nullable=False)
    rezultat = db.Column(db.String(50), nullable=False)
    fio = db.Column(db.String(250), nullable=False)
    diplomi = db.Column(db.String(250), nullable=False)
    nagradi = db.Column(db.String(250), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    meropriyatie = db.Column(db.String(200), nullable=False)
    uroven = db.Column(db.String(100), nullable=False)
    sroki_provedeniya = db.Column(db.String(50), nullable=False)
    rezultat = db.Column(db.String(50), nullable=False)
    fio = db.Column(db.String(250), nullable=False)
    diplomi = db.Column(db.String(250), nullable=False)
    nagradi = db.Column(db.String(250), nullable=False)
    fio_nastavnika = db.Column(db.String(250), nullable=False)
