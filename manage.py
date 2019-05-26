# -*- coding: utf-8 -*-
from app import app, db, manager
from app.models import User, Document, Source


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Document': Document,
        'Source': Source,
    }


if __name__ == '__main__':
    manager.run()
