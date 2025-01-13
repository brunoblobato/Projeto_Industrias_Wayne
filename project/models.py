from flask_login import UserMixin
from datetime import datetime
from . import db

# Classe User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)

    # Relacionamentos
    created_missions = db.relationship('Mission', back_populates='creator', lazy=True)
    usages = db.relationship('EquipmentUsage', back_populates='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name} - Role: {self.role}>"

# Classe Equipment
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default='disponível')
    times_used = db.Column(db.Integer, nullable=False, default=0)
    current_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    last_borrowed = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    image_url = db.Column(db.String(255), nullable=True, default='default_image.jpg')

    # Relacionamento
    usages = db.relationship('EquipmentUsage', back_populates='equipment')
    is_used = db.Column(db.Boolean, default=False)  # Verifique se essa linha existe

    def __repr__(self):
        return f"<Equipment {self.name} - Status: {self.status}>"

# Classe EquipmentUsage
class EquipmentUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'), nullable=True)
    reason_for_return = db.Column(db.String(255), nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)  # Adicionando a data de devolução


    # Relacionamentos
    equipment = db.relationship('Equipment', back_populates='usages')
    user = db.relationship('User', back_populates='usages')
    mission = db.relationship('Mission', back_populates='equipment_usages')
    
    def __repr__(self):
        return f"<EquipmentUsage {self.equipment.name} - Mission: {self.mission.name}>"

# Classe Mission
class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Ativa")
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)  # Data de encerramento da missão
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relacionamentos
    creator = db.relationship('User', back_populates='created_missions')
    equipment_usages = db.relationship('EquipmentUsage', back_populates='mission')

    def __repr__(self):
        return f"<Mission {self.name} - Status: {self.status}>"

