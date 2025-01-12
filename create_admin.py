from werkzeug.security import generate_password_hash
from project import db, create_app
from project.models import User

app = create_app()

# Ativa o contexto da aplicação para manipulação do banco
with app.app_context():
    # Verifica se já existe um administrador
    admin = User.query.filter_by(email='admin@admin.com').first()
    if admin:
        print("O usuário administrador já existe.")
    else:
        # Cria o primeiro usuário administrador
        admin_user = User(
            name='Administrador',
            email='admin@admin.com',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'  # Define o papel como administrador
        )

        # Adiciona o administrador no banco de dados
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário administrador criado com sucesso!")
