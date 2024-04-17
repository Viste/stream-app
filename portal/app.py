from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import flask_admin as admin
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_admin import helpers, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from wtforms import form, fields, validators
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'pprfnktechsekta2024'
app.config['API_KEY'] = 'pprfkebetvsehrot2024'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://sysop:0Z3tcFg7FE60YBpKdquwrQRk@pprfnkdb-primary.mariadb.svc.pprfnk.local/cyber?charset=utf8mb4'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
app.env = "production"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == app.config['API_KEY']:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"message": "Unauthorized"}), 401
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    user = Customer.query.get(int(user_id))
    print(user)
    return user


class Broadcast(db.Model):
    __tablename__ = 'broadcasts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    video_path = db.Column(db.String)
    is_live = db.Column(db.Boolean, default=False)
    course = db.relationship('Course', backref=db.backref('broadcasts', lazy=True))

    def __repr__(self):
        return f'<Broadcast {self.id} for course {self.course.name}>'


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    telegram_id = db.Column(db.String, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    allowed_courses = db.Column(db.String, nullable=False, default='academy')
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
    short_name = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)

    def __repr__(self):
        return f'<Course {self.name}>'


@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)


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
            login_user(customer)
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    if current_user:
        allowed_course_short_names = current_user.allowed_courses.split(',')
        courses = Course.query.filter(Course.short_name.in_(allowed_course_short_names)).all()
        return render_template('profile.html', account=current_user, courses=courses)
    return redirect(url_for('login'))


@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    allowed_course_short_names = current_user.allowed_courses.split(',')
    available_courses = Course.query.filter(Course.short_name.in_(allowed_course_short_names)).all()
    live_broadcasts = Broadcast.query.join(Course).filter(Broadcast.is_live == True, Course.short_name.in_(allowed_course_short_names)).all()
    print("Live Broadcasts:", live_broadcasts)
    return render_template('stream.html', account=current_user, courses=available_courses, live_broadcasts=live_broadcasts)


@app.route('/course/<short_name>')
@login_required
def course_page(short_name):
    course = Course.query.filter_by(short_name=short_name).first_or_404()
    broadcasts = Broadcast.query.filter_by(course_id=course.id, is_live=False).all()
    return render_template('course_page.html', course=course, broadcasts=broadcasts)


@app.route('/howto')
@login_required
def howto():
    return render_template('howto.html', account=current_user)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/api/start_broadcast', methods=['POST'])
@require_api_key
def start_broadcast():
    data = request.json
    course = Course.query.filter_by(short_name=data['short_name']).first()
    if course:
        new_broadcast = Broadcast(course_id=course.id, is_live=True)
        db.session.add(new_broadcast)
        db.session.commit()
        return jsonify({"message": "Broadcast started successfully", "broadcast_id": new_broadcast.id}), 200
    return jsonify({"message": "Course not found"}), 404


@app.route('/api/end_broadcast', methods=['POST'])
@require_api_key
def end_broadcast():
    data = request.json
    broadcast = Broadcast.query.filter_by(id=data['broadcast_id']).first()
    if broadcast:
        broadcast.is_live = False
        broadcast.video_path = data['video_path']
        db.session.commit()
        return jsonify({"message": "Broadcast ended successfully"}), 200
    return jsonify({"message": "Broadcast not found"}), 404


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


admin = admin.Admin(app, name='Stream Neuropunk Academy', index_view=MyAdminIndexView(), base_template='admin/my_master.html',
                    template_mode='bootstrap4', url='/admin')
admin.add_view(MyModelView(Course, db.session, category="Courses Management"))
admin.add_view(MyModelView(Customer, db.session, category="Users Management"))
admin.add_view(MyModelView(Broadcast, db.session, category="Broadcast Management"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
