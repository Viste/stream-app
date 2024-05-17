import os
from datetime import timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from database.models import db, Homework, Course, HomeworkSubmission, Broadcast, CourseProgram, Customer, Achievement, AchievementCriteria, Purchase, GlobalBalance
from tools.auth import authenticate_user, logout
from tools.forms import ChangePasswordForm, ChangeEmailForm, EditProfileForm

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
    return render_template('profile/login.html')


@views.route('/logout')
def logout_view():
    logout()
    return redirect(url_for('.login'))


@views.route('/register')
def register():
    return render_template('profile/register.html')


@views.route('/profile')
@login_required
def profile():
    if current_user and not current_user.is_banned:
        user_courses = current_user.courses
        submissions = HomeworkSubmission.query.options(joinedload(HomeworkSubmission.homework).joinedload(Homework.course)).filter_by(student_id=current_user.id).all()
        total_submissions = len(submissions)
        average_grade = sum(sub.grade for sub in submissions if sub.grade is not None) / total_submissions if total_submissions > 0 else 0
        achievements = Achievement.query.join(AchievementCriteria).filter(AchievementCriteria.criteria_type == 'average_grade', AchievementCriteria.threshold <= average_grade).all()
        purchases = Purchase.query.filter_by(is_purchased=True).all()

        return render_template('profile/profile.html', account=current_user, courses=user_courses, submissions=submissions, achievements=achievements, purchases=purchases)
    return redirect(url_for('login'))


@views.route('/public_profile/<int:user_id>')
def public_profile(user_id):
    user = Customer.query.get_or_404(user_id)
    got_courses = Course.query.filter(Course.short_name.in_(user.allowed_courses.split(','))).all()
    submissions = HomeworkSubmission.query.filter_by(student_id=user.id).all()
    total_submissions = len(submissions)
    average_grade = sum(sub.grade for sub in submissions if sub.grade is not None) / total_submissions if total_submissions > 0 else 0
    achievements = Achievement.query.join(AchievementCriteria).filter(AchievementCriteria.criteria_type == 'average_grade', AchievementCriteria.threshold <= average_grade).all()

    return render_template('profile/public_profile.html', user=user, courses=got_courses, total_submissions=total_submissions, average_grade=average_grade, achievements=achievements)


@views.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename != '':
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar_url = url_for('static', filename='storage/' + filename)
        current_user.city = form.city.data
        current_user.headphones = form.headphones.data
        current_user.sound_card = form.sound_card.data
        current_user.pc_setup = form.pc_setup.data
        db.session.commit()
        flash('Профиль успешно обновлен.', 'success')
        return redirect(url_for('views.profile'))
    return render_template('profile/edit_profile.html', form=form, account=current_user)


@views.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if user and user.check_password(form.current_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Ваш пароль был успешно изменен.', 'success')
            return redirect(url_for('views.profile'))
        else:
            flash('Неверный текущий пароль.', 'danger')
    return render_template('profile/change_password.html', form=form)


@views.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        user = current_user
        user.email = form.new_email.data
        db.session.commit()
        flash('Ваш Email был успешно изменен.', 'success')
        return redirect(url_for('views.profile'))
    return render_template('profile/change_email.html', form=form)


@views.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    subscribed_courses = current_user.courses
    subscribed_course_ids = [course.id for course in subscribed_courses]

    live_broadcasts = Broadcast.query.join(Course).filter(
        Broadcast.is_live == True,
        Course.id.in_(subscribed_course_ids)
    ).all()

    print("Live Broadcasts:", live_broadcasts)
    return render_template('course/stream.html', account=current_user, courses=subscribed_courses, live_broadcasts=live_broadcasts)


@views.route('/students')
def students():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    pagination = Customer.query.order_by(Customer.id).paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    user_data = []
    for user in users:
        submissions = HomeworkSubmission.query.filter_by(student_id=user.id).all()
        average_grade = sum(sub.grade for sub in submissions if sub.grade is not None) / len(submissions) if submissions else 0
        user_data.append({'user': user, 'average_grade': average_grade})
    return render_template('profile/students.html', user_data=user_data, pagination=pagination)


@views.route('/howto')
@login_required
def howto():
    return render_template('misc/howto.html', account=current_user)


@views.route('/about')
def about():
    return render_template('misc/about.html')


@views.route('/sport')
@login_required
def sport():
    balance, interesting_fact = GlobalBalance.get_balance()
    products = Purchase.query.all()
    return render_template('misc/sport.html', balance=balance, products=products, interesting_fact=interesting_fact)


@views.route('/buy_product/<int:product_id>')
@login_required
def buy_product(product_id):
    if not current_user.is_moderator:
        return "Доступ запрещен", 403

    product = Purchase.query.get(product_id)
    if product and not product.is_purchased:
        current_balance = GlobalBalance.get_balance()
        if current_balance >= product.price:
            product.is_purchased = True
            GlobalBalance.update_balance(-product.price)
            db.session.commit()
            return redirect(url_for('views.sport'))
        else:
            flash('Недостаточно средств для покупки', 'error')
    return redirect(url_for('views.sport'))


@views.route('/download_product/<int:product_id>')
@login_required
def download_product(product_id):
    product = Purchase.query.get(product_id)
    if product and product.is_purchased:
        directory = os.path.dirname(product.file_path)
        filename = os.path.basename(product.file_path)
        return send_from_directory(directory=directory,
                                   path=filename,
                                   as_attachment=True)
    return "Товар не куплен", 403


@views.route('/courses')
@login_required
def courses():
    allowed_courses = current_user.allowed_courses.split(',')
    course_item = Course.query.filter(Course.short_name.in_(allowed_courses)).all()
    all_courses = Course.query.all()
    return render_template('course/courses.html', courses=course_item, all_courses=all_courses)


@views.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    programs = CourseProgram.query.filter_by(course_id=course.id).all()
    homeworks = Homework.query.filter_by(course_id=course.id).all()
    broadcasts = Broadcast.query.filter_by(course_id=course.id, is_live=False).all()
    identity = {'user_id': current_user.id}
    token = create_access_token(identity=identity, expires_delta=timedelta(hours=1))
    return render_template('course/course_detail.html', course=course, programs=programs, homeworks=homeworks, token=token, broadcasts=broadcasts)


@views.route('/submit_homework/<int:homework_id>', methods=['POST'])
@login_required
def submit_homework(homework_id):
    existing_submissions_count = HomeworkSubmission.query.filter_by(
        homework_id=homework_id,
        student_id=current_user.id
    ).count()

    reviewer_name = "Не назначен"

    if existing_submissions_count >= 2:
        flash('Вы уже загрузили максимальное количество домашних заданий для этой темы.', 'error')
        return redirect(url_for('views.course_detail', course_id=Homework.query.get(homework_id).course_id))

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        db_path = "storage/" + filename
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=current_user.id,
            file_path=db_path,
            reviewer_name=reviewer_name
        )
        db.session.add(submission)
        db.session.commit()
        flash('Домашнее задание успешно отправлено!', 'success')
    else:
        flash('Ошибка загрузки файла. Допустимы только файлы форматов MP3 и WAV.', 'error')

    return redirect(url_for('views.course_detail', course_id=Homework.query.get(homework_id).course_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}
