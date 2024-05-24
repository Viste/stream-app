from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

db = SQLAlchemy()


class Broadcast(db.Model):
    __tablename__ = 'broadcasts'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    video_path = db.Column(db.String(255))
    is_live = db.Column(db.Boolean, default=False)
    course = db.relationship('Course', backref=db.backref('broadcasts', lazy=True))
    title = db.Column(db.String(255))

    def __repr__(self):
        return f'<Broadcast {self.id} for course {self.course.name}>'


class Customer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, unique=True, autoincrement=True)
    telegram_id = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255))
    allowed_courses = db.Column(db.String(255), nullable=False, default='academy')
    is_moderator = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    is_banned = db.Column(db.Boolean)
    is_podpivas = db.Column(db.Boolean, default=False, nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    headphones = db.Column(db.String(255), nullable=True)
    sound_card = db.Column(db.String(255), nullable=True)
    pc_setup = db.Column(db.Text, nullable=True)

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
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    students = db.relationship('Customer', secondary='course_registrations', back_populates='courses')

    def __repr__(self):
        return f'<Course {self.name}>'


class CourseRegistration(db.Model):
    __tablename__ = 'course_registrations'
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customers.id'), primary_key=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)


Customer.courses = db.relationship('Course', secondary='course_registrations', back_populates='students')


class CourseProgram(db.Model):
    __tablename__ = 'course_programs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('programs', lazy=True))


class Homework(db.Model):
    __tablename__ = 'homeworks'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('homeworks', lazy=True))


class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('customers.id'), nullable=False)
    file_path = db.Column(db.String(255))
    grade = db.Column(db.Integer)
    comments = db.Column(db.Text)
    reviewer_name = db.Column(db.String(255), nullable=False)  # ID преподавателя
    homework = db.relationship('Homework', backref=db.backref('submissions', lazy=True))
    student = db.relationship('Customer', foreign_keys=[student_id], backref=db.backref('submissions', lazy=True))


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, index=True, autoincrement=True, unique=True)
    telegram_id: int = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    balance_amount = db.Column(db.Float, nullable=False, default=0)
    used_tokens = db.Column(db.Integer, nullable=False, default=0)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(50), nullable=False, default='inactive')


class NeuropunkPro(db.Model):
    __tablename__ = "neuropunk_pro"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=True)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(50), nullable=False, default='inactive')


class Config(db.Model):
    __tablename__ = 'config'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)


class Zoom(db.Model):
    __tablename__ = "zoom"
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=True)


class Achievement(db.Model):
    __tablename__ = 'achievements'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    criteria = db.relationship('AchievementCriteria', backref='achievement', lazy=True)


class AchievementCriteria(db.Model):
    __tablename__ = 'achievement_criteria'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    criteria_type = db.Column(db.String(50), nullable=False)  # Например, 'average_grade', 'courses_completed'
    threshold = db.Column(db.Float, nullable=False)  # Порог для достижения


class Purchase(db.Model):
    __tablename__ = 'purchases'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    item_name = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    card_image_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.BigInteger)
    is_purchased = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Purchase {self.item_name}>'


class GlobalBalance(db.Model):
    __tablename__ = 'global_balance'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(Numeric(20, 4), default=0)
    interesting_fact = db.Column(db.Text, nullable=True)

    @staticmethod
    def get_balance():
        balance_record = GlobalBalance.query.first()
        if not balance_record:
            balance_record = GlobalBalance(balance=0)
            db.session.add(balance_record)
            db.session.commit()
        return float(balance_record.balance), balance_record.interesting_fact

    @staticmethod
    def update_balance(amount):
        balance_record = GlobalBalance.query.first()
        if not balance_record:
            balance_record = GlobalBalance(balance=amount)
        else:
            balance_record.balance += amount
        db.session.commit()
