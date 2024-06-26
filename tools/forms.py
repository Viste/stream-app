from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms import validators, fields, form
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from database.models import db, Customer


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


class ModLoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Вы не зарегистрированы')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Неправильный Пароль')

        if user.is_moderator is False:
            raise validators.ValidationError('Вы не модератор')

    def get_user(self):
        return db.session.query(Customer).filter_by(username=self.login.data).first()


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Сменить пароль')


class ChangeEmailForm(FlaskForm):
    new_email = StringField('Новый Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Сменить Email')


class EditProfileForm(FlaskForm):
    avatar = FileField('Аватар', validators=[Optional()])
    city = StringField('Город', validators=[Optional()])
    headphones = StringField('Наушники', validators=[Optional()])
    sound_card = StringField('Звуковая карта', validators=[Optional()])
    pc_setup = StringField('Сэтап ПК', validators=[Optional()])
    submit = SubmitField('Сохранить изменения')
