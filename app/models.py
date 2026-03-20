from datetime import datetime
from flask_login import UserMixin
from .extensions import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    role = db.relationship('Role', back_populates='users')

    @property
    def full_name(self):
        parts = [self.last_name or '', self.first_name or '', self.middle_name or '']
        result = ' '.join(part for part in parts if part).strip()
        return result or self.login

    def __repr__(self):
        return f'<User {self.login}>'