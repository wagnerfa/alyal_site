from datetime import datetime
from datetime import datetime

from app import db


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logo_path = db.Column(db.String(255))

    created_by = db.relationship('User', back_populates='companies_created')
    clients = db.relationship(
        'CompanyClient',
        back_populates='company',
        cascade='all, delete-orphan',
        order_by='CompanyClient.invited_at.desc()'
    )

    def __repr__(self):
        return f'<Company {self.name}>'


class CompanyClient(db.Model):
    __tablename__ = 'company_client'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cliente')
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='clients')
    user = db.relationship('User', back_populates='company_memberships')

    __table_args__ = (
        db.UniqueConstraint('company_id', 'user_id', name='uq_company_client_user'),
    )

    def __repr__(self):
        return f'<CompanyClient company_id={self.company_id} user_id={self.user_id}>'
