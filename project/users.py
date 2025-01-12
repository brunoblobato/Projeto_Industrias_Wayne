from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db

users = Blueprint('users', __name__)  # Define o blueprint para usuários


@users.route('/users')
@login_required
def list_users():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem visualizar usuários.')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('users.html', users=users)


@users.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem editar usuários.')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role', user.role)
        db.session.commit()
        flash('Usuário atualizado com sucesso.')
        return redirect(url_for('users.list_users'))

    return render_template('edit_user.html', user=user)


@users.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem excluir usuários.')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('users.list_users'))
    
    # Impede a exclusão do administrador principal
    if user.email == 'admin@admin.com':
        flash('Não é permitido excluir o administrador principal.')
        return redirect(url_for('users.list_users'))

    # Verificação de confirmação de exclusão para outros usuários
    confirmation = request.form.get('confirm')
    if confirmation != 'yes':
        flash('Você precisa confirmar a exclusão do usuário.')
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso.')
    return redirect(url_for('users.list_users'))


@users.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem alterar o status dos usuários.')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado.')
        return redirect(url_for('users.list_users'))
    
        # Impede que o administrador principal seja desativado
    if user.email == 'admin@admin.com':
        flash('Não é permitido desativar o administrador principal.')
        return redirect(url_for('users.list_users'))

    user.is_active = not user.is_active
    db.session.commit()
    flash('Status do usuário alterado com sucesso.')
    return redirect(url_for('users.list_users'))

@users.route('/users/<int:user_id>/update_password', methods=['GET', 'POST'])
@login_required
def update_admin_password(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem alterar a senha.')
        return redirect(url_for('main.index'))

    user = User.query.get(user_id)
    if not user or user.email != 'admin@admin.com':
        flash('Usuário não encontrado ou não é o administrador.')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if not new_password:
            flash('Nova senha é obrigatória.')
            return redirect(url_for('users.update_admin_password', user_id=user_id))

        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Senha do administrador atualizada com sucesso.')
        return redirect(url_for('users.list_users'))

    return render_template('update_admin_password.html', user=user)
