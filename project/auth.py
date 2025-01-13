from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
@login_required
def signup():
    if current_user.role != 'admin':  # Bloqueia acesso se não for admin
        flash('Acesso negado. Apenas administradores podem criar usuários.')
        return redirect(url_for('auth.login'))
    users = User.query.all()
    return render_template('signup.html', users=users)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
@login_required  # Só um usuário logado pode acessar o signup
def signup_post():
    if current_user.role != 'admin':  # Verifica se o usuário logado é administrador
        flash('Apenas administradores podem criar novos usuários.')
        return redirect(url_for('auth.login'))

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    role = request.form.get('role', 'user')  # Pega o role do formulário (padrão: 'user')

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email já cadastrado.')
        return redirect(url_for('users.list_users'))

    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        role=role  # Define o papel do usuário
    )

    db.session.add(new_user)
    db.session.commit()

    flash('Usuário criado com sucesso.')
    return redirect(url_for('users.list_users'))


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Por favor, verifique suas credenciais de login e tente novamente.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))

@auth.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('auth.signup'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        db.session.commit()
        flash('Usuário atualizado com sucesso.')
        return redirect(url_for('auth.signup'))
    
    return render_template('edit_user.html', user=user)

@auth.route('/toggle_user_status/<int:user_id>')
@login_required
def toggle_user_status(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('auth.signup'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('auth.signup'))

    user.is_active = not user.is_active
    db.session.commit()
    flash('Status do usuário alterado com sucesso.')
    return redirect(url_for('auth.signup'))

@auth.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('auth.signup'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('auth.signup'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso.')
    return redirect(url_for('auth.signup'))
