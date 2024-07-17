from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    # Criar o primeiro usuário administrador
    admin = Usuario(nome='Wagner Andrade', email='wagnerandrade.dev@gmail.com', matricula='000001', is_admin=True)
    admin.set_password('castiell')

    db.session.add(admin)
    db.session.commit()
    print("Administrador adicionado com sucesso!")
