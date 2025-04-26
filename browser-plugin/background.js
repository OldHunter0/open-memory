import { getUserId } from './utils.js';

// 扩展程序安装或更新时的处理
chrome.runtime.onInstalled.addListener(async function(details) {
  if (details.reason === 'install') {
    // 首次安装时的处理
    console.log('OpenMemory已安装');
    
    // 设置默认值
    chrome.storage.sync.set({
      apiUrl: 'http://localhost:5000'
    });
    
    // 生成并保存userId，使用与前端一致的键名
    await getUserId();
  } else if (details.reason === 'update') {
    // 更新时的处理
    console.log(`OpenMemory已更新到版本 ${chrome.runtime.getManifest().version}`);
  }
});

// 接收来自popup或content脚本的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'saveConversation') {
    // 处理保存对话请求
    saveConversationToAPI(request.data, sendResponse);
    return true; // 保持消息通道开放，异步响应
  }
});

// 保存对话数据到API
function saveConversationToAPI(data, callback) {
  const { apiUrl, userId, messages, platform } = data;
  
  if (!apiUrl || !userId || !messages) {
    callback({success: false, error: '参数不完整'});
    return;
  }
  
  // 准备请求数据
  const requestData = {
    user_id: userId,
    messages: messages,
    platform: platform || 'unknown'
  };
  
  // 发送API请求到新端点
  fetch(`${apiUrl}/api/update_memory_from_chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      callback({success: true, message: data.message});
    } else {
      callback({success: false, error: data.error || '未知错误'});
    }
  })
  .catch(error => {
    callback({success: false, error: error.message});
  });
}

// 扩展图标点击事件
chrome.action.onClicked.addListener(function(tab) {
  // 检查是否在支持的网站上
  const url = tab.url || '';
  
  if (
    url.includes('chat.openai.com') || 
    url.includes('chatgpt.com') ||
    url.includes('oai.liuliangbang.vip') ||
    url.includes('chat.deepseek.com') || 
    url.includes('chat.monica.im')
  ) {
    // 如果在支持的网站上，会自动打开popup.html
    // 这里不需要额外处理
  } else {
    // 如果不在支持的网站上，可以提醒用户
    chrome.tabs.sendMessage(tab.id, {
      action: 'showNotification',
      message: '此网站不支持OpenMemory',
      isSuccess: false
    });
  }
}); 