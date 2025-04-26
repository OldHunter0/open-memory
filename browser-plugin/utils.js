// 不再导入外部库
// import FingerprintJS from '@fingerprintjs/fingerprintjs';

// 获取用户唯一ID - 无需网络请求的版本
export const getUserId = async () => {
  try {
    // 先从chrome存储中获取用户ID
    const result = await chrome.storage.sync.get(['itch7_user_id']);
    if (result.itch7_user_id) {
      console.log("从存储中获取到用户ID:", result.itch7_user_id);
      return result.itch7_user_id;
    }

    // 如果没有存储的ID，生成一个新的，不依赖网络请求
    const userId = generateUserId();
    console.log("生成新的用户ID:", userId);

    // 存储到chrome存储中以便下次使用
    await chrome.storage.sync.set({ itch7_user_id: userId });

    return userId;
  } catch (error) {
    console.error('生成用户ID时出错:', error);
    // 简单的备用方案，不抛出错误
    const fallbackId = `user_${Math.random().toString(36).substring(2, 9)}`;
    console.log("使用备用用户ID:", fallbackId);
    try {
      await chrome.storage.sync.set({ itch7_user_id: fallbackId });
    } catch (storageError) {
      console.error("保存备用ID到存储失败:", storageError);
    }
    return fallbackId;
  }
};

// 生成唯一的用户ID - 纯本地方法，不依赖网络
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