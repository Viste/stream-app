from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from api.api import api
from core.admin.admin_panel import admins, MyAdminIndexView
from core.mod.mod_panel import moderator, MyModIndexView
from core.portal import views
from database.models import db
from tools.auth import login_manager
from tools.config import Config
from tools.utils import number_format, markdown_format

app = Flask(__name__)
talisman = Talisman(app, content_security_policy=None)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
# csrf = SeaSurf(app)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = 'views.login'

jwt = JWTManager(app)

app.template_filter('number_format')(number_format)
app.template_filter('markdown_format')(markdown_format)

app.register_blueprint(views)
app.register_blueprint(api, url_prefix='/api')

moderator.init_app(app, endpoint='moderator', index_view=MyModIndexView(endpoint='moderator', url='/moderator', template='mod/index.html'))
admins.init_app(app, index_view=MyAdminIndexView(endpoint='admin', url='/admin', template='admin/index.html'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
