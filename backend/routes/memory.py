from flask import Blueprint, request, jsonify
from database import db
from database.models import Memory, MemoryContent, MemoryHistory
from routes.auth import token_required
from datetime import datetime
from services.vector_store import VectorStore
import json

memory_bp = Blueprint('memory', __name__)
vector_store = VectorStore()

@memory_bp.route('/', methods=['GET'])
@token_required
def get_memories(current_user):
    """获取用户的所有记忆"""
    memories = Memory.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'memories': [memory.to_dict() for memory in memories]
    }), 200

@memory_bp.route('/<memory_id>', methods=['GET'])
@token_required
def get_memory(current_user, memory_id):
    """获取特定记忆的详细信息"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    # 获取记忆内容
    contents = MemoryContent.query.filter_by(memory_id=memory_id).all()
    
    return jsonify({
        'memory': memory.to_dict(),
        'contents': [content.to_dict() for content in contents]
    }), 200

@memory_bp.route('/', methods=['POST'])
@token_required
def create_memory(current_user):
    """创建新的记忆"""
    data = request.json
    
    # 验证请求数据
    if not data or not data.get('name') or not data.get('memory_type'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # 创建新记忆
    new_memory = Memory(
        user_id=current_user.id,
        name=data['name'],
        description=data.get('description', ''),
        memory_type=data['memory_type']
    )
    
    # 保存到数据库
    db.session.add(new_memory)
    db.session.commit()
    
    # 创建历史记录
    memory_history = MemoryHistory(
        memory_id=new_memory.id,
        operation='create',
        content_snapshot=new_memory.to_dict()
    )
    db.session.add(memory_history)
    db.session.commit()
    
    return jsonify({
        'message': 'Memory created successfully!',
        'memory': new_memory.to_dict()
    }), 201

@memory_bp.route('/<memory_id>', methods=['PUT'])
@token_required
def update_memory(current_user, memory_id):
    """更新记忆信息"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    data = request.json
    
    # 保存更新前的快照
    old_snapshot = memory.to_dict()
    
    # 更新记忆信息
    if data.get('name'):
        memory.name = data['name']
    if data.get('description') is not None:
        memory.description = data['description']
    if data.get('memory_type'):
        memory.memory_type = data['memory_type']
    
    # 更新时间戳
    memory.updated_at = datetime.utcnow()
    
    # 保存到数据库
    db.session.commit()
    
    # 创建历史记录
    memory_history = MemoryHistory(
        memory_id=memory.id,
        operation='update',
        content_snapshot={
            'old': old_snapshot,
            'new': memory.to_dict()
        }
    )
    db.session.add(memory_history)
    db.session.commit()
    
    return jsonify({
        'message': 'Memory updated successfully!',
        'memory': memory.to_dict()
    }), 200

