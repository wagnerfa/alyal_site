from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    senha_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"Usuario('{self.nome}', '{self.matricula}', {'Admin' if self.is_admin else 'Ativo' if self.ativo else 'Inativo'})"


class PreInscricao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_inscricao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    arquivado = db.Column(db.Boolean, default=False)  # Campo booleano para arquivamento

    def __repr__(self):
        return f"<PreInscricao('{self.nome}', '{self.email}', Arquivado: {'Sim' if self.arquivado else 'Não'})>"


class Lembrete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_lembrete = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Lembrete('{self.titulo}', '{self.data_lembrete}')>"