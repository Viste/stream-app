from database.models import db, Purchase, GlobalBalance
from flask import request, redirect, url_for
from flask_admin import Admin, expose, BaseView
from flask_login import current_user, login_required


class ModeratorAdminView(BaseView):
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


admin = Admin(name='Админ Панель. Нейропанк Академия', index_view=ModeratorAdminView(), base_template='admin/my_master.html', template_mode='bootstrap4', url='/mod')


admin.add_view(ModeratorAdminView(name='Модераторская панель', endpoint='moderator'))
