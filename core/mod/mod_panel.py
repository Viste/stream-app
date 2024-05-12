from collections import defaultdict

import flask_admin as moderator
from flask import request, redirect, url_for, session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import joinedload

from database.models import db, Purchase, GlobalBalance, HomeworkSubmission, Homework
from tools.forms import ModLoginForm


class MyModIndexView(moderator.AdminIndexView):
    @moderator.expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('moderator.login_view'))
        return super(MyModIndexView(), self).index()

    @moderator.expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = ModLoginForm(request.form)
        if moderator.helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('moderator.index'))
        self._template_args['form'] = form
        return super(MyModIndexView, self).render('mod/login.html')

    @moderator.expose('/logout/')
    def logout_view(self):
        logout_user()
        session.clear()
        return redirect(url_for('moderator.login_view'))


class ModeratorView(moderator.BaseView):
    @moderator.expose('/')
    @login_required
    def index(self):
        if not current_user.is_moderator:
            return redirect(url_for('.index'))
        balance = GlobalBalance.get_balance()
        return self.render('mod/moderator_dashboard.html', balance=balance)

    @moderator.expose('/update_balance', methods=['POST'])
    @login_required
    def update_balance(self):
        if not current_user.is_moderator:
            return redirect(url_for('mod.index'))
        amount = float(request.form['amount'])
        GlobalBalance.update_balance(amount)
        return redirect(url_for('.index'))

    @moderator.expose('/add_purchase', methods=['POST'])
    @login_required
    def add_purchase(self):
        if not current_user.is_moderator:
            return redirect(url_for('index'))
        user_id = request.form['user_id']
        item_name = request.form['item_name']
        download_url = request.form['download_url']
        purchase = Purchase(user_id=user_id, item_name=item_name, download_url=download_url)
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for('.index'))


class HomeworkReviewView(moderator.BaseView):
    @moderator.expose('/')
    @login_required
    def index(self):
        submissions = HomeworkSubmission.query.options(
            joinedload(HomeworkSubmission.homework).joinedload(Homework.course),
            joinedload(HomeworkSubmission.student)
        ).all()

        courses_dict = defaultdict(list)
        for submission in submissions:
            courses_dict[submission.homework.course.name].append(submission)

        return self.render('mod/homework_review.html', courses_dict=courses_dict)

    @moderator.expose('/grade/<int:submission_id>/', methods=['POST'])
    @login_required
    def homeworkreview_grade(self, submission_id):
        submission = HomeworkSubmission.query.get(submission_id)
        submission.grade = request.form['grade']
        submission.reviewer_name = current_user.username
        db.session.commit()
        return redirect(url_for('.index'))

    @moderator.expose('/comment/<int:submission_id>/', methods=['POST'])
    @login_required
    def homeworkreview_comment(self, submission_id):
        submission = HomeworkSubmission.query.get(submission_id)
        submission.comments = request.form['comments']
        submission.reviewer_name = current_user.username
        db.session.commit()
        return redirect(url_for('.index'))


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


moderator = moderator.Admin(name='Панель Модератора. Нейропанк Академия', base_template='mod/master.html', template_mode='bootstrap4')

moderator.add_view(ModeratorView(name='Управление Физкоином', endpoint='mod_coin'))
moderator.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworkmodview"))
