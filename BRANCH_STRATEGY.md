# 分支策略说明

## 分支结构

### main 分支
- **用途**：生产环境代码，稳定版本
- **保护规则**：
  - 不允许直接push
  - 必须通过Pull Request合并
  - 需要代码审查（单人开发可自审）
  - 必须通过CI检查

### dev 分支
- **用途**：开发分支，用于日常开发
- **规则**：
  - 可以自由push
  - 新功能在此分支开发
  - 测试通过后合并到main

## 工作流程

### 开发新功能
1. 从 `dev` 分支创建功能分支：`git checkout -b feature/功能名称`
2. 开发完成后提交：`git commit -m "feat: 功能描述"`
3. 推送到远程：`git push origin feature/功能名称`
4. 创建Pull Request合并到 `dev`
5. 测试通过后，从 `dev` 合并到 `main`

### 修复Bug
1. 从 `dev` 分支创建修复分支：`git checkout -b fix/bug描述`
2. 修复完成后提交：`git commit -m "fix: bug描述"`
3. 推送到远程并创建Pull Request

### 发布版本
1. 在 `main` 分支创建标签：`git tag -a v1.0.0 -m "版本说明"`
2. 推送标签：`git push origin v1.0.0`

## 提交信息规范

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

## GitHub设置建议

### 分支保护规则（在GitHub网页设置）

1. 进入仓库 Settings → Branches
2. 为 `main` 分支添加规则：
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1个，可以是自己)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### 标签保护（可选）
- 为重要标签添加保护，防止误删

