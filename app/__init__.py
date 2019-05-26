# -*- coding: utf-8 -*-
from flask import Flask
from flask_script import Manager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app.documents.blueprint import documents
from app.models import User, Role
from . import routes

app.register_blueprint(documents, url_prefix='/documents')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def create_user():
    if not User.query.first():
        db.create_all()
        admin_role = user_datastore.create_role(
            name='admin', description='Admin role')

        user_role = user_datastore.create_role(
            name='registered', description='User role')

        user_datastore.create_user(
            username='admin', email='admin@test.tt',
            password='password', active=True,
            roles=[admin_role]
        )

        user_datastore.create_user(
            username='user', email='user@test.tt',
            password='password', active=True,
            roles=[user_role]
        )
        db.session.commit()
