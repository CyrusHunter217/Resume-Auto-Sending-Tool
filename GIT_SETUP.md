# Git 仓库设置说明

Git 仓库已成功初始化并创建了初始提交。

## 推送到 GitHub

### 步骤 1：在 GitHub 上创建新仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 输入仓库名称（例如：`jobsdb-auto-apply`）
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
6. 点击 "Create repository"

### 步骤 2：连接本地仓库到 GitHub

在项目目录下运行以下命令（将 `<your-username>` 和 `<repository-name>` 替换为你的实际信息）：

```bash
git remote add origin https://github.com/<your-username>/<repository-name>.git
git branch -M main
git push -u origin main
```

### 示例

如果你的 GitHub 用户名是 `john`，仓库名是 `jobsdb-auto-apply`，则运行：

```bash
git remote add origin https://github.com/john/jobsdb-auto-apply.git
git branch -M main
git push -u origin main
```

### 使用 SSH（可选）

如果你配置了 SSH 密钥，可以使用 SSH URL：

```bash
git remote add origin git@github.com:<your-username>/<repository-name>.git
git branch -M main
git push -u origin main
```

## 后续更新

以后每次修改代码后，使用以下命令提交和推送：

```bash
git add .
git commit -m "描述你的更改"
git push
```

## 注意事项

- `config.json` 文件已添加到 `.gitignore`，不会被推送到 GitHub（保护你的 API Key）
- `application_records.json` 也不会被推送（保护隐私）
- 如果 GitHub 要求身份验证，请使用 Personal Access Token 而不是密码

