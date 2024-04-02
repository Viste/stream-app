from flask import Flask, render_template, request, redirect, url_for, session
import flask_admin as admin
import flask_login as login
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import expose, helpers
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from wtforms import form, fields, validators
import re

app = Flask(__name__, static_folder='public/static', template_folder='public/templates')

app.config['SECRET_KEY'] = 'pprfnktechsekta2024'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://sysop:0Z3tcFg7FE60YBpKdquwrQRk@pprfnkdb-primary.mariadb.svc.pprfnk.local/cyber?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.env = "production"


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
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
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            existing_user = Customer.query.filter_by(username=username).first()
            if existing_user:
                msg = 'Account already exists!'
            else:
                # Хешируем пароль перед сохранением
                hashed_password = generate_password_hash(password, method='sha256')
                new_user = Customer(username=username, password=hashed_password, email=email, allowed_courses='', is_moderator=False, is_admin=False, is_banned=False)
                db.session.add(new_user)
                db.session.commit()
                msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)


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
            raise validators.ValidationError('Invalid user')

        if not check_password_hash(user.password_hash, self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(Customer).filter_by(username=self.login.data).first()


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/admin')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('admin/login'))
        return super(MyAdminIndexView, self).index()


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin/login', next=request.url))


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/admin')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/admin/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).render('admin/login.html')

    @expose('/admin/logout/')
    def logout_view(self):
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('admin/login'))


admin = admin.Admin(app, name='Stream Neuropunk Academy', index_view=MyAdminIndexView(), base_template='my_master.html', template_mode='bootstrap4', url='/admin')
admin.add_view(MyModelView(menu_class_name='Управление Курсами', model=Course, session=db.session, category="Управление базой"))
admin.add_view(MyModelView(menu_class_name='ТУправление Пользователями', model=Customer, session=db.session))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
