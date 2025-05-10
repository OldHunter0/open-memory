from flask import Blueprint, request, jsonify
from database import db
from database.models import Memory, MemoryContent
from routes.auth import token_required
from services.vector_store import VectorStore
from services.llm_service import LLMService
from datetime import datetime

chat_bp = Blueprint('chat', __name__)
vector_store = VectorStore()
llm_service = LLMService()

@chat_bp.route('/memory/<memory_id>', methods=['POST'])
@token_required
def chat_with_memory(current_user, memory_id):
    """基于特定记忆进行对话"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    data = request.json
    
    if not data or not data.get('message'):
        return jsonify({'message': 'Message is required!'}), 400
    
    # 用户消息
    user_message = data['message']
    
    # 从记忆中检索相关内容
    relevant_content = vector_store.search(
        memory_id=memory_id,
        query=user_message,
        limit=5  # 最多返回5条相关内容
    )
    
    # 构建上下文
    context = []
    for item in relevant_content:
        # 获取完整内容
        content = MemoryContent.query.filter_by(id=item['content_id']).first()
        if content:
            context.append({
                'content': content.content,
                'content_type': content.content_type,
                'metadata': content.metadata,
                'similarity': item['similarity']
            })
    
    # 调用LLM服务生成回复
    response = llm_service.generate_response(
        user_message=user_message,
        context=context,
        memory_name=memory.name,
        memory_description=memory.description
    )
    
    # 保存对话到记忆
    conversation = f"User: {user_message}\nAI: {response}"
    new_content = MemoryContent(
        memory_id=memory_id,
        content=conversation,
        content_type='conversation',
        metadata={
            'timestamp': datetime.utcnow().isoformat(),
            'relevant_context': [item['content_id'] for item in relevant_content]
        }
    )
    
    db.session.add(new_content)
    db.session.commit()
    
    # 处理向量化存储
    vector_store.add_text(
        memory_id=memory_id,
        content_id=new_content.id,
        text=conversation,
        metadata=new_content.metadata
    )
    
    return jsonify({
        'response': response,
        'relevant_context': context
    }), 200

@chat_bp.route('/memory/<memory_id>/conversation', methods=['GET'])
@token_required
def get_conversations(current_user, memory_id):
    """获取特定记忆的对话历史"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    # 获取对话内容
    conversations = MemoryContent.query.filter_by(
        memory_id=memory_id,
        content_type='conversation'
    ).order_by(MemoryContent.created_at.desc()).all()
    
    return jsonify({
        'conversations': [conv.to_dict() for conv in conversations]
    }), 200