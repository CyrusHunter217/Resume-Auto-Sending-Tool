# API 代理服务器部署说明

## 什么是 API 代理服务器？

API 代理服务器是一个中间层，位于客户端和 DeepSeek API 之间：
- **客户端** → **代理服务器** → **DeepSeek API**
- API Key 只存储在服务器端，客户端无法看到
- 可以添加访问控制、使用量统计、限流等功能

## 优势

✅ **安全性**：API Key 完全隐藏，客户端无法获取
✅ **控制**：可以限制访问、监控使用量、设置配额
✅ **灵活性**：可以更换 API Key 而不需要更新客户端
✅ **统计**：可以统计每个客户的使用量，便于收费

## 部署步骤

### 方式一：本地部署（开发/测试）

1. **安装依赖**
```bash
pip install -r api_proxy_requirements.txt
```

2. **配置环境变量（可选）**
```bash
# Windows
set DEEPSEEK_API_KEY=sk-你的API-Key
set SERVER_API_KEY=your-server-api-key-here
set PORT=5000

# Linux/Mac
export DEEPSEEK_API_KEY=sk-你的API-Key
export SERVER_API_KEY=your-server-api-key-here
export PORT=5000
```

3. **直接运行**
```bash
python api_proxy_server.py
```

服务器会在 `http://localhost:5000` 启动

### 方式二：服务器部署（生产环境）

#### 使用 Gunicorn（推荐）

1. **安装 Gunicorn**
```bash
pip install gunicorn
```

2. **运行服务器**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_proxy_server:app
```

参数说明：
- `-w 4`: 4个工作进程
- `-b 0.0.0.0:5000`: 绑定到所有网络接口的5000端口

#### 使用 systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/api-proxy.service`：

```ini
[Unit]
Description=DeepSeek API Proxy Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/project
Environment="DEEPSEEK_API_KEY=sk-你的API-Key"
Environment="SERVER_API_KEY=your-server-api-key"
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 api_proxy_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start api-proxy
sudo systemctl enable api-proxy  # 开机自启
```

#### 使用 Docker（推荐）

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY api_proxy_requirements.txt .
RUN pip install --no-cache-dir -r api_proxy_requirements.txt

COPY api_proxy_server.py .

ENV DEEPSEEK_API_KEY=sk-你的API-Key
ENV SERVER_API_KEY=your-server-api-key
ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_proxy_server:app"]
```

构建和运行：
```bash
docker build -t api-proxy .
docker run -d -p 5000:5000 --name api-proxy api-proxy
```

### 方式三：云服务器部署

#### 使用云服务（如 Heroku、Railway、Render）

1. **Heroku 部署**
```bash
# 安装 Heroku CLI
heroku create your-app-name
heroku config:set DEEPSEEK_API_KEY=sk-你的API-Key
heroku config:set SERVER_API_KEY=your-server-api-key
git push heroku main
```

2. **Railway 部署**
- 连接 GitHub 仓库
- 设置环境变量
- 自动部署

## 配置客户端

### 修改 api_config.json

```json
{
  "api_key": "",
  "use_proxy": true,
  "proxy_url": "http://your-server.com:5000",
  "server_api_key": "your-server-api-key-here"
}
```

参数说明：
- `use_proxy`: 是否使用代理服务器（true/false）
- `proxy_url`: 代理服务器地址
- `server_api_key`: 服务器认证密钥（可选，如果服务器设置了认证）

### 客户端会自动切换

- 如果 `use_proxy: true`，客户端会通过代理服务器调用 API
- 如果 `use_proxy: false`，客户端会直接调用 DeepSeek API

## 安全建议

### 1. 使用 HTTPS

在生产环境，建议使用 HTTPS：
- 使用 Nginx 作为反向代理
- 配置 SSL 证书（Let's Encrypt 免费）

### 2. 设置访问控制

在 `api_proxy_server.py` 中设置 `SERVER_API_KEY`：
- 客户端需要在请求头中提供正确的 `Authorization: Bearer <SERVER_API_KEY>`
- 只有授权的客户端才能使用代理

### 3. 限制访问

可以添加 IP 白名单、请求频率限制等

### 4. 监控和日志

- 使用日志记录所有请求
- 监控 API 使用量
- 设置告警

## 测试代理服务器

### 1. 健康检查
```bash
curl http://localhost:5000/health
```

### 2. 测试 API 调用
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### 3. 查看统计（需要认证）
```bash
curl http://localhost:5000/api/stats \
  -H "Authorization: Bearer your-server-api-key"
```

## 费用控制

### 1. 设置使用限额

可以在服务器端添加：
- 每日请求限制
- 每个客户端的配额
- 自动拒绝超额请求

### 2. 监控使用量

访问 `/api/stats` 端点查看：
- 总请求数
- 总 token 使用量
- 今日请求数

## 常见问题

**Q: 代理服务器会影响性能吗？**
A: 影响很小，只是增加一次网络跳转，通常延迟增加 < 50ms

**Q: 如何更换 API Key？**
A: 只需在服务器端更新环境变量或配置文件，客户端无需修改

**Q: 可以同时支持多个 API Key 吗？**
A: 可以，修改服务器代码，根据客户端标识选择不同的 API Key

**Q: 如何收费？**
A: 可以通过统计每个客户端的使用量，按使用量收费

## 下一步

1. 部署代理服务器到云服务器
2. 配置 HTTPS 和域名
3. 设置访问控制和监控
4. 更新客户端配置使用代理
5. 打包客户端时设置 `use_proxy: true`

