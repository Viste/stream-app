import os
from functools import wraps

import flask_admin as admin
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_admin import helpers, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_jwt_extended import JWTManager, create_access_token
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from wtforms import form, fields, validators
from wtforms.fields import TextAreaField, IntegerField

app = Flask(__name__)
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_SECRET_KEY'] = 'pprfnktechsekta2024'
app.config['SECRET_KEY'] = 'pprfnktechsekta2024'
app.config['API_KEY'] = 'pprfkebetvsehrot2024'
app.config['UPLOAD_FOLDER'] = '/app/static/storage'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://sysop:0Z3tcFg7FE60YBpKdquwrQRk@pprfnkdb-primary.mariadb.svc.pprfnk.local/cyber?charset=utf8mb4'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

jwt = JWTManager(app)
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


class CourseProgram(db.Model):
    __tablename__ = 'course_programs'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('programs', lazy=True))


class Homework(db.Model):
    __tablename__ = 'homeworks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('homeworks', lazy=True))


class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    file_path = db.Column(db.String(255))
    grade = db.Column(db.Integer)
    comments = db.Column(db.Text)
    homework = db.relationship('Homework', backref=db.backref('submissions', lazy=True))
    student = db.relationship('Customer', backref=db.backref('submissions', lazy=True))


@app.route('/')
def index():
    slider_elements = Course.query.all()
    return render_template('index.html', courses=slider_elements)


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
        user_courses = Course.query.filter(Course.short_name.in_(allowed_course_short_names)).all()
        submissions = HomeworkSubmission.query.filter_by(student_id=current_user.id).join(Homework, Homework.id == HomeworkSubmission.homework_id).join(Course, Course.id == Homework.id).add_columns(
            Course.name, HomeworkSubmission.grade, HomeworkSubmission.comments).all()
        print(submissions)
        return render_template('profile.html', account=current_user, courses=user_courses, submissions=submissions)
    return redirect(url_for('login'))


@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    allowed_course_short_names = current_user.allowed_courses.split(',')
    available_courses = Course.query.filter(Course.short_name.in_(allowed_course_short_names)).all()
    live_broadcasts = Broadcast.query.join(Course).filter(Broadcast.is_live == True, Course.short_name.in_(allowed_course_short_names)).all()
    print("Live Broadcasts:", live_broadcasts)
    return render_template('stream.html', account=current_user, courses=available_courses, live_broadcasts=live_broadcasts)


@app.route('/howto')
@login_required
def howto():
    return render_template('howto.html', account=current_user)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/courses')
def courses():
    allowed_courses = current_user.allowed_courses.split(',')
    course_item = Course.query.filter(Course.short_name.in_(allowed_courses)).all()
    return render_template('courses.html', courses=course_item)


@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    programs = CourseProgram.query.filter_by(course_id=course.id).all()
    homeworks = Homework.query.filter_by(course_id=course.id).all()
    broadcasts = Broadcast.query.filter_by(course_id=course.id, is_live=False).all()
    identity = {'user_id': current_user.id}
    token = create_access_token(identity=identity)
    return render_template('course_detail.html', course=course, programs=programs, homeworks=homeworks, token=token, broadcasts=broadcasts)


@app.route('/submit_homework/<int:homework_id>', methods=['POST'])
@login_required
def submit_homework(homework_id):
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        db_path = "storage/" + filename
        submission = HomeworkSubmission(homework_id=homework_id, student_id=current_user.id, file_path=db_path)
        db.session.add(submission)
        db.session.commit()
        flash('Домашнее задание успешно отправлено!', 'success')
    return redirect(url_for('course_detail', course_id=Homework.query.get(homework_id).course_id))


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
        session.clear()
        return redirect(url_for('.login_view'))


class StarRatingWidget(object):
    def __call__(self, field, **kwargs):
        html = '<div class="star-rating">'
        for i in range(1, 11):
            checked = 'checked' if i == field.data else ''
            html += f'<input type="radio" name="{field.name}" value="{i}" {checked}/><label>{i}</label>'
        html += '</div>'
        return Markup(html)


class StarRatingField(IntegerField):
    widget = StarRatingWidget()


class HomeworkSubmissionAdminView(ModelView):
    form_columns = ['homework', 'student', 'file_path', 'grade', 'comments']

    column_list = ['homework', 'student', 'file_path', 'grade', 'comments']
    column_searchable_list = ['student.username', 'homework.title']
    column_filters = ['homework.course.name']

    def _list_thumbnail(self, context, model, name):
        if not model.file_path:
            return ''
        return Markup(f'<audio controls><source src="{url_for("static", filename=model.file_path)}" type="audio/mpeg"></audio>')

    form_overrides = {
        'comments': TextAreaField,
        'grade': StarRatingField
    }
    form_widget_args = {
        'comments': {
            'rows': 5,
            'style': 'color: black;'
        }
    }
    column_formatters = {
        'file_path': _list_thumbnail
    }


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = admin.Admin(app, name='Stream Neuropunk Academy', index_view=MyAdminIndexView(), base_template='admin/my_master.html',
                    template_mode='bootstrap4', url='/admin')

admin.add_view(HomeworkSubmissionAdminView(HomeworkSubmission, db.session, name="Проверка Домашек", endpoint="homeworksubmissionadmin"))

admin.add_view(MyModelView(Course, db.session, category="Таблицы", name="Курсы"))
admin.add_view(MyModelView(Customer, db.session, category="Таблицы", name="Пользователи"))
admin.add_view(MyModelView(Broadcast, db.session, category="Таблицы", name="Трансляции"))
admin.add_view(MyModelView(Homework, db.session, category="Таблицы", name="Домашки"))
admin.add_view(MyModelView(CourseProgram, db.session, category="Таблицы", name="Программа курсов"))
admin.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworksubmissionview"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
