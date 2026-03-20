from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .forms import ChangePasswordForm, LoginForm, UserCreateForm, UserEditForm
from .models import Role, User


def register_routes(app):
    @app.context_processor
    def inject_now():
        return {'current_user': current_user}

    @app.route('/')
    def index():
        users = User.query.outerjoin(Role).order_by(User.id).all()
        return render_template('index.html', users=users)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(login=form.login.data.strip()).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Вы успешно вошли в систему.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))

            flash('Неверный логин или пароль.', 'danger')

        return render_template('login.html', form=form)

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        flash('Вы вышли из системы.', 'info')
        return redirect(url_for('index'))

    @app.route('/users/<int:user_id>')
    def view_user(user_id):
        user = User.query.get_or_404(user_id)
        return render_template('user_view.html', user=user)

    @app.route('/users/create', methods=['GET', 'POST'])
    @login_required
    def create_user():
        form = UserCreateForm()
        populate_role_choices(form)

        if form.validate_on_submit():
            try:
                user = User(
                    login=form.login.data.strip(),
                    password_hash=generate_password_hash(form.password.data),
                    last_name=form.last_name.data.strip(),
                    first_name=form.first_name.data.strip(),
                    middle_name=(form.middle_name.data or '').strip() or None,
                    role_id=form.role_id.data or None,
                )
                db.session.add(user)
                db.session.commit()
                flash('Пользователь успешно создан.', 'success')
                return redirect(url_for('index'))

            except IntegrityError:
                db.session.rollback()
                form.login.errors.append('Пользователь с таким логином уже существует.')
                flash('Не удалось создать пользователя. Исправьте ошибки в форме.', 'danger')

            except Exception:
                db.session.rollback()
                flash('При сохранении пользователя произошла ошибка.', 'danger')

        elif request.method == 'POST':
            flash('Исправьте ошибки в форме.', 'danger')

        return render_template(
            'user_form_page.html',
            form=form,
            title='Создание пользователя',
            is_edit=False
        )

    @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        form = UserEditForm(obj=user)
        populate_role_choices(form)

        if request.method == 'GET':
            form.role_id.data = user.role_id or 0

        if form.validate_on_submit():
            try:
                user.last_name = form.last_name.data.strip()
                user.first_name = form.first_name.data.strip()
                user.middle_name = (form.middle_name.data or '').strip() or None
                user.role_id = form.role_id.data or None

                db.session.commit()
                flash('Пользователь успешно изменён.', 'success')
                return redirect(url_for('index'))

            except Exception:
                db.session.rollback()
                flash('При изменении пользователя произошла ошибка.', 'danger')

        elif request.method == 'POST':
            flash('Исправьте ошибки в форме.', 'danger')

        return render_template(
            'user_form_page.html',
            form=form,
            title='Редактирование пользователя',
            is_edit=True,
            user=user
        )

    @app.route('/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'Пользователь "{user.full_name}" удалён.', 'success')

        except Exception:
            db.session.rollback()
            flash('Не удалось удалить пользователя.', 'danger')

        return redirect(url_for('index'))

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        form = ChangePasswordForm()

        if form.validate_on_submit():
            if not check_password_hash(current_user.password_hash, form.old_password.data):
                form.old_password.errors.append('Старый пароль введён неверно.')
                flash('Не удалось сменить пароль. Проверьте введённые данные.', 'danger')
                return render_template('change_password.html', form=form)

            try:
                current_user.password_hash = generate_password_hash(form.new_password.data)
                db.session.commit()
                flash('Пароль успешно изменён.', 'success')
                return redirect(url_for('index'))

            except Exception:
                db.session.rollback()
                flash('При смене пароля произошла ошибка.', 'danger')

        elif request.method == 'POST':
            flash('Не удалось сменить пароль. Проверьте введённые данные.', 'danger')

        return render_template('change_password.html', form=form)


def populate_role_choices(form):
    roles = Role.query.order_by(Role.name).all()
    form.role_id.choices = [(0, 'Без роли')] + [(role.id, role.name) for role in roles]