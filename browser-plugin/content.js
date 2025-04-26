// 监听来自弹出窗口的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'getConversation') {
    const host = window.location.host;
    let conversationData = null;
    
    // 根据不同的网站调用不同的提取方法
    if (host.includes('chatgpt.com')) {
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
    console.log("正在提取ChatGPT对话...");
    
    // 打印页面上的whitespace-pre-wrap元素内容，帮助调试
    const preWrapElements = document.querySelectorAll('.whitespace-pre-wrap');
    console.log(`找到 ${preWrapElements.length} 个whitespace-pre-wrap元素`);
    preWrapElements.forEach((el, i) => {
      console.log(`whitespace-pre-wrap元素 #${i+1}: "${el.textContent}"`);
    });
    
    // 查找对话消息容器
    let messageContainers = [];
    
    // 新版ChatGPT使用的特定类
    const chatItems = document.querySelectorAll('div[class*="chat-message"], div[class*="conversation-turn"]');
    if (chatItems && chatItems.length > 0) {
      console.log(`找到 ${chatItems.length} 个聊天消息容器`);
      messageContainers = Array.from(chatItems);
    }
    
    // 如果没找到，尝试寻找包含whitespace-pre-wrap的父元素
    if (messageContainers.length === 0 && preWrapElements.length > 0) {
      console.log("尝试通过whitespace-pre-wrap元素查找消息容器");
      
      // 为每个whitespace-pre-wrap元素找到合适的父容器
      preWrapElements.forEach(el => {
        // 向上查找3-4级，寻找可能的消息容器
        let parent = el.parentElement;
        for (let i = 0; i < 4 && parent; i++) {
          if (parent.offsetHeight > 40 && 
              (parent.classList.length > 0 || parent.getAttribute('role'))) {
            if (!messageContainers.includes(parent)) {
              messageContainers.push(parent);
            }
            break;
          }
          parent = parent.parentElement;
        }
      });
      console.log(`通过whitespace-pre-wrap找到 ${messageContainers.length} 个可能的消息容器`);
    }
    
    // 如果仍然没找到，尝试其他通用方法
    if (messageContainers.length === 0) {
      // 尝试旧版界面 (chat.openai.com)
      const threadContainer = document.querySelector('div[data-testid="conversation-thread"]');
      if (threadContainer) {
        const oldMessages = threadContainer.querySelectorAll('[data-message-author-role]');
        if (oldMessages && oldMessages.length > 0) {
          messageContainers = Array.from(oldMessages);
        }
      }
      
      // 如果还是找不到消息元素，返回null
      if (messageContainers.length === 0) {
        console.error("无法找到ChatGPT消息元素");
        return null;
      }
    }
    
    // 从找到的容器中提取消息
    const messages = [];
    messageContainers.forEach((container, index) => {
      // 默认基于顺序推断角色
      let role = index % 2 === 0 ? 'user' : 'assistant';
      
      // 尝试通过类名或属性确定更准确的角色
      if (container.classList.contains('user') || 
          container.getAttribute('data-message-author-role') === 'user' ||
          container.querySelector('[aria-label*="user"]')) {
        role = 'user';
      } else if (container.classList.contains('assistant') || 
                container.getAttribute('data-message-author-role') === 'assistant' ||
                container.querySelector('[aria-label*="assistant"]')) {
        role = 'assistant';  
      }
      
      // 修改提取内容的方式，获取完整的HTML内容
      let contentElement;
      
      // 首先查找markdown内容容器
      contentElement = container.querySelector('.markdown.prose');
      
      // 如果没找到，尝试其他选择器
      if (!contentElement) {
        contentElement = container.querySelector('.whitespace-pre-wrap') ||
                         container.querySelector('[data-message-text-content="true"]') ||
                         container.querySelector('p') ||
                         container.querySelector('[class*="content"]') ||
                         container;
      }
      
      // 如果还是没有，使用容器本身
      if (!contentElement) {
        contentElement = container;
      }
      
      const content = contentElement.textContent.trim();
      
      // 记录详细信息
      console.log(`消息 #${index+1}:`);
      console.log(`- 角色: ${role}`);
      console.log(`- 内容: "${content.substring(0, 100)}${content.length > 300 ? '...' : ''}"`);
      console.log(`- 元素类名: ${container.className}`);
      console.log(`- 内容元素类名: ${contentElement.className}`);
      
      if (content && content.length > 0) {
        messages.push({ role, content });
      }
    });
    
    if (messages.length === 0) {
      console.error("提取的消息内容为空");
      return null;
    }
    
    console.log(`成功提取ChatGPT对话，共${messages.length}条消息`);
    return {
      messages: messages,
      platform: 'ChatGPT'
    };
  } catch (error) {
    console.error('提取ChatGPT对话时出错:', error);
    return null;
  }
}

