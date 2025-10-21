from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from sqlalchemy import func

from app import db
from app.models import Company, CompanyClient, ROLE_CLIENTE

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == ROLE_CLIENTE:
        memberships = CompanyClient.query.filter_by(user_id=current_user.id).all()
        return render_template('main/dashboard_client.html', memberships=memberships)

    company_query = Company.query.filter_by(created_by_id=current_user.id)
    total_companies = company_query.count()

    total_memberships = (
        db.session.query(func.count(CompanyClient.id))
        .join(Company, Company.id == CompanyClient.company_id)
        .filter(Company.created_by_id == current_user.id)
        .scalar()
    ) or 0

    unique_clients = (
        db.session.query(func.count(func.distinct(CompanyClient.user_id)))
        .join(Company, Company.id == CompanyClient.company_id)
        .filter(Company.created_by_id == current_user.id)
        .scalar()
    ) or 0

    latest_companies = company_query.order_by(Company.created_at.desc()).limit(4).all()

    return render_template(
        'main/dashboard_manager.html',
        total_companies=total_companies,
        total_memberships=total_memberships,
        unique_clients=unique_clients,
        latest_companies=latest_companies,
    )
