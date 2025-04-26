// 当弹出窗口加载时执行
document.addEventListener('DOMContentLoaded', function() {
  // 从存储中加载设置
  chrome.storage.sync.get(['userId', 'apiUrl'], function(items) {
    if (items.userId) {
      document.getElementById('userId').value = items.userId;
    }
    if (items.apiUrl) {
      document.getElementById('apiUrl').value = items.apiUrl;
    } else {
      // 默认API地址
      document.getElementById('apiUrl').value = 'http://localhost:5000';
    }
  });

  // 获取当前活跃标签页的对话信息
  getCurrentTabInfo();

  // 添加保存按钮点击事件
  document.getElementById('saveButton').addEventListener('click', saveConversation);
});

// 获取当前标签页信息
function getCurrentTabInfo() {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs.length === 0) return;
    
    const currentTab = tabs[0];
    
    // 检查是否在支持的网站上
    const url = currentTab.url;
    let platform = '';
    
    if (url.includes('chat.openai.com')) {
      platform = 'ChatGPT';
    } else if (url.includes('chat.deepseek.com')) {
      platform = 'DeepSeek';
    } else if (url.includes('chat.monica.im')) {
      platform = 'Monica';
    } else {
      document.getElementById('conversationInfo').textContent = '不支持的网站';
      document.getElementById('saveButton').disabled = true;
      return;
    }
    
    // 向内容脚本发送消息，请求对话数据
    chrome.tabs.sendMessage(currentTab.id, {action: 'getConversation'}, function(response) {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        document.getElementById('conversationInfo').textContent = 
          `无法获取${platform}对话: ${chrome.runtime.lastError.message}`;
        return;
      }
      
      if (!response || !response.success) {
        document.getElementById('conversationInfo').textContent = 
          `无法获取${platform}对话`;
        return;
      }
      
      // 更新对话信息显示
      const messageCount = response.conversationData.messages.length;
      document.getElementById('conversationInfo').textContent = 
        `平台: ${platform}\n消息数: ${messageCount}`;
      
      // 在全局存储对话数据，以便保存按钮使用
      window.conversationData = response.conversationData;
    });
  });
}

// 保存对话到API
function saveConversation() {
  // 获取用户ID和API URL
  const userId = document.getElementById('userId').value.trim();
  const apiUrl = document.getElementById('apiUrl').value.trim();
  
  // 验证输入
  if (!userId) {
    showStatus('请输入用户ID', false);
    return;
  }
  
  if (!apiUrl) {
    showStatus('请输入API地址', false);
    return;
  }
  
  if (!window.conversationData) {
    showStatus('未检测到对话数据', false);
    return;
  }
  
  // 保存设置到存储
  chrome.storage.sync.set({
    userId: userId,
    apiUrl: apiUrl
  });
  
  // 准备请求数据
  const requestData = {
    user_id: userId,
    messages: window.conversationData.messages
  };
  
  // 发送请求到API
  fetch(`${apiUrl}/api/save_episodic_memory`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      showStatus('对话已成功保存到记忆', true);
    } else {
      showStatus(`保存失败: ${data.error || '未知错误'}`, false);
    }
  })
  .catch(error => {
    showStatus(`API请求错误: ${error.message}`, false);
  });
}

// 显示状态消息
function showStatus(message, isSuccess) {
  const statusElement = document.getElementById('statusMessage');
  statusElement.textContent = message;
  statusElement.className = 'status ' + (isSuccess ? 'success' : 'error');
  statusElement.style.display = 'block';
  
  // 3秒后隐藏消息
  setTimeout(() => {
    statusElement.style.display = 'none';
  }, 3000);
} 