import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import Equipment, EquipmentUsage, Mission, User
from datetime import datetime

# Configurações
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# Blueprint para itens
items = Blueprint('items', __name__)

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image_file):
    """Salva a imagem e retorna o caminho relativo."""
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        return f'images/{filename}'
    return None

def create_or_update_item(name, description, category, quantity, image_file=None, existing_item=None):
    """Função para criar ou atualizar um item."""
    image_url = save_image(image_file) if image_file else None

    if existing_item:
        existing_item.name = name
        existing_item.description = description
        existing_item.category = category
        existing_item.quantity = quantity
        existing_item.image_url = image_url if image_url else existing_item.image_url

        if current_user.is_authenticated:
            existing_item.current_user = current_user.email
            existing_item.last_borrowed = datetime.utcnow()
            existing_item.times_used += 1

        db.session.commit()
    else:
        new_item = Equipment(
            name=name,
            description=description,
            category=category,
            quantity=quantity,
            image_url=image_url,
            current_user_id=current_user.id if current_user.is_authenticated else None,  # Corrigido aqui para usar 'current_user_id'
            last_borrowed=datetime.utcnow(),
            times_used=1,
            is_used=False  # Marca o item como não utilizado inicialmente
        )
        db.session.add(new_item)
        db.session.commit()

def process_item_form(name, description, category, quantity, image_file, existing_item=None):
    """Valida e processa os dados do formulário."""
    if not all([name, description, category, quantity]):
        flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
        return False
    create_or_update_item(name, description, category, quantity, image_file, existing_item)
    return True

@items.before_app_request
def limit_content_length():
    """Limita o tamanho do arquivo para 5MB."""
    if request.content_length and request.content_length > MAX_CONTENT_LENGTH:
        flash('O arquivo é muito grande, o tamanho máximo é 5MB.', 'danger')
        return redirect(request.referrer or url_for('items.manage_items'))

@items.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_items():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = request.form.get('quantity', type=int)
        image_file = request.files.get('image')

        if process_item_form(name, description, category, quantity, image_file):
            flash(f'Item {name} adicionado com sucesso!', 'success')
            return redirect(url_for('items.manage_items'))

    items = Equipment.query.all()
    return render_template('manage_items.html', items=items, user_email=current_user.email)

@items.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = request.form.get('quantity', type=int)
        image_file = request.files.get('image')

        if process_item_form(name, description, category, quantity, image_file):
            flash(f'Item {name} adicionado com sucesso!', 'success')
            return redirect(url_for('items.manage_items'))

    return render_template('add_item.html')

