import os
import os.path as op

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla

import tm470webapp.views

# Create application
app = Flask('tm470webapp')

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


class User(db.Model):
    '''
    User model for registered app users
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))


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
class FileView(sqla.ModelView):
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


class UserView(sqla.ModelView):
    '''
    This class demonstrates the use of 'rules' for controlling the rendering of forms.
    '''
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


# Create admin
admin = Admin(app, 'tm470 webapp', template_mode='bootstrap3')

# Add views
admin.add_view(FileView(File, db.session, name='Files'))
admin.add_view(UserView(User, db.session, name='Users'))

# Flask views
@app.route('/')
def index():
        # return 'Hello World!'
        # db.create_all()
    return '<a href="/admin/">Click here to get to Admin!</a>'
