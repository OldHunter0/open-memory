// 监听来自弹出窗口的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'getConversation') {
    const host = window.location.host;
    let conversationData = null;
    
    // 根据不同的网站调用不同的提取方法
    if (host.includes('chat.openai.com')) {
      conversationData = extractChatGPT();
    } else if (host.includes('chat.deepseek.com')) {
      conversationData = extractDeepSeek();
    } else if (host.includes('chat.monica.im')) {
      conversationData = extractMonica();
    }
    
    if (conversationData) {
      sendResponse({success: true, conversationData: conversationData});
    } else {
      sendResponse({success: false, error: '无法提取对话内容'});
    }
    
    return true; // 保持消息通道开放，异步响应
  }
});

// 提取ChatGPT对话
function extractChatGPT() {
  try {
    // 查找对话容器
    const threadContainer = document.querySelector('div[data-testid="conversation-thread"]');
    if (!threadContainer) return null;
    
    // 获取所有消息元素
    const messageElements = threadContainer.querySelectorAll('[data-message-author-role]');
    if (messageElements.length === 0) return null;
    
    // 提取消息内容
    const messages = Array.from(messageElements).map(element => {
      const role = element.getAttribute('data-message-author-role');
      const contentElement = element.querySelector('div[data-message-text-content="true"]');
      const content = contentElement ? contentElement.textContent.trim() : '';
      
      return { role, content };
    });
    
    return {
      platform: 'ChatGPT',
      timestamp: new Date().toISOString(),
      messages: messages
    };
  } catch (error) {
    console.error('提取ChatGPT对话时出错:', error);
    return null;
  }
}

// 提取DeepSeek对话
function extractDeepSeek() {
  try {
    // 查找对话容器 (根据DeepSeek的DOM结构调整选择器)
    const chatContainer = document.querySelector('.chat-content');
    if (!chatContainer) return null;
    
    // 获取所有消息元素
    const messageBlocks = chatContainer.querySelectorAll('.chat-message');
    if (messageBlocks.length === 0) return null;
    
    // 提取消息内容
    const messages = Array.from(messageBlocks).map(block => {
      // 判断消息角色
      const isUser = block.classList.contains('user-message');
      const role = isUser ? 'user' : 'assistant';
      
      // 获取消息内容
      const contentElement = block.querySelector('.message-content');
      const content = contentElement ? contentElement.textContent.trim() : '';
      
      return { role, content };
    });
    
    return {
      platform: 'DeepSeek',
      timestamp: new Date().toISOString(),
      messages: messages
    };
  } catch (error) {
    console.error('提取DeepSeek对话时出错:', error);
    return null;
  }
}

// 提取Monica对话
function extractMonica() {
  try {
    // 查找对话容器 (根据Monica的DOM结构调整选择器)
    const chatContainer = document.querySelector('.conversation-container');
    if (!chatContainer) return null;
    
    // 获取所有消息元素
    const messageElements = chatContainer.querySelectorAll('.message-item');
    if (messageElements.length === 0) return null;
    
    // 提取消息内容
    const messages = Array.from(messageElements).map(element => {
      // 判断消息角色
      const isUser = element.classList.contains('user-message');
      const role = isUser ? 'user' : 'assistant';
      
      // 获取消息内容
      const contentElement = element.querySelector('.message-text');
      const content = contentElement ? contentElement.textContent.trim() : '';
      
      return { role, content };
    });
    
    return {
      platform: 'Monica',
      timestamp: new Date().toISOString(),
      messages: messages
    };
  } catch (error) {
    console.error('提取Monica对话时出错:', error);
    return null;
  }
}

// 添加消息提示，显示在页面右上角
function showNotification(message, isSuccess = true) {
  // 创建通知元素
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background-color: ${isSuccess ? '#4caf50' : '#f44336'};
    color: white;
    border-radius: 4px;
    z-index: 10000;
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    transition: opacity 0.3s ease-in-out;
  `;
  
  // 添加到页面
  document.body.appendChild(notification);
  
  // 3秒后移除
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// 初始化通知信息
console.log('AI对话记忆器已加载'); 