// 提取DeepSeek对话内容
function extractDeepSeek() {
  try {
    console.log("正在提取DeepSeek对话...");
    
    // DeepSeek使用React，内容会在JS加载后渲染
    // 需要等待DOM完全加载并渲染
    
    // 首先尝试找出所有可能包含对话的区域
    const mainContent = document.querySelector('#root') || document.body;
    console.log("找到主容器:", mainContent);
    
    // 查找对话区域 - DeepSeek经常使用flex布局
    const possibleChatContainers = Array.from(
      mainContent.querySelectorAll('div[class*="chat"], div[class*="message"], main, [role="main"]')
    ).filter(el => el.offsetHeight > 200); // 只考虑有足够高度的容器
    
    console.log(`找到${possibleChatContainers.length}个可能的对话容器`);
    
    // 尝试在各个可能的容器中查找消息
    let messages = [];
    let chatContainer = null;
    
    for (const container of possibleChatContainers) {
      // 查找可能的消息元素
      const potentialMessages = Array.from(
        container.querySelectorAll('div[class*="flex"]')
      ).filter(el => {
        // 消息通常有一定的高度和宽度
        return el.offsetHeight > 30 && el.offsetWidth > 200 && 
               // 通常包含文本内容
               el.textContent.trim().length > 10 &&
               // 图像元素通常表示用户或AI头像
               (el.querySelector('img') || el.querySelector('svg'));
      });
      
      if (potentialMessages.length >= 2) { // 至少应有一问一答
        chatContainer = container;
        console.log(`在容器中找到${potentialMessages.length}个潜在消息`);
        
        // 提取消息内容
        messages = potentialMessages.map((el, index) => {
          // 检测是否为用户消息
          // DeepSeek通常在右侧放置用户消息或使用特定图标
          const isUser = index % 2 === 0; // 简单假设奇偶交替为用户和AI
          
          // 清理HTML并提取文本
          const content = el.textContent.trim()
            .replace(/^复制$|^复制代码$/gm, '') // 移除"复制"按钮文本
            .replace(/^\s*\d+\/\d+\s*$/gm, ''); // 移除分页指示器
            
          // 打印每段对话的详细信息
          console.log(`消息 #${index+1}:`);
          console.log(`- 角色: ${isUser ? "用户" : "AI助手"}`);
          console.log(`- 内容预览: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`);
          console.log(`- 内容长度: ${content.length}字符`);
          console.log(`- HTML元素高度: ${el.offsetHeight}px, 宽度: ${el.offsetWidth}px`);
          console.log(`- 子元素数量: ${el.childElementCount}`);
          
          // 检查这是否可能是UI元素而非实际对话
          if (content.length < 20 || /^(复制|复制代码|继续生成|重新生成)$/.test(content)) {
            console.log(`- 警告: 这可能是UI元素而非实际对话内容`);
          }
          console.log('----------------------------');
          
          return {
            role: isUser ? "user" : "assistant",
            content: content
          };
        });
        
        break; // 找到消息后退出循环
      }
    }
    
    // 如果没有找到消息，尝试更通用的方法
    if (messages.length === 0) {
      console.log("尝试备用提取方法...");
      
      // 提取页面上所有可能的文本块
      const textBlocks = Array.from(
        document.querySelectorAll('p, div[class*="text"], pre, code')
      ).filter(el => {
        const text = el.textContent.trim();
        return text.length > 20 && text.length < 2000;
      });
      
      if (textBlocks.length >= 2) {
        console.log(`找到${textBlocks.length}个文本块`);
        
        // 推断对话模式
        messages = textBlocks.map((el, index) => {
          return {
            role: index % 2 === 0 ? "user" : "assistant",
            content: el.textContent.trim()
          };
        });
        console.log(messages);
      }
    }
    
    // 记录调试信息
    if (messages.length === 0) {
      console.error("未能提取任何DeepSeek消息");
      
      // 收集调试信息
      const debugInfo = {
        url: window.location.href,
        title: document.title,
        bodyContent: document.body.innerText.substring(0, 500)
      };
      
      console.log("调试信息:", debugInfo);
      return null;
    }
    
    console.log(`成功提取DeepSeek对话，共${messages.length}条消息`);
    return {
      messages: messages,
      platform: "deepseek"
    };
  } catch (error) {
    console.error("提取DeepSeek对话时出错:", error);
    return null;
  }
}

// 添加调试信息收集功能，便于分析问题
function extractDeepSeekDebugInfo() {
  const debugInfo = {
    url: window.location.href,
    containers: {},
    messages: {}
  };
  
  // 记录可能包含消息的容器
  document.querySelectorAll("div").forEach((div, i) => {
    if (div.childElementCount > 3 && div.innerText.length > 100) {
      debugInfo.containers[`container_${i}`] = {
        className: div.className,
        childCount: div.childElementCount,
        textLength: div.innerText.length,
        firstWords: div.innerText.substring(0, 50).replace(/\n/g, " ")
      };
    }
  });
  
  // 返回调试信息，可通过控制台查看
  console.log("DeepSeek网页调试信息:", debugInfo);
  return debugInfo;
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