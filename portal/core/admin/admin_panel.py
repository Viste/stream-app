from collections import defaultdict

from database.models import db, Course, Customer, Broadcast, Homework, CourseProgram, HomeworkSubmission
from flask import request, redirect, url_for, session
from flask_admin import Admin, expose, AdminIndexView, BaseView, helpers
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import joinedload
from tools.forms import LoginForm


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
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


class HomeworkReviewView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        submissions = HomeworkSubmission.query.options(
            joinedload(HomeworkSubmission.homework).joinedload(Homework.course),
            joinedload(HomeworkSubmission.student)
        ).all()

        # Группировка по названию курса
        courses_dict = defaultdict(list)
        for submission in submissions:
            courses_dict[submission.homework.course.name].append(submission)

        return self.render('admin/homework_review.html', courses_dict=courses_dict)


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = Admin(name='Админ Панель. Нейропанк Академия', index_view=MyAdminIndexView(), base_template='admin/my_master.html', template_mode='bootstrap4', url='/admin')

admin.add_view(HomeworkReviewView(name='Проверка Домашек', endpoint='homeworkreview'))

admin.add_view(MyModelView(Course, db.session, category="Таблицы", name="Курсы"))
admin.add_view(MyModelView(Customer, db.session, category="Таблицы", name="Пользователи"))
admin.add_view(MyModelView(Broadcast, db.session, category="Таблицы", name="Трансляции"))
admin.add_view(MyModelView(Homework, db.session, category="Таблицы", name="Домашки"))
admin.add_view(MyModelView(CourseProgram, db.session, category="Таблицы", name="Программа курсов"))
admin.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworksubmissionview"))
