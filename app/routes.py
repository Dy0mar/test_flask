# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for
from flask_login import login_required, logout_user, current_user

from app import app


@app.route('/')
@app.route('/index/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('documents.index'))
    return render_template('index.html', home_page=True)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
