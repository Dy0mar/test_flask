# -*- coding: utf-8 -*-
from wtforms import Form, StringField, TextAreaField
from wtforms.fields.html5 import DateField
from datetime import date

from wtforms.validators import DataRequired


class DocumentForm(Form):
    title = StringField('Title')
    text = TextAreaField('Text')
    created = DateField(
        label='Start date', default=date.today(), format='%Y-%m-%d',
        validators=[DataRequired(
            message="You need to enter the created date")]
    )

    source_name = StringField('Source name')
    source_url = StringField('Source url')
