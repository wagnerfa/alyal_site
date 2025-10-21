from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

ROLE_GESTOR = 'gestor'
ROLE_ANALISTA = 'analista'
ROLE_CLIENTE = 'cliente'
ROLE_CHOICES = {ROLE_GESTOR, ROLE_ANALISTA, ROLE_CLIENTE}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default=ROLE_CLIENTE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    companies_created = db.relationship(
        'Company',
        back_populates='created_by',
        lazy='dynamic',
        foreign_keys='Company.created_by_id'
    )

    company_memberships = db.relationship(
        'CompanyClient',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_manager(self):
        return self.role in {ROLE_GESTOR, ROLE_ANALISTA}

    def set_role(self, role):
        if role not in ROLE_CHOICES:
            raise ValueError('Invalid role')
        self.role = role

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
