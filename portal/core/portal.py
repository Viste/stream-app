import os
from datetime import timedelta

from database.models import db, Homework, Course, HomeworkSubmission, Broadcast, CourseProgram
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_required
from tools.auth import authenticate_user, logout
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)


@views.route('/')
def index():
    slider_elements = Course.query.all()
    return render_template('index.html', courses=slider_elements)


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            return redirect(url_for('.index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@views.route('/logout')
def logout_view():
    logout()
    return redirect(url_for('.login'))


@views.route('/register')
def register():
    return render_template('register.html')


@views.route('/profile')
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


@views.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    allowed_course_short_names = current_user.allowed_courses.split(',')
    available_courses = Course.query.filter(Course.short_name.in_(allowed_course_short_names)).all()
    live_broadcasts = Broadcast.query.join(Course).filter(Broadcast.is_live == True, Course.short_name.in_(allowed_course_short_names)).all()
    print("Live Broadcasts:", live_broadcasts)
    return render_template('stream.html', account=current_user, courses=available_courses, live_broadcasts=live_broadcasts)


@views.route('/howto')
@login_required
def howto():
    return render_template('howto.html', account=current_user)


@views.route('/about')
def about():
    return render_template('about.html')


@views.route('/sport')
def sport():
    return render_template('sport.html')


@views.route('/courses')
@login_required
def courses():
    allowed_courses = current_user.allowed_courses.split(',')
    course_item = Course.query.filter(Course.short_name.in_(allowed_courses)).all()
    return render_template('courses.html', courses=course_item)


@views.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    programs = CourseProgram.query.filter_by(course_id=course.id).all()
    homeworks = Homework.query.filter_by(course_id=course.id).all()
    broadcasts = Broadcast.query.filter_by(course_id=course.id, is_live=False).all()
    identity = {'user_id': current_user.id}
    token = create_access_token(identity=identity, expires_delta=timedelta(hours=1))
    return render_template('course_detail.html', course=course, programs=programs, homeworks=homeworks, token=token, broadcasts=broadcasts)


@views.route('/submit_homework/<int:homework_id>', methods=['POST'])
@login_required
def submit_homework(homework_id):
    # Проверяем, сколько уже есть загрузок для данного домашнего задания от этого студента
    existing_submissions_count = HomeworkSubmission.query.filter_by(
        homework_id=homework_id,
        student_id=current_user.id
    ).count()

    # Разрешаем загрузку только если загрузок меньше 2
    if existing_submissions_count >= 2:
        flash('Вы уже загрузили максимальное количество домашних заданий для этой темы.', 'error')
        return redirect(url_for('views.course_detail', course_id=Homework.query.get(homework_id).course_id))

    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        db_path = "storage/" + filename
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=current_user.id,
            file_path=db_path
        )
        db.session.add(submission)
        db.session.commit()
        flash('Домашнее задание успешно отправлено!', 'success')
    else:
        flash('Ошибка загрузки файла.', 'error')

    return redirect(url_for('views.course_detail', course_id=Homework.query.get(homework_id).course_id))
