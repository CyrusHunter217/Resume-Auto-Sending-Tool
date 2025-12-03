# DeepSeek API Key 配置说明

## 方式一：在代码文件中直接配置（推荐用于快速测试）

打开 `jobsdb_ai_tool.py` 文件，找到文件顶部的配置区域（大约在第 165-170 行），修改以下变量：

```python
# ==================== 配置区域 ====================
# 在这里填入你的 DeepSeek API Key
DEEPSEEK_API_KEY = "sk-你的API-Key-在这里"  # 请替换为你的实际 API Key
```

**优点**：简单直接，适合个人使用  
**缺点**：如果推送到GitHub，API Key会暴露（但已添加到.gitignore，不会被推送）

## 方式二：通过GUI界面配置（推荐用于日常使用）

1. 运行程序
2. 在「API Configuration」区域输入你的 API Key
3. 程序会自动保存到 `config.json` 文件
4. 下次启动时会自动加载

**优点**：更安全，不会在代码中暴露  
**缺点**：需要每次手动输入（如果清除缓存）

## 方式三：在 config.json 文件中配置

直接编辑 `config.json` 文件，添加或修改：

```json
{
  "api_key": "sk-你的API-Key-在这里",
  ...
}
```

**注意**：`config.json` 已添加到 `.gitignore`，不会被推送到GitHub，可以安全保存API Key。

## 获取 DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 API Key 并按照上述方式之一配置

## 安全提示

- ⚠️ **不要**将包含真实 API Key 的代码推送到公开的 GitHub 仓库
- ✅ `config.json` 和代码中的 API Key 变量已添加到 `.gitignore`
- ✅ 建议使用方式二或方式三，更安全

