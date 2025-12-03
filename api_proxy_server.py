#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API 代理服务器
功能：作为中间层，隐藏真实的 API Key，客户端通过代理服务器调用 API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量或配置文件读取 API Key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-aa830600ff6b46839da3e59734f82c89')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# API 密钥（用于验证客户端请求，可选）
SERVER_API_KEY = os.getenv('SERVER_API_KEY', 'your-server-api-key-here')

# 使用量统计
usage_stats = {
    'total_requests': 0,
    'total_tokens': 0,
    'requests_today': 0,
    'last_reset_date': datetime.now().strftime('%Y-%m-%d')
}


def reset_daily_stats():
    """重置每日统计"""
    today = datetime.now().strftime('%Y-%m-%d')
    if usage_stats['last_reset_date'] != today:
        usage_stats['requests_today'] = 0
        usage_stats['last_reset_date'] = today


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'API Proxy Server is running'})


@app.route('/api/chat', methods=['POST'])
def chat_completion():
    """
    聊天完成接口（代理 DeepSeek API）
    
    请求体：
    {
        "messages": [...],
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    可选的认证头：
    Authorization: Bearer <SERVER_API_KEY>
    """
    try:
        # 可选：验证客户端 API Key
        auth_header = request.headers.get('Authorization', '')
        if SERVER_API_KEY and SERVER_API_KEY != 'your-server-api-key-here':
            if not auth_header.startswith('Bearer ') or auth_header[7:] != SERVER_API_KEY:
                return jsonify({'error': 'Unauthorized'}), 401
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400
        
        # 构建 DeepSeek API 请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        api_data = {
            "model": data.get('model', 'deepseek-chat'),
            "messages": data.get('messages', []),
            "temperature": data.get('temperature', 0.7),
            "max_tokens": data.get('max_tokens', 2000)
        }
        
        # 调用 DeepSeek API
        logger.info(f"Proxying request to DeepSeek API: {api_data.get('model')}")
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=api_data,
            timeout=60
        )
        
        # 更新统计
        reset_daily_stats()
        usage_stats['total_requests'] += 1
        usage_stats['requests_today'] += 1
        
        if response.status_code == 200:
            result = response.json()
            # 统计 token 使用量
            if 'usage' in result:
                usage_stats['total_tokens'] += result['usage'].get('total_tokens', 0)
            
            logger.info(f"Request successful. Total requests: {usage_stats['total_requests']}")
            return jsonify(result)
        else:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
            return jsonify({
                'error': 'API request failed',
                'status_code': response.status_code,
                'message': response.text
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取使用统计（需要认证）"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != SERVER_API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reset_daily_stats()
    return jsonify(usage_stats)


@app.route('/api/reset-stats', methods=['POST'])
def reset_stats():
    """重置统计（需要认证）"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != SERVER_API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    
    usage_stats['total_requests'] = 0
    usage_stats['total_tokens'] = 0
    usage_stats['requests_today'] = 0
    usage_stats['last_reset_date'] = datetime.now().strftime('%Y-%m-%d')
    
    return jsonify({'message': 'Stats reset successfully'})


if __name__ == '__main__':
    # 从环境变量读取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting API Proxy Server on {host}:{port}")
    logger.info(f"DeepSeek API Key: {DEEPSEEK_API_KEY[:10]}...")
    
    app.run(host=host, port=port, debug=debug)