@memory_bp.route('/<memory_id>', methods=['DELETE'])
@token_required
def delete_memory(current_user, memory_id):
    """删除记忆"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    # 保存要删除的记忆快照
    memory_snapshot = memory.to_dict()
    
    # 创建历史记录
    memory_history = MemoryHistory(
        memory_id=memory.id,
        operation='delete',
        content_snapshot=memory_snapshot
    )
    db.session.add(memory_history)
    
    # 删除向量存储中的记忆
    vector_store.delete_vectors(memory_id)
    
    # 删除记忆
    db.session.delete(memory)
    db.session.commit()
    
    return jsonify({
        'message': 'Memory deleted successfully!'
    }), 200

@memory_bp.route('/<memory_id>/content', methods=['POST'])
@token_required
def add_memory_content(current_user, memory_id):
    """向记忆中添加内容"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    data = request.json
    
    # 验证请求数据
    if not data or not data.get('content') or not data.get('content_type'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # 创建新的记忆内容
    new_content = MemoryContent(
        memory_id=memory_id,
        content=data['content'],
        content_type=data['content_type'],
        metadata=data.get('metadata', {})
    )
    
    # 保存到数据库
    db.session.add(new_content)
    db.session.commit()
    
    # 处理向量化存储
    vector_store.add_text(
        memory_id=memory_id,
        content_id=new_content.id,
        text=data['content'],
        metadata=data.get('metadata', {})
    )
    
    # 更新记忆的更新时间
    memory.updated_at = datetime.utcnow()
    db.session.commit()
    
    # 创建历史记录
    memory_history = MemoryHistory(
        memory_id=memory.id,
        operation='add_content',
        content_snapshot=new_content.to_dict()
    )
    db.session.add(memory_history)
    db.session.commit()
    
    return jsonify({
        'message': 'Content added successfully!',
        'content': new_content.to_dict()
    }), 201

@memory_bp.route('/<memory_id>/content/<content_id>', methods=['DELETE'])
@token_required
def delete_memory_content(current_user, memory_id, content_id):
    """删除记忆内容"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    content = MemoryContent.query.filter_by(id=content_id, memory_id=memory_id).first()
    
    if not content:
        return jsonify({'message': 'Content not found!'}), 404
    
    # 保存要删除的内容快照
    content_snapshot = content.to_dict()
    
    # 从向量存储中删除
    vector_store.delete_text(content_id)
    
    # 删除内容
    db.session.delete(content)
    db.session.commit()
    
    # 创建历史记录
    memory_history = MemoryHistory(
        memory_id=memory.id,
        operation='delete_content',
        content_snapshot=content_snapshot
    )
    db.session.add(memory_history)
    db.session.commit()
    
    return jsonify({
        'message': 'Content deleted successfully!'
    }), 200

@memory_bp.route('/<memory_id>/search', methods=['GET'])
@token_required
def search_memory(current_user, memory_id):
    """在特定记忆中搜索内容"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({'message': 'Query parameter is required!'}), 400
    
    # 搜索向量存储
    results = vector_store.search(
        memory_id=memory_id,
        query=query,
        limit=10
    )
    
    return jsonify({
        'results': results
    }), 200

@memory_bp.route('/<memory_id>/history', methods=['GET'])
@token_required
def get_memory_history(current_user, memory_id):
    """获取记忆的历史记录"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    # 获取历史记录
    history = MemoryHistory.query.filter_by(memory_id=memory_id).order_by(MemoryHistory.created_at.desc()).all()
    
    return jsonify({
        'history': [item.to_dict() for item in history]
    }), 200

@memory_bp.route('/<memory_id>/rollback/<history_id>', methods=['POST'])
@token_required
def rollback_memory(current_user, memory_id, history_id):
    """回滚记忆到特定历史点"""
    memory = Memory.query.filter_by(id=memory_id, user_id=current_user.id).first()
    
    if not memory:
        return jsonify({'message': 'Memory not found!'}), 404
    
    history_item = MemoryHistory.query.filter_by(id=history_id, memory_id=memory_id).first()
    
    if not history_item:
        return jsonify({'message': 'History item not found!'}), 404
    
    # 根据历史操作类型执行回滚
    if history_item.operation == 'create':
        # 记忆创建操作，无法回滚
        return jsonify({'message': 'Cannot rollback to memory creation!'}), 400
    
    elif history_item.operation == 'update':
        # 回滚到更新前的状态
        old_data = history_item.content_snapshot.get('old', {})
        
        if old_data:
            memory.name = old_data.get('name', memory.name)
            memory.description = old_data.get('description', memory.description)
            memory.memory_type = old_data.get('memory_type', memory.memory_type)
            
            db.session.commit()
    
    elif history_item.operation == 'add_content':
        # 回滚添加内容（删除该内容）
        content_data = history_item.content_snapshot
        if content_data and content_data.get('id'):
            content = MemoryContent.query.filter_by(id=content_data['id'], memory_id=memory_id).first()
            if content:
                # 从向量存储中删除
                vector_store.delete_text(content.id)
                
                # 删除内容
                db.session.delete(content)
                db.session.commit()
    
    elif history_item.operation == 'delete_content':
        # 回滚内容删除（重新创建内容）
        content_data = history_item.content_snapshot
        if content_data:
            # 检查内容是否已存在
            existing_content = MemoryContent.query.filter_by(id=content_data['id']).first()
            
            if not existing_content:
                # 重新创建内容
                new_content = MemoryContent(
                    id=content_data['id'],
                    memory_id=memory_id,
                    content=content_data['content'],
                    content_type=content_data['content_type'],
                    metadata=content_data.get('metadata', {}),
                    created_at=datetime.fromisoformat(content_data['created_at'])
                )
                
                # 保存到数据库
                db.session.add(new_content)
                db.session.commit()
                
                # 处理向量化存储
                vector_store.add_text(
                    memory_id=memory_id,
                    content_id=new_content.id,
                    text=content_data['content'],
                    metadata=content_data.get('metadata', {})
                )
    
    # 记录回滚操作
    rollback_history = MemoryHistory(
        memory_id=memory_id,
        operation='rollback',
        content_snapshot={
            'rolled_back_to': history_id,
            'original_operation': history_item.operation
        }
    )
    db.session.add(rollback_history)
    db.session.commit()
    
    return jsonify({
        'message': 'Memory rolled back successfully!'
    }), 200

@memory_bp.route('/snapshot', methods=['POST'])
@token_required
def create_snapshot(current_user):
    """创建当前所有记忆的快照"""
    data = request.json
    name = data.get('name', f"Snapshot-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")
    
    # 获取用户的所有记忆
    memories = Memory.query.filter_by(user_id=current_user.id).all()
    
    # 准备快照数据
    snapshot_data = []
    
    for memory in memories:
        memory_data = memory.to_dict()
        
        # 获取记忆内容
        contents = MemoryContent.query.filter_by(memory_id=memory.id).all()
        memory_data['contents'] = [content.to_dict() for content in contents]
        
        snapshot_data.append(memory_data)
    
    # 创建新的记忆作为快照
    snapshot_memory = Memory(
        user_id=current_user.id,
        name=name,
        description=f"Snapshot created at {datetime.utcnow().isoformat()}",
        memory_type='snapshot'
    )
    
    # 保存到数据库
    db.session.add(snapshot_memory)
    db.session.commit()
    
    # 将快照数据作为内容保存
    snapshot_content = MemoryContent(
        memory_id=snapshot_memory.id,
        content=json.dumps(snapshot_data),
        content_type='snapshot',
        metadata={'created_at': datetime.utcnow().isoformat()}
    )
    
    db.session.add(snapshot_content)
    db.session.commit()
    
    return jsonify({
        'message': 'Snapshot created successfully!',
        'snapshot': snapshot_memory.to_dict()
    }), 201

@memory_bp.route('/snapshot/<snapshot_id>/restore', methods=['POST'])
@token_required
def restore_snapshot(current_user, snapshot_id):
    """从快照恢复记忆"""
    snapshot_memory = Memory.query.filter_by(id=snapshot_id, user_id=current_user.id, memory_type='snapshot').first()
    
    if not snapshot_memory:
        return jsonify({'message': 'Snapshot not found!'}), 404
    
    # 获取快照内容
    snapshot_content = MemoryContent.query.filter_by(memory_id=snapshot_id, content_type='snapshot').first()
    
    if not snapshot_content:
        return jsonify({'message': 'Snapshot content not found!'}), 404
    
    # 解析快照数据
    try:
        snapshot_data = json.loads(snapshot_content.content)
    except:
        return jsonify({'message': 'Invalid snapshot data!'}), 400
    
    # 删除现有的记忆（排除快照类型）
    existing_memories = Memory.query.filter_by(user_id=current_user.id).filter(Memory.memory_type != 'snapshot').all()
    
    for memory in existing_memories:
        # 从向量存储中删除
        vector_store.delete_vectors(memory.id)
        
        # 删除记忆
        db.session.delete(memory)
    
    # 从快照恢复记忆
    restored_memories = []
    
    for memory_data in snapshot_data:
        # 创建新记忆
        new_memory = Memory(
            user_id=current_user.id,
            name=memory_data['name'],
            description=memory_data['description'],
            memory_type=memory_data['memory_type']
        )
        
        db.session.add(new_memory)
        db.session.flush()  # 获取新的ID
        
        # 恢复内容
        contents = memory_data.get('contents', [])
        
        for content_data in contents:
            new_content = MemoryContent(
                memory_id=new_memory.id,
                content=content_data['content'],
                content_type=content_data['content_type'],
                metadata=content_data.get('metadata', {})
            )
            
            db.session.add(new_content)
            db.session.flush()
            
            # 处理向量化存储
            if content_data['content_type'] != 'snapshot':  # 不处理嵌套快照
                vector_store.add_text(
                    memory_id=new_memory.id,
                    content_id=new_content.id,
                    text=content_data['content'],
                    metadata=content_data.get('metadata', {})
                )
        
        restored_memories.append(new_memory.to_dict())
    
    db.session.commit()
    
    return jsonify({
        'message': 'Snapshot restored successfully!',
        'restored_memories': restored_memories
    }), 200