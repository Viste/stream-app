from database.models import db, Purchase, GlobalBalance
from flask import request, redirect, url_for, session
from flask_admin import expose, AdminIndexView, BaseView, helpers, Admin
from flask_login import login_user, logout_user, current_user, login_required
from tools.forms import ModLoginForm


class MyModIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyModIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = ModLoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyModIndexView, self).render('admin/login.html')

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        session.clear()
        return redirect(url_for('.login_view'))


class ModeratorView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_moderator:
            return redirect(url_for('index'))
        balance = GlobalBalance.get_balance()
        return self.render('admin/moderator_dashboard.html', balance=balance)

    @expose('/update_balance', methods=['POST'])
    @login_required
    def update_balance(self):
        if not current_user.is_moderator:
            return redirect(url_for('index'))
        amount = float(request.form['amount'])
        GlobalBalance.update_balance(amount)
        return redirect(url_for('.index'))

    @expose('/add_purchase', methods=['POST'])
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


mod = Admin(name='Модераторская Нейропанк Академия', index_view=MyModIndexView(), base_template='admin/my_master.html', template_mode='bootstrap4', url='/mod', endpoint='mod')


mod.add_view(ModeratorView(name='Управление Физкоином', endpoint='moderator'))
