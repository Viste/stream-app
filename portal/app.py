from flask import Flask, render_template, request, redirect, url_for, session
import flask_admin as admin
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import helpers, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from wtforms import form, fields, validators
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = 'pprfnktechsekta2024'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://sysop:0Z3tcFg7FE60YBpKdquwrQRk@pprfnkdb-primary.mariadb.svc.pprfnk.local/cyber?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.env = "production"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = db.Column(db.String, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    allowed_courses = db.Column(db.String, nullable=False)
    is_moderator = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    is_banned = db.Column(db.Boolean)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        # пользователь активен, если он не забанен.
        return not self.is_banned

    @property
    def is_anonymous(self):
        # должно возвращать False, так как пользователи не анонимны.
        return False

    def get_id(self):
        # Возвращаем уникальный идентификатор пользователя в виде строки для управления пользовательской сессией.
        return str(self.id)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    video_path = db.Column(db.String)
    is_live = db.Column(db.Boolean)

    def __repr__(self):
        return f'<Course {self.name}>'

    @property
    def is_authenticated(self):
        return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        customer = Customer.query.filter_by(username=username).first()

        if customer and check_password_hash(customer.password, password):
            session['loggedin'] = True
            session['id'] = customer.id
            session['username'] = customer.username
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        customer = Customer.query.filter_by(id=session['id']).first()
        if customer:
            return render_template('profile.html', account=customer)
    return redirect(url_for('login'))


@app.route('/stream', methods=['GET', 'POST'])
def stream():
    streamkey = ''
    if request.method == 'POST':
        streamkey = request.form['streamkey']

    return render_template('stream.html', key=streamkey)


@app.route('/howto')
def howto():
    return render_template('howto.html')


@app.route('/about')
def about():
    return render_template('about.html')


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Вы не зарегистрированы')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Неправильный Пароль')

        if user.is_admin is False:
            raise validators.ValidationError('Вы не администратор')

        if user.is_moderator is False:
            raise validators.ValidationError('Вы не модератор')

    def get_user(self):
        return db.session.query(Customer).filter_by(username=self.login.data).first()


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).render('admin/login.html')

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.login_view'))


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = admin.Admin(app, name='Stream Neuropunk Academy', index_view=MyAdminIndexView(), base_template='my_master.html',
                    template_mode='bootstrap4', url='/admin')
admin.add_view(MyModelView(Course, db.session, category="Courses Management"))
admin.add_view(MyModelView(Customer, db.session, category="Users Management"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
