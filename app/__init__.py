from flask import Flask
from .extensions import db, login_manager
from .models import User, Role
from .routes import register_routes
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Сначала войдите в систему.'
    login_manager.login_message_category = 'warning'

    register_routes(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    from werkzeug.security import generate_password_hash

    if Role.query.count() == 0:
        roles = [
            Role(name='Администратор', description='Полный доступ к системе'),
            Role(name='Менеджер', description='Работа с учётными записями пользователей'),
            Role(name='Пользователь', description='Обычный пользователь системы'),
        ]
        db.session.add_all(roles)
        db.session.commit()

    if User.query.filter_by(login='admin01').first() is None:
        admin_role = Role.query.filter_by(name='Администратор').first()
        admin = User(
            login='admin01',
            password_hash=generate_password_hash('Admin123!'),
            last_name='Иванов',
            first_name='Админ',
            middle_name='Системный',
            role_id=admin_role.id if admin_role else None,
        )
        db.session.add(admin)
        db.session.commit()