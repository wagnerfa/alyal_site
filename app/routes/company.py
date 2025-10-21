from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user

from app import db
from app.models.company import Company, CompanyClient
from app.models.user import ROLE_CLIENTE, User

bp = Blueprint('companies', __name__, url_prefix='/companies')


def _ensure_manager():
    if not current_user.is_authenticated or not current_user.is_manager:
        abort(403)


@bp.route('/', methods=['GET'])
@login_required
def index():
    _ensure_manager()
    companies = Company.query.filter_by(created_by_id=current_user.id).order_by(Company.created_at.desc()).all()
    return render_template('companies/manage.html', companies=companies)


@bp.route('/', methods=['POST'])
@login_required
def create_company():
    _ensure_manager()

    data = request.get_json() if request.is_json else request.form
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        return jsonify({'success': False, 'message': 'Informe o nome da empresa.'}), 400

    if Company.query.filter(db.func.lower(Company.name) == name.lower()).first():
        return jsonify({'success': False, 'message': 'Já existe uma empresa com esse nome.'}), 400

    company = Company(name=name, description=description, created_by=current_user)
    db.session.add(company)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Empresa cadastrada com sucesso!',
        'company': {
            'id': company.id,
            'name': company.name,
            'description': company.description,
            'created_at': company.created_at.isoformat(),
        },
    })


@bp.route('/<int:company_id>/clients', methods=['POST'])
@login_required
def add_client(company_id):
    _ensure_manager()

    company = Company.query.filter_by(id=company_id, created_by_id=current_user.id).first()
    if not company:
        abort(404)

    data = request.get_json() if request.is_json else request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not username or not email:
        return jsonify({'success': False, 'message': 'Informe nome e email do cliente.'}), 400

    if '@' not in email:
        return jsonify({'success': False, 'message': 'Email inválido.'}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        if user.role != ROLE_CLIENTE:
            return jsonify({'success': False, 'message': 'Este email pertence a um usuário com outro perfil.'}), 400
    else:
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Defina uma senha temporária com pelo menos 6 caracteres.'}), 400

        user = User(username=username, email=email, role=ROLE_CLIENTE)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    if CompanyClient.query.filter_by(company_id=company.id, user_id=user.id).first():
        return jsonify({'success': False, 'message': 'Cliente já associado a esta empresa.'}), 400

    membership = CompanyClient(company=company, user=user, role=ROLE_CLIENTE)
    db.session.add(membership)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Cliente associado com sucesso!',
        'client': {
            'id': membership.id,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        },
    })


@bp.route('/<int:company_id>/clients/<int:membership_id>', methods=['DELETE'])
@login_required
def remove_client(company_id, membership_id):
    _ensure_manager()

    membership = CompanyClient.query.join(Company).filter(
        Company.id == company_id,
        Company.created_by_id == current_user.id,
        CompanyClient.id == membership_id,
    ).first()

    if not membership:
        abort(404)

    db.session.delete(membership)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Cliente removido da empresa.'})
