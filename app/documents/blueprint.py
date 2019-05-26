# -*- coding: utf-8 -*-
from flask import (
    Blueprint, render_template, request, redirect, url_for
)
from flask_login import current_user, login_required

from app import db
from app.documents.forms import DocumentForm
from app.models import Document, Source

documents = Blueprint('documents', __name__, template_folder='templates')


def save_db(o):
    try:
        db.session.add(o)
        db.session.commit()
    except Exception as e:
        print(e)


@documents.route('/', methods=['POST', 'GET'])
@login_required
def index():
    q = request.args.get('q')

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    docs = Document.query.all()

    if q:
        docs = Document.query.filter(
            Document.title.contains(q) | Document.text.contains(q)
        )
    pages = []

    return render_template(
        'documents/index.html', docs=docs, pages=pages, documents_page=True)


@documents.route('/create/', methods=['POST', 'GET'])
@login_required
def create_document():
    form = DocumentForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO add validate to form
        title = form.title.data
        created = form.created.data
        text = form.text.data
        source_name = form.source_name.data
        source_url = form.source_url.data
        source = Source(name=source_name, url=source_url)
        save_db(source)

        document = Document(
            title=title, text=text, created=created, author=current_user,
            source=source
        )
        save_db(document)
        return redirect(url_for('documents.index'))

    return render_template(
        'documents/create.html', document_create_page=True, form=form
    )
