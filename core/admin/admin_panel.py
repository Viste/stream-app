from collections import defaultdict

import flask_admin as admin
from flask import request, redirect, url_for, session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import joinedload

from database.models import db, Homework, HomeworkSubmission, Course, Broadcast, Customer, Achievement, AchievementCriteria, CourseProgram, Purchase, GlobalBalance
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


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admins = admin.Admin(name='Панель Администратора. Нейропанк Академия', base_template='admin/master.html', template_mode='bootstrap4')

admins.add_view(HomeworkReviewView(name='Проверка Домашек', endpoint='homeworkreview'))
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
