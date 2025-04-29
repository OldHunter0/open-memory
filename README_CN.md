# Open Memory - AI记忆平台

[English](./README.md) | 中文

## 产品概述

### 产品愿景
打造一个能够捕捉、整理和利用用户知识及交互历史的AI记忆平台，帮助用户构建个性化知识库，提升大模型交互体验。

### 解决痛点
- 项目过程中需要在不同平台使用不同chatbot，每次都需要重复解释上下文
- 项目文档需要手动整理，缺乏自动化的知识记录机制

### 应用场景
1. 内容创作者
   - 项目过程中跨平台使用多个大模型
   - 整合参考资料、论文、文档、代码和设计草图
   - 基于记忆的AI项目助手
   - 支持记忆快照保存和恢复

2. 心理咨询
   - 持续跟踪咨询记录
   - 提供连贯的咨询体验

## 核心价值
- 构建个人化的AI记忆库
- 避免与chatbot交流时的重复解释
- 提供更连贯的交互体验
- 保存和共享有价值的知识与见解
- 增强AI对用户长期兴趣和项目的理解

## 系统架构

### 系统组件
1. 网站平台
   - RAG chatbot主界面
   - 记忆管理
   - 记忆历史与回滚
   - 记忆市场
   - 用户权限管理

2. 浏览器插件
   - 上传聊天记录
   - 文本等多模态内容采集
   - 记忆辅助工具

3. 记忆处理引擎
   - 多源数据采集（聊天记录、文本、PDF、图片、代码）
   - 数据预处理
   - 记忆整合

### 记忆类型
1. 个人特质记忆
   - 用户偏好
   - 背景信息
   - 使用习惯

2. 项目记忆
   - 项目相关知识
   - 项目相关资料

3. 知识记忆
   - 学习资料
   - 研究论文
   - 个人笔记

## 功能设计

### 数据采集
- 主动上传：文件、链接、文本
- 浏览器插件采集：网页内容
- 平台对话自动记忆

### 记忆管理
- 核心功能：
  - 记忆创建、注释、查看、删除
  - 记忆检索
- 扩展功能：
  - 记忆历史追踪
  - 记忆回滚

### 记忆应用
- RAG增强对话
- 记忆快照
- 记忆市场

## 快速开始

### 1. 克隆代码
```bash
git clone https://github.com/RecallNet0526/ai-memory.git
cd ai-memory
```

### 2. 启动后端服务

#### 使用 Docker Compose
```bash
cd braindance_back
docker-compose up -d
```

#### 配置和运行后端
```bash
pip install -r requirements.txt
python run_braindance.py --port 5002
```

### 3. 配置和运行前端
```bash
cd braindance_front
npm install
npm start
```

访问 http://localhost:3000 开始使用应用。

## 项目结构
```
- braindance_back/ (Python后端)
  - api.py (API接口)
  - chat.py (聊天功能)
  - config.py (配置信息)
  - memory_store.py (记忆存储)
  - main.py (程序入口)
  - docker-compose.yaml (Docker配置)

- braindance_front/ (React前端)
  - src/
    - components/ (UI组件)
    - api/ (API服务)
    - styles/ (样式文件)
    - utils/ (工具函数)

- your_memory/ (记忆快照)
```