from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression

db = SQLAlchemy()


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_name = db.Column(db.String(255))
    download_url = db.Column(db.String(255))
    customer = db.relationship('Customer', backref='purchases')

    def __repr__(self):
        return f'<Purchase {self.item_name} by {self.customers.username}>'


class GlobalBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)

    @staticmethod
    def get_balance():
        balance_record = GlobalBalance.query.first()
        if not balance_record:
            balance_record = GlobalBalance(balance=0.0)
            db.session.add(balance_record)
            db.session.commit()
        return balance_record.balance

    @staticmethod
    def update_balance(amount):
        balance_record = GlobalBalance.query.first()
        if not balance_record:
            balance_record = GlobalBalance(balance=amount)
        else:
            balance_record.balance += amount
        db.session.commit()


class Broadcast(db.Model):
    __tablename__ = 'broadcasts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    video_path = db.Column(db.String(255))
    is_live = db.Column(db.Boolean, default=False)
    course = db.relationship('Course', backref=db.backref('broadcasts', lazy=True))
    title = db.Column(db.String(255))
    mariadb_engine = "InnoDB"

    def __repr__(self):
        return f'<Broadcast {self.id} for course {self.course.name}>'


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.BigInteger, primary_key=True, unique=True, autoincrement=True)
    telegram_id = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255))
    allowed_courses = db.Column(db.String(255), nullable=False, default='academy')
    is_moderator = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    is_banned = db.Column(db.Boolean)
    avatar_url = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    headphones = db.Column(db.String(255), nullable=True)
    sound_card = db.Column(db.String(255), nullable=True)
    pc_setup = db.Column(db.String(255), nullable=True)
    mariadb_engine = "InnoDB"

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
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    mariadb_engine = "InnoDB"

    def __repr__(self):
        return f'<Course {self.name}>'


class CourseProgram(db.Model):
    __tablename__ = 'course_programs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('programs', lazy=True))
    mariadb_engine = "InnoDB"


class Homework(db.Model):
    __tablename__ = 'homeworks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.BigInteger, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course = db.relationship('Course', backref=db.backref('homeworks', lazy=True))
    mariadb_engine = "InnoDB"


class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('customers.id'), nullable=False)
    file_path = db.Column(db.String(255))
    grade = db.Column(db.Integer)
    comments = db.Column(db.Text)
    reviewer_name = db.Column(db.String(255), nullable=False)  # ID преподавателя
    homework = db.relationship('Homework', backref=db.backref('submissions', lazy=True))
    student = db.relationship('Customer', foreign_keys=[student_id], backref=db.backref('submissions', lazy=True))
    mariadb_engine = "InnoDB"


class Calendar(db.Model):
    __tablename__ = "calendar"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    end_time = db.Column(db.TIMESTAMP, nullable=False)
    mariadb_engine = "InnoDB"


class StreamEmails(db.Model):
    __tablename__ = "stream_emails"

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    stream_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=False)
    mariadb_engine = "InnoDB"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, index=True, autoincrement=True, unique=True)
    telegram_id: int = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    balance_amount = db.Column(db.Float, nullable=False, default=0)
    used_tokens = db.Column(db.Integer, nullable=False, default=0)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(50), nullable=False, default='inactive')
    mariadb_engine = "InnoDB"


class NeuropunkPro(db.Model):
    __tablename__ = "neuropunk_pro"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=True)
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(50), nullable=False, default='inactive')
    mariadb_engine = "InnoDB"


class ChatMember(db.Model):
    __tablename__ = "chat_members"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, nullable=False)
    telegram_username = db.Column(db.String(255), nullable=True)
    chat_name = db.Column(db.String(255), nullable=False)
    chat_id = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')
    banned = db.Column(db.Boolean, default=False, server_default=expression.false())
    mariadb_engine = "InnoDB"


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    mariadb_engine = "InnoDB"


class Zoom(db.Model):
    __tablename__ = "zoom"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger, nullable=False, unique=True)
    telegram_username = db.Column(db.String(255), nullable=True, unique=True)
    email = db.Column(db.String(255), nullable=True)
    mariadb_engine = "InnoDB"


class Admins(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    telegram_id: int = db.Column(db.BigInteger, nullable=False, unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    mariadb_engine = "InnoDB"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.is_admin

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    criteria = db.relationship('AchievementCriteria', backref='achievement', lazy=True)
    mariadb_engine = "InnoDB"


class AchievementCriteria(db.Model):
    __tablename__ = 'achievement_criteria'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    criteria_type = db.Column(db.String(50), nullable=False)  # Например, 'average_grade', 'courses_completed'
    threshold = db.Column(db.Float, nullable=False)  # Порог для достижения
    mariadb_engine = "InnoDB"
