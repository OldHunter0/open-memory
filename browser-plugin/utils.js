// 不再导入外部库
// import FingerprintJS from '@fingerprintjs/fingerprintjs';

// 获取用户唯一ID
export const getUserId = async () => {
  try {
    // 先从chrome存储中获取用户ID，使用与前端一致的键名
    const result = await chrome.storage.sync.get(['itch7_user_id']);
    if (result.itch7_user_id) {
      return result.itch7_user_id;
    }

    // 如果没有存储的ID，生成一个新的（使用内置的generateUserId函数）
    const userId = generateUserId();

    // 存储到chrome存储中以便下次使用，使用与前端一致的键名
    await chrome.storage.sync.set({ itch7_user_id: userId });

    return userId;
  } catch (error) {
    console.error('Error generating user ID:', error);
    // 如果出错，返回随机ID
    const fallbackId = `user_${Math.random().toString(36).substr(2, 9)}`;
    await chrome.storage.sync.set({ itch7_user_id: fallbackId });
    return fallbackId;
  }
};

// 生成唯一的用户ID
function generateUserId() {
  // 生成一个随机的ID，结合当前时间、随机数和一些浏览器信息
  const navigatorInfo = [
    navigator.userAgent,
    navigator.language,
    new Date().getTimezoneOffset()
  ].join('');
  const randomPart = Math.random().toString(36).substring(2, 10);
  const timePart = Date.now().toString(36);
  
  // 简单哈希函数
  let hash = 0;
  for (let i = 0; i < navigatorInfo.length; i++) {
    hash = ((hash << 5) - hash) + navigatorInfo.charCodeAt(i);
    hash |= 0; // 转为32位整数
  }
  
  return `user_${Math.abs(hash).toString(36)}_${timePart}_${randomPart}`;
} 