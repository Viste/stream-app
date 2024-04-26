from database.models import db, Customer
from werkzeug.security import check_password_hash
from wtforms import validators, fields, form


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Вы не зарегистрированы')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Неправильный Пароль')

        if user.is_admin is False:
            raise validators.ValidationError('Вы не администратор')

        if user.is_moderator is False:
            raise validators.ValidationError('Вы не модератор')

    def get_user(self):
        return db.session.query(Customer).filter_by(username=self.login.data).first()
