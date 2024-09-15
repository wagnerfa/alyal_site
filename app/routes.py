from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from app import db, mail
from app.models import Usuario, PreInscricao, Lembrete
from app.utils import envio_email
import random
import string
from functools import wraps
from datetime import datetime
import datetime



main = Blueprint('main', __name__)

def gerar_matricula():
    return ''.join(random.choices(string.digits, k=6))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso não autorizado.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function

def gerar_matricula_unico():
    while True:
        nova_matricula = ''.join(random.choices(string.digits, k=6))
        usuario_existente = Usuario.query.filter_by(matricula=nova_matricula).first()
        if not usuario_existente:
            return nova_matricula

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        treinamento = request.form.get('treinamento')
        pre_inscricao = PreInscricao(nome=nome, email=email, telefone=telefone, treinamento=treinamento)
        db.session.add(pre_inscricao)
        db.session.commit()

        titulo = f"Pré-inscrição treinamento {treinamento.capitalize()} | Alyal"
        envio_email(email, titulo, nome, treinamento)

        return jsonify({'success': True})

    return render_template('index.html')


@main.route('/treinamento/python', methods=['GET', 'POST'])
def treinamentoPython():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        treinamento = 'Python'  # Já que esta rota é específica para Python
        pre_inscricao = PreInscricao(nome=nome, email=email, telefone=telefone, treinamento=treinamento)
        db.session.add(pre_inscricao)
        db.session.commit()

        titulo = f"Pré-inscrição treinamento {treinamento} | Alyal"
        envio_email(email, titulo, nome, treinamento)

        return jsonify({'success': True})

    # Definir a data de término da oferta (por exemplo, em 5 dias)
    offer_end_date = datetime.datetime(2024, 10, 15, 23, 59, 59)  # Ajuste para a data desejada
    offer_end_timestamp = int(offer_end_date.timestamp() * 1000)  # Converter para milissegundos

    return render_template('treinamentoPython.html', offer_end_timestamp=offer_end_timestamp)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(matricula=matricula).first()

        if usuario and usuario.check_password(senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            if usuario.is_admin:
                return redirect(url_for('main.admin'))
            else:
                return redirect(url_for('main.aluno'))
        else:
            flash('Número de matrícula ou senha incorretos.', 'danger')

    return render_template('login.html')


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    if request.method == 'POST':
        if 'titulo' in request.form:
            # Adicionar novo lembrete
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data_lembrete = datetime.strptime(request.form['data_lembrete'], '%Y-%m-%dT%H:%M')
            lembrete = Lembrete(titulo=titulo, descricao=descricao, data_lembrete=data_lembrete)
            db.session.add(lembrete)
            db.session.commit()
            flash('Lembrete adicionado com sucesso!', 'success')
        elif 'excluir' in request.form:
            # Excluir lembrete
            lembrete_id = request.form['excluir']
            lembrete = Lembrete.query.get_or_404(lembrete_id)
            db.session.delete(lembrete)
            db.session.commit()
            flash('Lembrete excluído com sucesso.', 'success')

    lembretes = Lembrete.query.order_by(Lembrete.data_lembrete).all()
    return render_template('admin.html', lembretes=lembretes)

#teste
@main.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_usuarios():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form.get('telefone', None)  # Opcional
            observacao = request.form.get('observacao', None)  # Opcional
            status = request.form['status']

            matricula = gerar_matricula_unico()
            usuario = Usuario(
                nome=nome,
                email=email,
                telefone=telefone,
                observacao=observacao,
                matricula=matricula,
                is_admin=status == 'admin',
                ativo=status == 'ativo'
            )
            usuario.set_password(matricula)  # Criptografa a senha usando a matrícula

            db.session.add(usuario)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # Para GET
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)


@main.route('/admin/usuarios/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        'success': True,
        'user': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'observacao': usuario.observacao,
            'is_admin': usuario.is_admin,
            'ativo': usuario.ativo,
            'data_inscricao': usuario.data_inscricao.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@main.route('/admin/usuarios/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_usuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.telefone = request.form.get('telefone', None)
        usuario.observacao = request.form.get('observacao', None)
        status = request.form['status']
        usuario.is_admin = status == 'admin'
        usuario.ativo = status == 'ativo'

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@main.route('/admin/usuarios/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_usuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/aluno')
@login_required
def aluno():
    return render_template('aluno_index.html')

@main.route('/admin/pre-inscricoes')
@login_required
@admin_required
def admin_pre_inscricoes():

    pre_inscricoes = PreInscricao.query.filter_by(arquivado=0).all()

    return render_template('admin_pre_inscricoes.html', pre_inscricoes=pre_inscricoes)


@main.route('/admin/pre-inscricoes/arquivadas')
@login_required
@admin_required
def admin_pre_inscricoes_arquivadas():

    pre_inscricoes = PreInscricao.query.filter_by(arquivado=1).all()

    return render_template('admin_pre_inscricoes.html', pre_inscricoes=pre_inscricoes)

@main.route('/admin/pre-inscricoes/arquivar/<int:id>', methods=['POST'])
@login_required
@admin_required
def arquivar_pre_inscricao(id):
    inscricao = PreInscricao.query.get_or_404(id)
    inscricao.arquivado = True  # Marcar como arquivado
    db.session.commit()
    flash('Pré-inscrição arquivada com sucesso.', 'success')
    return redirect(url_for('main.admin_pre_inscricoes'))


@main.route('/admin/pre-inscricoes/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_pre_inscricao(id):
    inscricao = PreInscricao.query.get_or_404(id)
    db.session.delete(inscricao)
    db.session.commit()
    flash('Pré-inscrição excluída com sucesso.', 'success')
    return redirect(url_for('main.admin_pre_inscricoes'))


@main.route('/admin/lembretes/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_lembrete(id):
    try:
        lembrete = Lembrete.query.get_or_404(id)
        db.session.delete(lembrete)
        db.session.commit()
        flash('Lembrete excluído com sucesso.', 'success')
        return redirect(url_for('main.admin_lembretes'))
    except Exception as e:
        flash('Erro ao excluir o lembrete.', 'danger')
        return redirect(url_for('main.admin_lembretes'))


@main.route('/upload-pdf-url', methods=['POST'])
def upload_pdf_url():
    try:
        pdf_url = request.json.get('url')
        source_id = upload_pdf_via_url(pdf_url)
        return jsonify({'sourceId': source_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/upload-pdf-file', methods=['POST'])
def upload_pdf_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado.'}), 400

        file = request.files['file']
        source_id = upload_pdf_via_file(file)
        return jsonify({'sourceId': source_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/chat-with-pdf', methods=['POST'])
def chat_with_pdf_route():
    try:
        source_id = request.json.get('sourceId')
        user_message = request.json.get('message')
        bot_response = chat_with_pdf(source_id, user_message)
        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500