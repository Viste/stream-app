from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
