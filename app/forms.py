import re
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Optional


LOGIN_RE = re.compile(r'^[A-Za-z0-9]{5,}$')
ALLOWED_PASSWORD_RE = re.compile(
    r'^[A-Za-zА-Яа-яЁё0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'.,:;]+$'
)
HAS_UPPER_RE = re.compile(r'[A-ZА-ЯЁ]')
HAS_LOWER_RE = re.compile(r'[a-zа-яё]')
HAS_DIGIT_RE = re.compile(r'[0-9]')


def validate_login_value(value):
    errors = []

    if not value or not value.strip():
        errors.append('Поле не может быть пустым.')
        return errors

    if not LOGIN_RE.fullmatch(value):
        errors.append(
            'Логин должен содержать только латинские буквы и цифры и иметь длину не менее 5 символов.'
        )

    return errors


def validate_password_value(value):
    errors = []

    if not value:
        errors.append('Поле не может быть пустым.')
        return errors

    if len(value) < 8:
        errors.append('Пароль должен содержать не менее 8 символов.')

    if len(value) > 128:
        errors.append('Пароль должен содержать не более 128 символов.')

    if ' ' in value:
        errors.append('Пароль не должен содержать пробелы.')

    if not HAS_UPPER_RE.search(value):
        errors.append('Пароль должен содержать хотя бы одну заглавную букву.')

    if not HAS_LOWER_RE.search(value):
        errors.append('Пароль должен содержать хотя бы одну строчную букву.')

    if not HAS_DIGIT_RE.search(value):
        errors.append('Пароль должен содержать хотя бы одну цифру.')

    if not ALLOWED_PASSWORD_RE.fullmatch(value):
        errors.append('Пароль содержит недопустимые символы.')

    return errors


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(message='Введите логин.')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Введите пароль.')])
    submit = SubmitField('Войти')


class UserCreateForm(FlaskForm):
    login = StringField('Логин', validators=[Optional()])
    password = PasswordField('Пароль', validators=[Optional()])
    last_name = StringField('Фамилия', validators=[Optional()])
    first_name = StringField('Имя', validators=[Optional()])
    middle_name = StringField('Отчество', validators=[Optional()])
    role_id = SelectField('Роль', coerce=int, validators=[Optional()])
    submit = SubmitField('Сохранить')

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)

        self.login.errors.extend(validate_login_value(self.login.data))
        self.password.errors.extend(validate_password_value(self.password.data))

        if not self.last_name.data or not self.last_name.data.strip():
            self.last_name.errors.append('Поле не может быть пустым.')

        if not self.first_name.data or not self.first_name.data.strip():
            self.first_name.errors.append('Поле не может быть пустым.')

        return valid and not any([
            self.login.errors,
            self.password.errors,
            self.last_name.errors,
            self.first_name.errors,
        ])


class UserEditForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[Optional()])
    first_name = StringField('Имя', validators=[Optional()])
    middle_name = StringField('Отчество', validators=[Optional()])
    role_id = SelectField('Роль', coerce=int, validators=[Optional()])
    submit = SubmitField('Сохранить')

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)

        if not self.last_name.data or not self.last_name.data.strip():
            self.last_name.errors.append('Поле не может быть пустым.')

        if not self.first_name.data or not self.first_name.data.strip():
            self.first_name.errors.append('Поле не может быть пустым.')

        return valid and not any([
            self.last_name.errors,
            self.first_name.errors,
        ])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired(message='Введите старый пароль.')])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(message='Введите новый пароль.')])
    confirm_new_password = PasswordField(
        'Повторите новый пароль',
        validators=[
            DataRequired(message='Повторите новый пароль.'),
            EqualTo('new_password', message='Новые пароли не совпадают.'),
        ]
    )
    submit = SubmitField('Сменить пароль')

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)
        self.new_password.errors.extend(validate_password_value(self.new_password.data))
        return valid and not self.new_password.errors