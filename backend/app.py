from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.memory import memory_bp
from routes.chat import chat_bp
from database import init_db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(memory_bp, url_prefix='/api/memory')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# 初始化数据库
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5002)))