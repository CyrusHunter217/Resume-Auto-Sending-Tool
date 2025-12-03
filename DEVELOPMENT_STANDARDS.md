# 开发标准文档

本文档定义了项目的开发标准、代码规范和最佳实践。**所有新对话都应该先阅读此文档**。

## 项目概述

**项目名称**：JobsDB 自动求职工具  
**技术栈**：Python 3.7+, Tkinter, Selenium, DeepSeek API  
**仓库地址**：https://github.com/CyrusHunter217/Resume-Auto-Sending-Tool

## 代码规范

### 1. 语言和编码
- **界面语言**：默认中文，支持中英文切换
- **代码注释**：中文注释
- **变量命名**：英文，使用下划线命名法（snake_case）
- **文件编码**：UTF-8

### 2. GUI界面规范
- **使用 `ttk.Notebook` 将界面分为4个标签页**：
  1. 初始化配置
  2. 全自动求职
  3. 手动单岗处理
  4. 投递记录查询

- **界面文字要求**：
  - ✅ 所有UI文字必须使用 `self.texts` 字典，支持中英文切换
  - ✅ 使用纯中文，避免英文混杂（如"Job Link"应改为"岗位链接"）
  - ✅ 按钮文字要通俗易懂（如"开始全自动求职"而非"Start Auto Search & Apply"）
  - ❌ 禁止硬编码文字，必须通过 `get_texts()` 函数获取

- **界面元素分组**：
  - 使用 `ttk.LabelFrame` 对相关元素进行分组
  - 每个分组要有清晰的标题
  - 重要输入框旁边要有提示文字（如"必填"）

- **按钮样式**：
  - 核心操作按钮使用高亮样式（蓝色背景 `#4A90E2`，白色文字，粗体）
  - 普通按钮使用默认 `ttk.Button` 样式

### 3. 功能实现规范

#### 3.1 配置管理
- 配置文件：`config.json`（用户配置，不提交到Git）
- API配置：`api_config.json`（可选，不提交到Git）
- 所有配置必须支持保存和加载
- 配置变更后自动保存

#### 3.2 多线程处理
- **所有耗时操作必须使用线程**，避免GUI冻结
- 使用 `threading.Thread(target=worker, daemon=True)`
- UI更新使用 `self.root.after(0, lambda: ...)`

#### 3.3 错误处理
- 所有网络请求、文件操作都要有 try-except
- 错误信息要友好，使用 `messagebox.showerror()`
- 记录错误日志到控制台

#### 3.4 文件管理
- 数据文件：
  - `application_records.json`：投递记录
  - `resume_cache.txt`：简历缓存
  - 这些文件不提交到Git（已在.gitignore中）

### 4. 代码结构规范

#### 4.1 类结构
```python
class ResumeGeneratorApp:
    def __init__(self, root):
        # 1. 初始化变量
        # 2. 加载配置
        # 3. 创建界面
        # 4. 设置自动保存
    
    def get_texts(self, lang="zh"):
        # 返回界面文字字典
    
    def create_widgets(self):
        # 创建主界面
    
    def create_tab_init(self):
        # 创建标签1：初始化配置
    
    def create_tab_auto(self):
        # 创建标签2：全自动求职
    
    def create_tab_manual(self):
        # 创建标签3：手动单岗处理
    
    def create_tab_records(self):
        # 创建标签4：投递记录查询
```

#### 4.2 函数命名
- GUI事件处理：`on_xxx_click()`
- 核心功能：`generate_custom_resume()`, `auto_apply_job()` 等
- 辅助函数：`update_status()`, `save_config()` 等

#### 4.3 导入顺序
1. 标准库
2. 第三方库
3. 本地模块

### 5. Git工作流规范

#### 5.1 分支策略
- `main`：生产环境，稳定版本（受保护）
- `dev`：开发分支，日常开发
- `feature/xxx`：功能分支
- `fix/xxx`：Bug修复分支

#### 5.2 提交信息规范
使用约定式提交（Conventional Commits）：
- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加自动投递功能
fix: 修复简历生成错误
docs: 更新README说明
```

#### 5.3 提交前检查
- 代码能正常运行
- 没有语法错误
- 已更新相关文档（如需要）

### 6. 依赖管理

#### 6.1 依赖文件
- `requirements.txt`：列出所有Python依赖
- 版本号要明确（如 `selenium>=4.0.0`）

#### 6.2 新增依赖
- 添加新依赖后必须更新 `requirements.txt`
- 在提交信息中说明新增依赖的原因

### 7. 文档规范

#### 7.1 必须维护的文档
- `README.md`：项目说明和使用指南
- `DEVELOPMENT_STANDARDS.md`：本文档（开发标准）
- `BRANCH_STRATEGY.md`：分支策略说明

#### 7.2 代码注释
- 函数要有docstring说明功能、参数、返回值
- 复杂逻辑要有行内注释

### 8. 测试规范

#### 8.1 测试要求
- 新功能开发后要手动测试
- 确保GUI界面正常显示
- 确保核心功能正常工作

#### 8.2 测试清单
- [ ] 界面文字正确显示
- [ ] 中英文切换正常
- [ ] 配置保存和加载正常
- [ ] 核心功能（抓取、生成、投递）正常

### 9. 特殊要求

#### 9.1 简历语言
- 生成的简历语言应该与原始简历语言一致，或由用户选择
- 支持自动检测（auto）、中文（zh）、英文（en）

#### 9.2 投递频率控制
- 每日最多投递15个
- 两次投递间隔6-12分钟（随机）
- 支持暂停/继续功能

#### 9.3 Chrome浏览器配置
- 支持使用已登录的Chrome配置文件
- 自动检测Chrome用户数据目录
- 支持手动选择配置文件

## 开发流程

### 开发新功能
1. 从 `dev` 分支创建功能分支
2. 按照代码规范开发
3. 更新相关文档
4. 测试功能
5. 提交代码（使用规范提交信息）
6. 创建PR合并到 `dev`
7. 测试通过后合并到 `main`

### 修复Bug
1. 从 `dev` 分支创建修复分支
2. 修复问题
3. 测试修复
4. 提交代码
5. 创建PR合并

## 注意事项

1. **不要硬编码文字**：所有UI文字必须通过 `get_texts()` 获取
2. **不要阻塞GUI**：耗时操作必须使用线程
3. **不要提交敏感信息**：API Key、配置文件等已在.gitignore中
4. **保持代码整洁**：遵循PEP 8规范
5. **及时更新文档**：功能变更后更新相关文档

## 参考资源

- [PEP 8 - Python代码风格指南](https://pep8.org/)
- [约定式提交](https://www.conventionalcommits.org/)
- [Git工作流](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

**最后更新**：2025-01-XX  
**维护者**：项目开发者