@items.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if current_user.email != 'admin@admin.com':
        flash('Acesso negado: somente administradores podem editar itens.', 'danger')
        return redirect(url_for('items.manage_items'))
    
    item = Equipment.query.get_or_404(item_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = request.form.get('quantity', type=int)
        image_file = request.files.get('image')

        if process_item_form(name, description, category, quantity, image_file, existing_item=item):
            flash(f'Item {item.name} atualizado com sucesso!', 'success')
            return redirect(url_for('items.manage_items'))

    return render_template('edit_item.html', item=item)

@items.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if current_user.email != 'admin@admin.com':
        flash('Acesso negado: somente administradores podem excluir itens.', 'danger')
        return redirect(url_for('items.manage_items'))
    
    # Verificar se o item existe
    item = Equipment.query.get_or_404(item_id)

    # Verificar se existe um registro de uso na tabela 'equipment_usage' (supondo que o relacionamento seja feito pelo campo item_id)
    usage_record = EquipmentUsage.query.filter_by(equipment_id=item.id).first()

    if usage_record:  # Se existir um registro de uso, o item não pode ser excluído
        flash(f'O item "{item.name}" não pode ser excluído, pois já possui registro de uso.', 'warning')
        return redirect(url_for('items.manage_items'))
    
    # Se não houver registro de uso, deleta o item
    db.session.delete(item)
    db.session.commit()
    flash(f'Item {item.name} removido com sucesso!', 'success')
    return redirect(url_for('items.manage_items'))


@items.route('/view/<int:item_id>', methods=['GET'])
@login_required
def view_item(item_id):
    item = Equipment.query.get_or_404(item_id)
    return render_template('view_item.html', item=item)

@items.route('/equipamento/usar/<int:item_id>', methods=['GET', 'POST'])
@login_required
def use_equipment(item_id):
    item = Equipment.query.get_or_404(item_id)

    # Verificando se há unidades disponíveis e se o item não está em uso
    if item.quantity <= 0:
        return render_template('use_equipment.html', 
                               item=item, 
                               alert_message="Não há unidades disponíveis para uso.", 
                               alert_type="error")
    
    # Se o item não está disponível, mostramos um alerta
    if item.status == 'Em uso':
        return render_template('use_equipment.html', 
                               item=item, 
                               alert_message="O equipamento já está em uso.", 
                               alert_type="error")

    if request.method == 'POST':
        action = request.form['action']
        mission_name = request.form['mission_name']
        mission_description = request.form['mission_description']
        start_date = request.form['start_date']  # Data de início da missão

        # Corrigindo a conversão da data para incluir o 'T'
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')

        # Criando a missão
        new_mission = Mission(
            name=mission_name,
            description=mission_description,
            status="Ativa",
            start_date=start_date,
            created_by=current_user.id
        )
        db.session.add(new_mission)
        db.session.commit()  # Commit a missão antes de criar o uso

        # Criando o registro de uso do equipamento
        usage = EquipmentUsage(
            equipment_id=item.id,
            user_id=current_user.id,
            action=action,
            status="Em uso",
            usage_date=datetime.utcnow(),
            mission_id=new_mission.id  # Relacionando o uso à missão
        )
        db.session.add(usage)

        # Atualizando o status do item e decrementando a quantidade disponível
        item.quantity -= 1  # Decrementa a quantidade de unidades
        if item.quantity == 0:
            item.status = "Em uso"  # Se não há mais unidades disponíveis, o item está totalmente em uso
        db.session.commit()

        return redirect(url_for('items.manage_items'))

    return render_template('use_equipment.html', item=item)



from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Equipment, EquipmentUsage, Mission
from . import db

@items.route('/equipamento/devolver/<int:item_id>', methods=['GET', 'POST'])
@login_required
def return_equipment(item_id):
    item = Equipment.query.get_or_404(item_id)

    if request.method == 'POST':
        # Verificando se o equipamento está em uso antes de tentar devolver
        usage = EquipmentUsage.query.filter_by(equipment_id=item.id, user_id=current_user.id, status='Em uso').first()
        if usage:
            # Atualizando o status do uso para "Devolvido"
            usage.status = 'Devolvido'
            usage.return_date = datetime.utcnow()  # Define a data e hora atual como data de devolução
            usage.reason_for_return = request.form.get('reason_for_return')  # Captura a observação
            
            # Atualizando o status do equipamento
            item.status = 'Disponível'
            item.is_used = False  # Marca o item como não em uso

            # Atualizando a quantidade disponível do item
            item.quantity += 1  # Incrementa a quantidade disponível

            # Atualizando o status da missão relacionada ao equipamento
            mission = Mission.query.get(usage.mission_id)  # Obtém a missão associada
            if mission:
                mission.status = 'Encerrada'  # Marca a missão como encerrada

            # Salvando as mudanças no banco de dados
            db.session.commit()

            flash('Equipamento devolvido com sucesso!', 'success')
        else:
            # Caso o equipamento não esteja em uso
            flash('Este equipamento não está em uso ou já foi devolvido.', 'error')

        return redirect(url_for('items.manage_items'))

    # Quando a página for acessada com GET, exibe o formulário de devolução
    return render_template('return_equipment.html', item=item)