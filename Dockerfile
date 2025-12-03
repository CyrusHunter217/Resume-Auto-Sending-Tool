FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY api_proxy_requirements.txt .
RUN pip install --no-cache-dir -r api_proxy_requirements.txt

# 复制应用代码
COPY api_proxy_server.py .

# 设置环境变量（可以在运行时覆盖）
ENV DEEPSEEK_API_KEY=""
ENV SERVER_API_KEY=""
ENV PORT=5000
ENV HOST=0.0.0.0
ENV DEBUG=False

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "api_proxy_server:app"]

