# Open Memory 后端服务

Open Memory 的后端服务，基于 Flask 实现，提供记忆管理、用户认证和基于记忆的对话功能。

## 功能特性

### 核心功能
- **用户系统**：支持用户通过邮箱或手机号注册和登录
- **记忆管理**：创建、查看、更新和删除多个记忆
- **记忆内容**：向记忆中添加和管理内容
- **记忆检索**：基于语义相似度搜索记忆内容

### 非核心功能
- **记忆历史**：记录记忆的变更历史，支持回滚操作
- **记忆快照**：创建和恢复记忆状态的快照
- **RAG增强对话**：基于检索增强生成的对话功能

## 技术栈
- **Web框架**：Flask
- **数据库**：SQLAlchemy + PostgreSQL/SQLite
- **向量存储**：Weaviate
- **大模型集成**：LangChain + OpenAI
- **认证**：JWT

## 快速开始

### 1. 设置环境变量
复制 `.env.example` 文件为 `.env`，并设置必要的环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，设置API密钥等
```

### 2. 启动方式

#### 使用 Docker Compose（推荐）
```bash
docker-compose up -d
```

#### 手动运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 3. API 文档

应用启动后，API文档可以通过以下地址访问：
- Swagger UI: http://localhost:5002/api/docs

## API 端点概览

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 记忆管理
- `GET /api/memory/` - 获取所有记忆
- `POST /api/memory/` - 创建新记忆
- `GET /api/memory/{memory_id}` - 获取特定记忆
- `PUT /api/memory/{memory_id}` - 更新记忆
- `DELETE /api/memory/{memory_id}` - 删除记忆

### 记忆内容
- `POST /api/memory/{memory_id}/content` - 添加记忆内容
- `DELETE /api/memory/{memory_id}/content/{content_id}` - 删除记忆内容
- `GET /api/memory/{memory_id}/search` - 搜索记忆内容

### 记忆历史
- `GET /api/memory/{memory_id}/history` - 获取记忆历史
- `POST /api/memory/{memory_id}/rollback/{history_id}` - 回滚记忆

### 快照管理
- `POST /api/memory/snapshot` - 创建快照
- `POST /api/memory/snapshot/{snapshot_id}/restore` - 恢复快照

### 对话功能
- `POST /api/chat/memory/{memory_id}` - 基于记忆的对话
- `GET /api/chat/memory/{memory_id}/conversation` - 获取对话历史

## 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request