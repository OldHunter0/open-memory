import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

class LLMService:
    """大模型服务 - 使用OpenAI API实现"""
    
    def __init__(self):
        """初始化LLM服务"""
        # 初始化OpenAI客户端
        self.llm = ChatOpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            model=os.environ.get('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo'),
            temperature=0.7
        )
    
    async def generate_response(self, user_message: str, context: List[Dict], memory_name: str, memory_description: str) -> str:
        """生成回复"""
        # 格式化上下文
        formatted_context = self._format_context(context)
        
        # 创建系统提示
        system_prompt = f"""你是一个有记忆的AI助手，你可以通过记忆为用户提供有针对性的帮助。
        
记忆名称: {memory_name}
记忆描述: {memory_description}

基于以下检索到的相关记忆内容回答用户的问题：
{formatted_context}

如果相关记忆为空或不相关，只使用你的基础知识回答。
请简明扼要地回答用户问题，不要提及你在使用记忆或检索系统。"""
        
        # 准备消息列表
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        # 调用LLM生成回复
        response = await self.llm.ainvoke(messages)
        
        return response.content
    
    def _format_context(self, context: List[Dict]) -> str:
        """格式化上下文"""
        if not context:
            return "没有找到相关记忆内容。"
        
        formatted = "相关记忆内容:\n\n"
        
        for i, item in enumerate(context):
            content = item['content']
            similarity = item.get('similarity', 0)
            
            # 限制内容长度
            if len(content) > 1000:
                content = content[:997] + "..."
            
            formatted += f"--- 记忆片段 {i+1} (相关度: {similarity:.2f}) ---\n"
            formatted += content + "\n\n"
        
        return formatted 