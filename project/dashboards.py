from flask import Blueprint, render_template
from .models import Equipment, Mission, EquipmentUsage, User
from flask_login import login_required
from . import db
from datetime import datetime

# Blueprint para dashboards
dashboards = Blueprint('dashboards', __name__)

@dashboards.route('/dashboard')
@login_required
def dashboard():
    # Dados para o Dashboard
    total_items = Equipment.query.count()
    used_items = Equipment.query.filter_by(status='em uso').count()
    
    # Dados de Histórico de Uso
    usage_history = EquipmentUsage.query.order_by(EquipmentUsage.usage_date.desc()).limit(10).all()
    
    # Dados de Missões
    missions = Mission.query.all()
    
    # Tempo de uso total dos itens
    usage_time = db.session.query(
        EquipmentUsage.equipment_id, 
        db.func.sum(db.func.julianday(EquipmentUsage.usage_date) - db.func.julianday(EquipmentUsage.return_date)).label('total_time')
    ).group_by(EquipmentUsage.equipment_id).all()

    return render_template(
        'dashboard.html',
        total_items=total_items,
        used_items=used_items,
        usage_history=usage_history,
        missions=missions,
        usage_time=usage_time
    )
