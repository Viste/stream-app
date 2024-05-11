from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from api.api import api
from core.admin.admin_panel import admin
from core.mod.mod_panel import mod
from core.portal import views
from database.models import db
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
admin.init_app(app)
mod.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
