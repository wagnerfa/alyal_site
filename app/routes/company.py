import os
import uuid

from flask import Blueprint, render_template, request, jsonify, abort, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.company import Company, CompanyClient
from app.models.user import ROLE_ANALISTA, ROLE_CLIENTE, User

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

    data = request.get_json(silent=True) if request.is_json else request.form
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()
    logo_file = request.files.get('logo') if not request.is_json else None

    if not name:
        return jsonify({'success': False, 'message': 'Informe o nome da empresa.'}), 400

    if Company.query.filter(db.func.lower(Company.name) == name.lower()).first():
        return jsonify({'success': False, 'message': 'Já existe uma empresa com esse nome.'}), 400

    company = Company(name=name, description=description, created_by=current_user)

    if logo_file and logo_file.filename:
        try:
            company.logo_path = _store_logo_file(logo_file)
        except ValueError as exc:
            return jsonify({'success': False, 'message': str(exc)}), 400

    db.session.add(company)
    db.session.commit()

    logo_url = url_for('static', filename=company.logo_path) if company.logo_path else None

    return jsonify({
        'success': True,
        'message': 'Empresa cadastrada com sucesso!',
        'company': {
            'id': company.id,
            'name': company.name,
            'description': company.description,
            'created_at': company.created_at.isoformat(),
            'logo_url': logo_url,
        },
    })


@bp.route('/<int:company_id>/clients', methods=['POST'])
@login_required
def add_client(company_id):
    _ensure_manager()

    company = Company.query.filter_by(id=company_id, created_by_id=current_user.id).first()
    if not company:
        abort(404)

    data = request.get_json(silent=True) if request.is_json else request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role = (data.get('role') or ROLE_CLIENTE).strip().lower()

    if not username or not email:
        return jsonify({'success': False, 'message': 'Informe nome e email do cliente.'}), 400

    if '@' not in email:
        return jsonify({'success': False, 'message': 'Email inválido.'}), 400

    if role not in {ROLE_CLIENTE, ROLE_ANALISTA}:
        return jsonify({'success': False, 'message': 'Perfil selecionado é inválido.'}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        if user.role != role:
            return jsonify({'success': False, 'message': 'Este email pertence a um usuário com outro perfil.'}), 400
    else:
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Defina uma senha temporária com pelo menos 6 caracteres.'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Nome de usuário já utilizado. Escolha outro nome.'}), 400

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    if CompanyClient.query.filter_by(company_id=company.id, user_id=user.id).first():
        return jsonify({'success': False, 'message': 'Cliente já associado a esta empresa.'}), 400

    membership = CompanyClient(company=company, user=user, role=role)
    db.session.add(membership)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Cliente associado com sucesso!',
        'client': {
            'membership_id': membership.id,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': membership.role,
            'invited_at': membership.invited_at.isoformat(),
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


@bp.route('/<int:company_id>/logo', methods=['POST'])
@login_required
def update_logo(company_id):
    _ensure_manager()

    company = Company.query.filter_by(id=company_id, created_by_id=current_user.id).first()
    if not company:
        abort(404)

    logo_file = request.files.get('logo')
    if not logo_file or not logo_file.filename:
        return jsonify({'success': False, 'message': 'Envie um arquivo de imagem válido.'}), 400

    try:
        new_logo_path = _store_logo_file(logo_file, current_path=company.logo_path)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400

    company.logo_path = new_logo_path
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Logotipo atualizado com sucesso!',
        'logo_url': url_for('static', filename=company.logo_path),
    })


def _store_logo_file(file_storage, current_path=None):
    filename = secure_filename(file_storage.filename or '')
    if not filename:
        raise ValueError('Arquivo de imagem inválido.')

    if '.' not in filename:
        raise ValueError('Arquivo de imagem inválido.')

    extension = filename.rsplit('.', 1)[-1].lower()
    allowed = current_app.config.get('ALLOWED_LOGO_EXTENSIONS', set())
    if extension not in allowed:
        raise ValueError('Formato de imagem não suportado.')

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    full_path = os.path.join(upload_folder, unique_name)
    file_storage.save(full_path)

    if current_path:
        _remove_logo_file(current_path)

    relative_path = os.path.relpath(full_path, current_app.static_folder)
    return relative_path


def _remove_logo_file(relative_path):
    if not relative_path:
        return

    absolute_path = os.path.join(current_app.static_folder, relative_path)
    if os.path.exists(absolute_path):
        try:
            os.remove(absolute_path)
        except OSError:
            pass
