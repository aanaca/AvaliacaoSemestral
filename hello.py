import os
from flask import abort
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True)
    semestre = db.Column(db.String(20))

    def __repr__(self):
        return f'<Disciplina {self.nome} - {self.semestre}>'


class DisciplinaForm(FlaskForm):
    nome = StringField('Nome da Disciplina', validators=[DataRequired()])
    semestre = SelectField('Semestre', choices=[
        ('1º semestre', '1º semestre'),
        ('2º semestre', '2º semestre'),
        ('3º semestre', '3º semestre'),
        ('4º semestre', '4º semestre'),
        ('5º semestre', '5º semestre'),
        ('6º semestre', '6º semestre')
    ])
    submit = SubmitField('Cadastrar')

@app.route('/cadastro/disciplinas', methods=['GET', 'POST'])
def cadastro_disciplinas():
    form = DisciplinaForm()
    if form.validate_on_submit():
        disciplina = Disciplina(nome=form.nome.data, semestre=form.semestre.data)
        db.session.add(disciplina)
        db.session.commit()
        return redirect(url_for('cadastro_disciplinas'))
    
    disciplinas = Disciplina.query.all()
    return render_template('cadastro_disciplinas.html', form=form, disciplinas=disciplinas)


@app.route('/cadastro/aluno')
def cadastro_aluno():
    abort(404)


@app.route('/cadastro/professores')
def cadastro_professores():
  abort(404)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/user/<name>/<prontuario>/<institution>')
def user(name, prontuario, institution):
    current_time = datetime.now()
    return render_template('user.html', 
                           name=name, 
                           prontuario=prontuario,
                           institution=institution,
                        current_time=current_time);

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            role_name = form.role.data
            user_role = Role.query.filter_by(name=role_name.capitalize()).first()

            if user_role is None:
                user_role = Role(name=role_name.capitalize())
                db.session.add(user_role)
                db.session.commit()

            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True

        session['name'] = form.name.data
        return redirect(url_for('index'))

    current_time = datetime.utcnow()
    return render_template('index.html', 
                           name=session.get('name', 'Estranho'),
                           prontuario=session.get('prontuario', 'N/A'),
                           current_time=current_time)

