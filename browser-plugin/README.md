# OpenMemory浏览器插件

这个Chrome浏览器插件用于在访问ChatGPT、DeepSeek、Monica等AI聊天平台时，将对话内容上传到OpenMemory中。

## 功能特点

- 支持从多个AI聊天平台提取对话内容
- 将对话内容上传到OpenMemory上用户的记忆库中
- 可定制API地址和用户ID
- 简洁直观的用户界面

## 支持的AI平台

- ChatGPT (chat.openai.com)
- DeepSeek (chat.deepseek.com)
- Monica (chat.monica.im)

## 安装方法

### 开发模式安装

1. 下载本插件代码
2. 打开Chrome浏览器，进入扩展管理页面 (chrome://extensions/)
3. 开启"开发者模式"（右上角）
4. 点击"加载已解压的扩展程序"
5. 选择本插件的文件夹

### 从商店安装

*该插件尚未上架Chrome商店*

## 使用方法

1. 访问任意支持的AI聊天平台（ChatGPT、DeepSeek或Monica）
2. 进行正常对话
3. 点击浏览器工具栏中的插件图标
4. 输入您的用户ID和API地址（默认为http://localhost:5000）
5. 点击"保存对话到记忆"按钮

## 运行要求

- 后端API服务需要正常运行
- 确保API地址可从浏览器访问（考虑跨域问题）

## 隐私说明

- 本插件仅在用户主动点击保存按钮时提取对话内容
- 所有数据仅保存在指定的API服务器上
- 不会收集或传输其他个人信息

## 开发信息

- 插件版本: 1.0
- 许可协议: MIT 