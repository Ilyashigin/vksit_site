from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Participation(db.Model):
    __tablename__ = 'participation'

    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(300), nullable=False)
    year1 = db.Column(db.Integer, nullable=False)
    year2 = db.Column(db.Integer, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    event = db.relationship('Event', backref='participations', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], backref='participations')
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref='mentored_participations')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(250), nullable=False)
    group = db.Column(db.String(50), nullable=True)


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)

    level = db.relationship('Level', backref='events', lazy=True)


class Level(db.Model):
    __tablename__ = 'level'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
