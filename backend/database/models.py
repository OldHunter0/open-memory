from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    memories = db.relationship('Memory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Memory(db.Model):
    """记忆模型 - 记忆是用户管理的一个单位"""
    __tablename__ = 'memories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    memory_type = db.Column(db.String(50), nullable=False)  # 个人特质/项目/知识
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    contents = db.relationship('MemoryContent', backref='memory', lazy=True, cascade='all, delete-orphan')
    history = db.relationship('MemoryHistory', backref='memory', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'memory_type': self.memory_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MemoryContent(db.Model):
    """记忆内容 - 存储实际的记忆内容片段"""
    __tablename__ = 'memory_contents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = db.Column(db.String(36), db.ForeignKey('memories.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # text, pdf, image, code
    metadata = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'memory_id': self.memory_id,
            'content': self.content,
            'content_type': self.content_type,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

class MemoryHistory(db.Model):
    """记忆历史 - 记录记忆的变更历史"""
    __tablename__ = 'memory_history'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = db.Column(db.String(36), db.ForeignKey('memories.id'), nullable=False)
    operation = db.Column(db.String(50), nullable=False)  # create, update, delete
    content_snapshot = db.Column(db.JSON, nullable=True)  # 操作时的内容快照
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'memory_id': self.memory_id,
            'operation': self.operation,
            'content_snapshot': self.content_snapshot,
            'created_at': self.created_at.isoformat()
        }