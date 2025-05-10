from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from database import db
from database.models import User
import jwt
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# JWT token验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头中获取token
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        # 传递当前用户到下一个函数
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册 - 支持邮箱或手机号注册"""
    data = request.json
    
    # 验证请求数据
    if not data or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # 检查是否提供了邮箱或手机号
    email = data.get('email')
    phone = data.get('phone')
    
    if not email and not phone:
        return jsonify({'message': 'Email or phone is required!'}), 400
    
    # 检查邮箱或手机号是否已存在
    if email and User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists!'}), 409
    
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'message': 'Phone already exists!'}), 409
    
    # 创建新用户
    new_user = User(
        email=email,
        phone=phone
    )
    new_user.set_password(data['password'])
    
    # 保存到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully!', 'user': new_user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 支持邮箱或手机号登录"""
    data = request.json
    
    # 验证请求数据
    if not data or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # 获取用户
    user = None
    if data.get('email'):
        user = User.query.filter_by(email=data['email']).first()
    elif data.get('phone'):
        user = User.query.filter_by(phone=data['phone']).first()
    else:
        return jsonify({'message': 'Email or phone is required!'}), 400
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    # 生成JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    """获取当前用户信息"""
    return jsonify({'user': current_user.to_dict()}), 200