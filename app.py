import flask_admin as admin
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from api.api import api
from core.admin.admin_panel import MyAdminIndexView, MyModelView, HomeworkReviewView
from core.mod.mod_panel import ModeratorView, MyModIndexView
from core.portal import views
from database.models import db, Course, Customer, Broadcast, Homework, CourseProgram, HomeworkSubmission
from tools.auth import login_manager
from tools.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'views.login'
jwt = JWTManager(app)
app.register_blueprint(views)
app.register_blueprint(api, url_prefix='/api')
admins = admin.Admin(name='Админ Панель. Нейропанк Академия', index_view=MyAdminIndexView(), base_template='admin/master.html', template_mode='bootstrap4', url='/admin')
admins.add_view(HomeworkReviewView(name='Проверка Домашек', endpoint='homeworkreview'))
admins.add_view(MyModelView(Course, db.session, category="Таблицы", name="Курсы"))
admins.add_view(MyModelView(Customer, db.session, category="Таблицы", name="Пользователи"))
admins.add_view(MyModelView(Broadcast, db.session, category="Таблицы", name="Трансляции"))
admins.add_view(MyModelView(Homework, db.session, category="Таблицы", name="Домашки"))
admins.add_view(MyModelView(CourseProgram, db.session, category="Таблицы", name="Программа курсов"))
admins.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworksubmissionview"))

moderator = admin.Admin(name='Панель Модератора', base_template='mod/master.html', template_mode='bootstrap4', url='/moderator', endpoint='moderator', index_view=MyModIndexView())

moderator.add_view(ModeratorView(name='Управление Физкоином', endpoint='mod_coin'))
moderator.add_view(MyModelView(HomeworkSubmission, db.session, category="Таблицы", name="проверки домашек", endpoint="homeworkmodview"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
