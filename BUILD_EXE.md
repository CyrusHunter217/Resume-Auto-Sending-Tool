# 打包成 EXE 文件说明

## 使用 PyInstaller 打包

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包命令

```bash
pyinstaller --onefile --windowed --name="JobsDB自动求职工具" --icon=icon.ico jobsdb_ai_tool.py
```

参数说明：
- `--onefile`: 打包成单个exe文件
- `--windowed`: 不显示控制台窗口（GUI程序）
- `--name`: 指定生成的exe文件名
- `--icon`: 指定图标文件（可选）

### 3. 完整打包命令（包含所有依赖）

```bash
pyinstaller --onefile --windowed ^
    --name="JobsDB自动求职工具" ^
    --add-data="config.json;." ^
    --hidden-import=selenium ^
    --hidden-import=bs4 ^
    --hidden-import=fpdf ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=docx ^
    jobsdb_ai_tool.py
```

### 4. 打包后的文件结构

打包完成后，会在 `dist` 目录下生成：
- `JobsDB自动求职工具.exe` - 主程序文件

### 5. 配置文件处理

**重要**：打包后的exe需要 `config.json` 文件才能保存配置。

**方案一**：将 `config.json` 放在exe同目录下
- 首次运行会自动创建空的 `config.json`
- 用户通过GUI输入API Key后会自动保存

**方案二**：在打包时包含默认的 `config.json`（不包含API Key）
```json
{
  "api_key": "",
  "resume_content": "",
  "search_keyword": "Administrative Officer",
  "search_location": "Hong Kong",
  "match_threshold": 70,
  "region": "香港 (hk)",
  "language": "zh"
}
```

## API Key 安全说明

✅ **安全**：
- 代码中**没有**硬编码的API Key
- API Key只能通过GUI输入框或config.json配置
- config.json不会被推送到GitHub（已在.gitignore中）

⚠️ **注意事项**：
- 打包成exe后，用户需要首次运行时在GUI中输入API Key
- API Key会保存在exe同目录下的 `config.json` 文件中
- 建议提醒用户妥善保管 `config.json` 文件

## 分发给客户

1. 将 `JobsDB自动求职工具.exe` 和 `config.json`（可选，空文件即可）一起打包
2. 提供使用说明：
   - 首次运行需要在「初始化配置」标签页输入DeepSeek API Key
   - API Key会保存在同目录下的 `config.json` 文件中
   - 不要将 `config.json` 分享给他人

## 测试打包后的exe

1. 在干净的Windows系统上测试
2. 确保没有安装Python环境也能运行
3. 测试所有功能是否正常
4. 检查配置文件是否能正常保存和加载

