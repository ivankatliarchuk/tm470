import os
import os.path as op

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla
from wtforms import fields, validators
from wtforms import form as wtform
from werkzeug.security import generate_password_hash, check_password_hash

# Create application
app = Flask(__name__)

# Create secrey key so we can use sessions
app.config['SECRET_KEY'] = 'r15Joii3oDRnm0K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Joachim:@localhost/tm470'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass


# Create models
class File(db.Model):
    '''
    File model for files saved into the database and disk
    '''
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class User(db.Model):
    '''
    User model for registered app users
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(255))
    password = db.Column(db.String(50))

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username


class PayPeriod(db.Model):
    __tablename__ = 'pay_periods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    period_name = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cutoff_date = db.Column(db.Date)

    def __str__(self):
        return self.period_name

    def __unicode__(self):
        return self.period_name


class PayGrade(db.Model):
    __tablename__ = 'pay_grades'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade_name = db.Column(db.String(255))

    def __str__(self):
        return self.grade_name

    def __unicode__(self):
        return self.grade_name


class PayRange(db.Model):
    __tablename__ = 'pay_ranges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade_id = db.Column(db.Integer, db.ForeignKey(PayGrade.id))
    period_id = db.Column(db.Integer, db.ForeignKey(PayPeriod.id))
    min = db.Column(db.Integer)
    max = db.Column(db.Integer)

    grade = db.relationship(PayGrade, backref='pay_grades')
    period = db.relationship(PayPeriod, backref='pay_periods')


# Delete hooks for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass


# Administrative views
class FileAdmin(sqla.ModelView):
    '''
    File view definition
    '''
    form_columns = ['name', 'path']

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'path': form.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': True
        }
    }


class UserAdmin(sqla.ModelView):
    '''
    This class demonstrates the use of 'rules' for controlling the rendering of forms.
    '''
    column_exclude_list = ['password', ]

    # Override password filed
    form_overrides = dict(password=fields.PasswordField)

    form_create_rules = [
        # Header and four fields. Email field will go into separate Contact section
        rules.FieldSet(('first_name', 'last_name',
                        'username', 'password'), 'Personal'),
        # Separate header and few fields
        rules.Header('Contact'),
        rules.Field('email'),

        # Show macro from Flask-Admin lib.html (it is included with 'lib' prefix)
        #        rules.Container('rule_demo.wrap', rules.Field('notes'))
    ]

    # Use same rule set for edit page
    form_edit_rules = form_create_rules


class PayPeriodAdmin(sqla.ModelView):
    '''
    Pay period admin
    '''
    form_columns = ['period_name', 'start_date', 'end_date', 'cutoff_date']


class PayGradeAdmin(sqla.ModelView):
    '''
    Grade admin view
    '''
    can_create = True
    can_delete = False
    column_editable_list = ['grade_name']


class PayRangeAdmin(sqla.ModelView):
    '''
    Pay range admin view
    '''

    form_columns = [
        'grade',
        'period',
        'min',
        'max'
    ]

    # Enable CSV export
    can_export = True


# Create admin
admin = Admin(app, 'tm470 webapp', template_mode='bootstrap3')

# Add views
admin.add_view(FileAdmin(File, db.session, name='Files'))
admin.add_view(UserAdmin(User, db.session, name='Users'))
admin.add_view(PayPeriodAdmin(PayPeriod, db.session, category='Pay Model', name='Periods'))
admin.add_view(PayGradeAdmin(PayGrade, db.session, category='Pay Model', name='Grades'))
admin.add_view(PayRangeAdmin(PayRange, db.session, category='Pay Model', name='Pay Ranges'))

import tm470webapp.views

