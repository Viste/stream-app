import os
from collections import defaultdict
from decimal import Decimal, InvalidOperation

import flask_admin as moderator
from flask import request, redirect, url_for, session, current_app, send_from_directory, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from database.models import db, Purchase, GlobalBalance, HomeworkSubmission, Homework
from tools.forms import ModLoginForm


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'rar', 'zip', '7z'}


class MyModIndexView(moderator.AdminIndexView):
    @moderator.expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('moderator.login_view'))
        return super(MyModIndexView, self).index()

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
        balance = GlobalBalance.get_balance()
        products = Purchase.query.all()
        return self.render('mod/moderator_dashboard.html', balance=balance, products=products)

    @moderator.expose('/update_balance', methods=['POST'])
    @login_required
    def update_balance(self):
        try:
            amount = Decimal(request.form['amount'])
            action = request.form['action']
            if action == 'decrease':
                amount = -amount
            GlobalBalance.update_balance(amount)
        except InvalidOperation:
            flash('Некорректное значение. Пожалуйста, введите число с точностью до четырех знаков после запятой.', 'error')
            return redirect(url_for('moderatorview.index'))  # предполагается, что есть такой endpoint
        return redirect(url_for('moderator.index'))

    @moderator.expose('/buy_product/<int:product_id>/')
    @login_required
    def buy_product(self, product_id):
        product = Purchase.query.get(product_id)
        if product and not product.is_purchased:
            current_balance, interesting_fact = GlobalBalance.get_balance()
            if current_balance >= product.price:
                product.is_purchased = True
                GlobalBalance.update_balance(-product.price)
                db.session.commit()
        return redirect(url_for('moderator.index'))

    @moderator.expose('/download_product/<int:product_id>/')
    @login_required
    def download_product(self, product_id):
        product = Purchase.query.get(product_id)
        if product.is_purchased:
            directory = os.path.dirname(product.file_path)
            filename = os.path.basename(product.file_path)
            return send_from_directory(directory=directory,
                                       path=filename,
                                       as_attachment=True)
        return "Товар не куплен", 403


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
        return redirect(url_for('moderator.index'))

    @moderator.expose('/comment/<int:submission_id>/', methods=['POST'])
    @login_required
    def homeworkreview_comment(self, submission_id):
        submission = HomeworkSubmission.query.get(submission_id)
        submission.comments = request.form['comments']
        submission.reviewer_name = current_user.username
        db.session.commit()
        return redirect(url_for('moderator.index'))


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class ProductUploadView(moderator.BaseView):
    @moderator.expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        if request.method == 'POST':
            file = request.files['file']
            card_image = request.files['card_image']
            name = request.form['name']
            description = request.form['description']
            price = int(request.form['price'])
            if file and card_image:
                filename = secure_filename(file.filename)
                card_image_filename = secure_filename(card_image.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                card_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], card_image_filename)
                file.save(file_path)
                card_image.save(card_image_path)
                new_product = Purchase(item_name=name, file_path=file_path, card_image_path=card_image_path, description=description, price=price)
                db.session.add(new_product)
                db.session.commit()
                return self.render('admin/message.html', message="Товар успешно загружен")
        return self.render('mod/upload_product.html')


class ProductEditView(moderator.BaseView):
    @moderator.expose('/')
    @login_required
    def index(self):
        products = Purchase.query.all()
        return self.render('mod/edit_products.html', products=products)

    @moderator.expose('/edit/<int:product_id>/', methods=['GET', 'POST'])
    @login_required
    def edit_product(self, product_id):
        product = Purchase.query.get_or_404(product_id)
        if request.method == 'POST':
            product.item_name = request.form['name']
            product.description = request.form['description']
            product.price = int(request.form['price'])

            file = request.files.get('file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                product.file_path = file_path

            card_image = request.files.get('card_image')
            if card_image and allowed_file(card_image.filename):
                card_image_filename = secure_filename(card_image.filename)
                card_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], card_image_filename)
                card_image.save(card_image_path)
                product.card_image_path = card_image_path

            db.session.commit()
            flash('Товар успешно обновлен', 'success')
            return redirect(url_for('product_edit.index'))
        return self.render('mod/product_form.html', product=product)


moderator = moderator.Admin(name='Панель Модератора. Нейропанк Академия', base_template='mod/master.html', template_mode='bootstrap4')

moderator.add_view(ModeratorView(name='Управление Физкоином'))
moderator.add_view(ProductUploadView(name='Загрузка товара', endpoint='product_upload'))
moderator.add_view(ProductEditView(name='Редактирование товара', endpoint='product_edit'))
moderator.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworkmodview"))
