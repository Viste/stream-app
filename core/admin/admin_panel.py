from collections import defaultdict

import flask_admin as admin
from flask import flash
from flask import request, redirect, url_for, session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import joinedload

from database.models import db, Homework, HomeworkSubmission, Course, Broadcast, Customer, Achievement, AchievementCriteria, CourseProgram, Purchase, GlobalBalance, CourseRegistration
from tools.forms import LoginForm

next_broadcast_title = None


class MyAdminIndexView(admin.AdminIndexView):
    @admin.expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login_view'))
        return super(MyAdminIndexView, self).index()

    @admin.expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).render('admin/login.html')

    @admin.expose('/logout/')
    def logout_view(self):
        logout_user()
        session.clear()
        return redirect(url_for('admin.login_view'))


class HomeworkReviewView(admin.BaseView):
    @admin.expose('/')
    @login_required
    def index(self):
        submissions = HomeworkSubmission.query.options(
            joinedload(HomeworkSubmission.homework).joinedload(Homework.course),
            joinedload(HomeworkSubmission.student)
        ).all()

        courses_dict = defaultdict(list)
        for submission in submissions:
            courses_dict[submission.homework.course.name].append(submission)

        return self.render('admin/homework_review.html', courses_dict=courses_dict)

    @admin.expose('/grade/<int:submission_id>/', methods=['POST'])
    @login_required
    def homeworkreview_grade(self, submission_id):
        submission = HomeworkSubmission.query.get(submission_id)
        submission.grade = request.form['grade']
        submission.reviewer_name = current_user.username
        db.session.commit()
        return redirect(url_for('admin.index'))

    @admin.expose('/comment/<int:submission_id>/', methods=['POST'])
    @login_required
    def homeworkreview_comment(self, submission_id):
        submission = HomeworkSubmission.query.get(submission_id)
        submission.comments = request.form['comments']
        submission.reviewer_name = current_user.username
        db.session.commit()
        return redirect(url_for('admin.index'))


class BroadcastTitleView(admin.BaseView):
    @admin.expose('/', methods=['GET', 'POST'])
    def index(self):
        global next_broadcast_title
        if request.method == 'POST':
            next_broadcast_title = request.form['title']
            return redirect(url_for('admin.index'))
        return self.render('admin/set_broadcast_title.html')


class InterestingFactView(admin.BaseView):
    @admin.expose('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'POST':
            fact = request.form.get('interesting_fact')
            balance_record = GlobalBalance.query.first()
            if not balance_record:
                balance_record = GlobalBalance(interesting_fact=fact)
                db.session.add(balance_record)
            else:
                balance_record.interesting_fact = fact
            db.session.commit()
            return redirect(url_for('admin.index'))
        balance_record = GlobalBalance.query.first()
        return self.render('admin/interesting_fact.html', interesting_fact=balance_record.interesting_fact if balance_record else "")


class CourseSyncView(admin.BaseView):
    @admin.expose('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'POST':
            try:
                self.migrate_available_courses()
                flash('Синхронизация прошла успешно!', 'success')
            except Exception as e:
                flash(f'Ошибка при синхронизации: {str(e)}', 'error')
            return redirect(url_for('coursesync.index'))
        return self.render('admin/course_sync.html')

    @staticmethod
    def migrate_available_courses():
        customers = Customer.query.all()
        courses = {course.short_name: course for course in Course.query.all()}
        for customer in customers:
            if customer.allowed_courses:
                course_short_names = customer.allowed_courses.split(',')
                for short_name in course_short_names:
                    course = courses.get(short_name)
                    if course:
                        registration = CourseRegistration(customer_id=customer.id, course_id=course.id)
                        db.session.add(registration)
        db.session.commit()


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admins = admin.Admin(name='Панель Администратора. Нейропанк Академия', base_template='admin/master.html', template_mode='bootstrap4')

admins.add_view(HomeworkReviewView(name='Проверка Домашек', endpoint='homeworkreview'))
admins.add_view(BroadcastTitleView(name='Установка названия стрима'))
admins.add_view(InterestingFactView(name='Интересный Факт', endpoint='interestingfact'))
admins.add_view(CourseSyncView(name='Синхронизация Курсов', endpoint='coursesync'))
admins.add_view(MyModelView(Course, db.session, category="Таблицы", name="Курсы"))
admins.add_view(MyModelView(Customer, db.session, category="Таблицы", name="Пользователи"))
admins.add_view(MyModelView(Broadcast, db.session, category="Таблицы", name="Трансляции"))
admins.add_view(MyModelView(Homework, db.session, category="Таблицы", name="Домашки"))
admins.add_view(MyModelView(CourseProgram, db.session, category="Таблицы", name="Программа курсов"))
admins.add_view(MyModelView(Achievement, db.session, category="Таблицы", name="Достижения"))
admins.add_view(MyModelView(AchievementCriteria, db.session, category="Таблицы", name="Критерии достижений"))
admins.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworksubmissionview"))
admins.add_view(MyModelView(Purchase, db.session, category="Таблицы", name="Товары за коины"))
admins.add_view(MyModelView(GlobalBalance, db.session, category="Таблицы", name="Баланс коинов"))
admins.add_view(MyModelView(CourseRegistration, db.session, category="Таблицы", name="Доступ к курсам"))
