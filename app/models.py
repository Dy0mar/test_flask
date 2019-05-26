import re

from flask_security import RoleMixin, UserMixin
from sqlalchemy.sql.functions import current_timestamp

from app import db
from datetime import datetime


def slugify(s):
    pattern = r'[^\w+]'
    s = re.sub(pattern, '-', s.lower())
    s = re.sub('--+', '-', s)
    s = re.sub('-$', '', s)
    s = re.sub('^-', '', s)
    return s


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True)
    text = db.Column(db.Text, unique=True)
    url = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=current_timestamp())
    updated_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    editor_count = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Document id {}, title {}>'.format(self.id, self.title)

    def generate_url(self):
        self.url = slugify(self.title)


# Define models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    documents = db.relationship('Document', backref='author', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.email = kwargs['email']
        self.password = kwargs['password']
        self.active = kwargs['active']
        self.roles = kwargs['roles']
        self.confirmed_at = datetime.now()

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(255))
    documents = db.relationship('Document', backref='source', lazy='dynamic')

    def __repr__(self):
        return '<Source {}, name {}>'.format(self.id, self.name)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
