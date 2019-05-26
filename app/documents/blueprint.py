# -*- coding: utf-8 -*-
import datetime

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    abort)
from flask_login import current_user, login_required
from sqlalchemy.sql.functions import current_timestamp

from app import db
from app.documents.forms import DocumentForm, DocumentModelForm
from app.models import Document, Source, slugify
from flask import current_app as app

documents = Blueprint('documents', __name__, template_folder='templates')


def save_db(o):
    try:
        db.session.add(o)
        db.session.commit()
    except Exception as e:
        return False
    return True


@documents.route('/')
@login_required
def index():
    q = request.args.get('q')

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    docs = Document.query.order_by(Document.id.asc())

    if q:
        docs = Document.query.filter(
            Document.title.contains(q) | Document.text.contains(q)
        )
    pages = docs.paginate(page=page, per_page=5)

    return render_template(
        'documents/index.html', pages=pages, documents_page=True)


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
        saved = save_db(document)
        if saved:
            return redirect(url_for('documents.index'))
        else:
            flash('Документ не был создан')

    return render_template(
        'documents/create.html', document_create_page=True, form=form
    )


@documents.route('/edit/<int:pk>', methods=['POST', 'GET'])
@login_required
def edit_document(pk):
    document = Document.query.filter_by(id=pk).first()
    time_edit_limit = document.created_at + datetime.timedelta(hours=1)

    if not current_user.has_role('admin'):
        if time_edit_limit <= datetime.datetime.now():
            flash('Time is up')
            return redirect(url_for('documents.index'))

    if request.method == 'POST':
        cnt = document.editor_count or 0
        cnt += 1
        document.editor_count = cnt
        document.updated_at = current_timestamp()
        db.session.add(document)
        db.session.commit()

        form = DocumentModelForm(formdata=request.form, obj=document)
        form.populate_obj(document)
        db.session.commit()
        return redirect(url_for('documents.index'))

    form = DocumentModelForm(obj=document)
    return render_template('documents/edit.html', document_edit_page=True,
                           document=document, form=form)


@documents.route('/generate_documents/',)
@login_required
def generate_documents():
    title = 'Document {}'
    text = render_template('documents/generate_text/text.html')
    created = current_timestamp()
    url = '{}{}'

    for i in range(1, app.config['GENERATE_COUNT_DOCUMENTS']):
        tmp_url = url.format(format(request.base_url), i)
        tmp_text = '{} {}'.format(text, i)
        source = Source(name='Source {}'.format(i), url=tmp_url)
        save_db(source)

        document = Document(
            title=title.format(i), text=tmp_text, created=created,
            author=current_user, source=source,
            url=slugify(title.format(i))
        )
        save_db(document)
    return redirect(url_for('documents.index'))
