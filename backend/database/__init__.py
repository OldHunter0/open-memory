from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import os

db = SQLAlchemy()

def init_db():
    """初始化数据库"""
    current_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///memory.db')
    current_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化SQLAlchemy
    db.init_app(current_app)
    
    # 创建所有表
    from .models import User, Memory, MemoryContent, MemoryHistory
    db.create_all()