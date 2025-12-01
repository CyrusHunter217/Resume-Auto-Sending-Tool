#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JobsDB 自动求职工具
功能：自动搜索岗位、生成定制简历、自动投递
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import threading
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fpdf import FPDF
import pandas as pd
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
import webbrowser


class ResumeGeneratorApp:
    """主应用程序类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JobsDB 自动求职工具")
        self.root.geometry("1000x700")
        
        # 初始化变量（需要在load_config之前设置默认值）
        self.language = "zh"  # 默认中文
        self.texts = self.get_texts("zh")
        
        # 初始化变量
        self.is_auto_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # 初始状态为运行
        
        # 存储GUI元素引用（用于语言切换）
        self.ui_labels = {}
        self.ui_buttons = {}
        self.ui_frames = {}
        
        # 加载配置
        self.config_file = "config.json"
        self.load_config()
        
        # 恢复语言设置
        if 'language' in self.config:
            self.language = self.config['language']
            self.texts = self.get_texts(self.language)
        
        # 创建界面
        self.create_widgets()
        
        # 设置自动保存
        self.setup_auto_save()
    
    def get_texts(self, lang="zh"):
        """获取界面文字（中英文）"""
        texts_zh = {
            'app_title': 'JobsDB 自动求职工具',
            'tab_init': '1. 初始化配置',
            'tab_auto': '2. 全自动求职',
            'tab_manual': '3. 手动单岗处理',
            'tab_records': '4. 投递记录查询',
            'frame_api': 'API密钥配置',
            'frame_browser': '浏览器登录状态',
            'frame_user_info': '个人投递信息',
            'label_api_key': 'DeepSeek API Key：',
            'label_api_required': '必填',
            'label_chrome_profile': 'Chrome用户数据目录（可选）：',
            'label_chrome_profile_name': '配置文件名称：',
            'label_user_name': '姓名：',
            'label_user_email': '邮箱：',
            'label_user_phone': '电话：',
            'label_region': '地区选择：',
            'label_keyword': '搜索关键词：',
            'label_location': '搜索地点：',
            'label_threshold': '匹配度阈值：',
            'label_job_url': '岗位链接：',
            'label_job_description': '岗位描述：',
            'label_resume': '原始简历：',
            'label_resume_language': '简历语言：',
            'label_resume_language_auto': '自动检测',
            'button_open_website': '打开目标网站',
            'button_start_auto': '开始全自动求职',
            'button_pause': '暂停',
            'button_resume': '继续',
            'button_fetch_job': '抓取岗位信息',
            'button_generate': '生成定制简历',
            'button_export_pdf': '导出PDF',
            'button_export_records': '导出记录',
            'button_upload_word': '上传Word简历',
            'button_preview': '预览简历',
            'button_clear': '清空',
            'hint_auto_steps': '步骤：先完成「初始化配置」→ 上传简历 → 点击开始',
            'status_ready': '就绪',
            'warning': '警告',
            'error': '错误',
            'success': '成功',
            'confirm': '确认',
        }
        
        texts_en = {
            'app_title': 'JobsDB Auto Job Application Tool',
            'tab_init': '1. Initial Setup',
            'tab_auto': '2. Auto Job Search',
            'tab_manual': '3. Manual Single Job',
            'tab_records': '4. Application Records',
            'frame_api': 'API Key Configuration',
            'frame_browser': 'Browser Login Status',
            'frame_user_info': 'Personal Information',
            'label_api_key': 'DeepSeek API Key:',
            'label_api_required': 'Required',
            'label_chrome_profile': 'Chrome User Data Dir (Optional):',
            'label_chrome_profile_name': 'Profile Name:',
            'label_user_name': 'Name:',
            'label_user_email': 'Email:',
            'label_user_phone': 'Phone:',
            'label_region': 'Region:',
            'label_keyword': 'Search Keyword:',
            'label_location': 'Search Location:',
            'label_threshold': 'Match Threshold:',
            'label_job_url': 'Job Link:',
            'label_job_description': 'Job Description:',
            'label_resume': 'Original Resume:',
            'label_resume_language': 'Resume Language:',
            'label_resume_language_auto': 'Auto-detect',
            'button_open_website': 'Open Target Website',
            'button_start_auto': 'Start Auto Job Search',
            'button_pause': 'Pause',
            'button_resume': 'Resume',
            'button_fetch_job': 'Fetch Job Info',
            'button_generate': 'Generate Custom Resume',
            'button_export_pdf': 'Export PDF',
            'button_export_records': 'Export Records',
            'button_upload_word': 'Upload Word Resume',
            'button_preview': 'Preview Resume',
            'button_clear': 'Clear',
            'hint_auto_steps': 'Steps: Complete "Initial Setup" → Upload Resume → Click Start',
            'status_ready': 'Ready',
            'warning': 'Warning',
            'error': 'Error',
            'success': 'Success',
            'confirm': 'Confirm',
        }
        
        return texts_zh if lang == "zh" else texts_en
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.config = config
            except:
                self.config = {}
        else:
            self.config = {}
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def create_widgets(self):
        """创建主界面"""
        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建4个标签页
        self.tab_init = ttk.Frame(self.notebook, padding="10")
        self.tab_auto = ttk.Frame(self.notebook, padding="10")
        self.tab_manual = ttk.Frame(self.notebook, padding="10")
        self.tab_records = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.tab_init, text=self.texts['tab_init'])
        self.notebook.add(self.tab_auto, text=self.texts['tab_auto'])
        self.notebook.add(self.tab_manual, text=self.texts['tab_manual'])
        self.notebook.add(self.tab_records, text=self.texts['tab_records'])
        
        # 创建各个标签页的内容
        self.create_tab_init()
        self.create_tab_auto()
        self.create_tab_manual()
        self.create_tab_records()
        
        # 创建状态栏和语言切换按钮
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text=self.texts['status_ready'], relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 语言切换按钮
        lang_text = "EN" if self.language == "zh" else "中文"
        self.lang_button = ttk.Button(status_frame, text=lang_text, width=5, command=self.toggle_language)
        self.lang_button.pack(side=tk.RIGHT, padx=5)
    
    def create_tab_init(self):
        """创建标签1：初始化配置"""
        # API密钥配置分组
        api_frame = ttk.LabelFrame(self.tab_init, text=self.texts['frame_api'], padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_key_row = ttk.Frame(api_frame)
        api_key_row.pack(fill=tk.X, pady=5)
        ttk.Label(api_key_row, text=self.texts['label_api_key']).pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(api_key_row, width=50, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        if 'api_key' in self.config:
            self.api_key_entry.insert(0, self.config['api_key'])
        ttk.Label(api_key_row, text=self.texts['label_api_required'], foreground="red").pack(side=tk.LEFT)
        
        # 浏览器登录状态分组
        browser_frame = ttk.LabelFrame(self.tab_init, text=self.texts['frame_browser'], padding="10")
        browser_frame.pack(fill=tk.X, pady=(0, 10))
        
        chrome_dir_row = ttk.Frame(browser_frame)
        chrome_dir_row.pack(fill=tk.X, pady=5)
        ttk.Label(chrome_dir_row, text=self.texts['label_chrome_profile']).pack(side=tk.LEFT)
        self.chrome_dir_entry = ttk.Entry(chrome_dir_row, width=40)
        self.chrome_dir_entry.pack(side=tk.LEFT, padx=5)
        if 'chrome_user_data_dir' in self.config:
            self.chrome_dir_entry.insert(0, self.config['chrome_user_data_dir'])
        ttk.Button(chrome_dir_row, text="浏览", command=self.browse_chrome_dir).pack(side=tk.LEFT)
        
        chrome_profile_row = ttk.Frame(browser_frame)
        chrome_profile_row.pack(fill=tk.X, pady=5)
        ttk.Label(chrome_profile_row, text=self.texts['label_chrome_profile_name']).pack(side=tk.LEFT)
        self.chrome_profile_entry = ttk.Entry(chrome_profile_row, width=20)
        self.chrome_profile_entry.pack(side=tk.LEFT, padx=5)
        if 'chrome_profile' in self.config:
            self.chrome_profile_entry.insert(0, self.config['chrome_profile'])
        else:
            self.chrome_profile_entry.insert(0, "Default")
        
        # 个人投递信息分组
        user_frame = ttk.LabelFrame(self.tab_init, text=self.texts['frame_user_info'], padding="10")
        user_frame.pack(fill=tk.X, pady=(0, 10))
        
        name_row = ttk.Frame(user_frame)
        name_row.pack(fill=tk.X, pady=5)
        ttk.Label(name_row, text=self.texts['label_user_name']).pack(side=tk.LEFT)
        self.user_name_entry = ttk.Entry(name_row, width=30)
        self.user_name_entry.pack(side=tk.LEFT, padx=5)
        if 'user_name' in self.config:
            self.user_name_entry.insert(0, self.config['user_name'])
        
        email_row = ttk.Frame(user_frame)
        email_row.pack(fill=tk.X, pady=5)
        ttk.Label(email_row, text=self.texts['label_user_email']).pack(side=tk.LEFT)
        self.user_email_entry = ttk.Entry(email_row, width=30)
        self.user_email_entry.pack(side=tk.LEFT, padx=5)
        if 'user_email' in self.config:
            self.user_email_entry.insert(0, self.config['user_email'])
        
        phone_row = ttk.Frame(user_frame)
        phone_row.pack(fill=tk.X, pady=5)
        ttk.Label(phone_row, text=self.texts['label_user_phone']).pack(side=tk.LEFT)
        self.user_phone_entry = ttk.Entry(phone_row, width=30)
        self.user_phone_entry.pack(side=tk.LEFT, padx=5)
        if 'user_phone' in self.config:
            self.user_phone_entry.insert(0, self.config['user_phone'])
        
        # 保存配置按钮
        save_button = ttk.Button(self.tab_init, text="保存配置", command=self.save_config_from_ui)
        save_button.pack(pady=10)
    
    def browse_chrome_dir(self):
        """浏览Chrome用户数据目录"""
        directory = filedialog.askdirectory(title="选择Chrome用户数据目录")
        if directory:
            self.chrome_dir_entry.delete(0, tk.END)
            self.chrome_dir_entry.insert(0, directory)
    
    def save_config_from_ui(self):
        """从UI保存配置"""
        self.config['api_key'] = self.api_key_entry.get()
        self.config['chrome_user_data_dir'] = self.chrome_dir_entry.get()
        self.config['chrome_profile'] = self.chrome_profile_entry.get()
        self.config['user_name'] = self.user_name_entry.get()
        self.config['user_email'] = self.user_email_entry.get()
        self.config['user_phone'] = self.user_phone_entry.get()
        self.save_config()
        messagebox.showinfo(self.texts['success'], "配置已保存！")
    
    def create_tab_auto(self):
        """创建标签2：全自动求职"""
        # 顶部提示文字
        hint_label = ttk.Label(self.tab_auto, text=self.texts['hint_auto_steps'], 
                              foreground="blue", font=("Arial", 10, "bold"))
        hint_label.pack(pady=(0, 15))
        
        # 地区选择
        region_row = ttk.Frame(self.tab_auto)
        region_row.pack(fill=tk.X, pady=5)
        ttk.Label(region_row, text=self.texts['label_region']).pack(side=tk.LEFT)
        self.region_var = tk.StringVar()
        region_combo = ttk.Combobox(region_row, textvariable=self.region_var, 
                                    values=["香港 (hk)", "新加坡 (sg)", "马来西亚 (my)", "菲律宾 (ph)"],
                                    width=20, state="readonly")
        region_combo.pack(side=tk.LEFT, padx=5)
        if 'region' in self.config:
            self.region_var.set(self.config['region'])
        else:
            self.region_var.set("香港 (hk)")
        
        # 搜索关键词
        keyword_row = ttk.Frame(self.tab_auto)
        keyword_row.pack(fill=tk.X, pady=5)
        ttk.Label(keyword_row, text=self.texts['label_keyword']).pack(side=tk.LEFT)
        self.search_keyword_entry = ttk.Entry(keyword_row, width=40)
        self.search_keyword_entry.pack(side=tk.LEFT, padx=5)
        if 'search_keyword' in self.config:
            self.search_keyword_entry.insert(0, self.config['search_keyword'])
        
        # 搜索地点
        location_row = ttk.Frame(self.tab_auto)
        location_row.pack(fill=tk.X, pady=5)
        ttk.Label(location_row, text=self.texts['label_location']).pack(side=tk.LEFT)
        self.search_location_entry = ttk.Entry(location_row, width=40)
        self.search_location_entry.pack(side=tk.LEFT, padx=5)
        if 'search_location' in self.config:
            self.search_location_entry.insert(0, self.config['search_location'])
        
        # 匹配度阈值
        threshold_row = ttk.Frame(self.tab_auto)
        threshold_row.pack(fill=tk.X, pady=5)
        ttk.Label(threshold_row, text=self.texts['label_threshold']).pack(side=tk.LEFT)
        self.match_threshold_entry = ttk.Entry(threshold_row, width=10)
        self.match_threshold_entry.pack(side=tk.LEFT, padx=5)
        if 'match_threshold' in self.config:
            self.match_threshold_entry.insert(0, str(self.config['match_threshold']))
        else:
            self.match_threshold_entry.insert(0, "70")
        ttk.Label(threshold_row, text="（0-100，建议70）", foreground="gray").pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(self.tab_auto)
        button_frame.pack(pady=20)
        
        # 打开目标网站按钮
        open_website_btn = ttk.Button(button_frame, text=self.texts['button_open_website'],
                                      command=self.on_open_website_click)
        open_website_btn.pack(side=tk.LEFT, padx=5)
        
        # 开始全自动求职按钮（高亮）
        self.start_auto_btn = tk.Button(button_frame, text=self.texts['button_start_auto'],
                                        command=self.on_start_auto_click,
                                        bg="#4A90E2", fg="white", font=("Arial", 11, "bold"),
                                        padx=20, pady=5, cursor="hand2")
        self.start_auto_btn.pack(side=tk.LEFT, padx=5)
        
        # 暂停/继续按钮
        self.pause_button = ttk.Button(button_frame, text=self.texts['button_pause'],
                                       command=self.on_pause_click, state="disabled")
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.tab_auto, text="执行结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.auto_result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        self.auto_result_text.pack(fill=tk.BOTH, expand=True)
    
    def on_open_website_click(self):
        """打开目标网站"""
        region = self.config.get('region', '香港 (hk)')
        if 'hk' in region:
            url = 'https://hk.jobsdb.com'
        elif 'sg' in region:
            url = 'https://sg.jobsdb.com'
        elif 'my' in region:
            url = 'https://my.jobsdb.com'
        elif 'ph' in region:
            url = 'https://ph.jobsdb.com'
        else:
            url = 'https://hk.jobsdb.com'
        
        webbrowser.open(url)
        self.update_status("已打开目标网站")
    
    def on_start_auto_click(self):
        """开始全自动求职"""
        if self.is_auto_running:
            # 停止
            self.is_auto_running = False
            self.start_auto_btn.config(text=self.texts['button_start_auto'])
            self.pause_button.config(state="disabled")
            self.update_status("已停止自动求职")
            return
        
        # 检查必要配置
        if not self.config.get('api_key'):
            messagebox.showerror(self.texts['error'], "请先配置API Key")
            return
        
        if not self.config.get('resume_content'):
            messagebox.showerror(self.texts['error'], "请先上传或输入原始简历")
            return
        
        # 开始自动求职
        self.is_auto_running = True
        self.start_auto_btn.config(text="停止自动求职" if self.language == "zh" else "Stop Auto Search")
        self.pause_button.config(state="normal")
        
        # 在新线程中运行
        thread = threading.Thread(target=self.auto_job_search_worker, daemon=True)
        thread.start()
    
    def auto_job_search_worker(self):
        """自动求职工作线程"""
        try:
            keyword = self.search_keyword_entry.get()
            location = self.search_location_entry.get()
            threshold = int(self.match_threshold_entry.get())
            region = self.region_var.get()
            
            self.log_auto_result(f"开始搜索：关键词={keyword}, 地点={location}\n")
            
            # 这里应该实现实际的岗位搜索逻辑
            # 由于JobsDB的搜索API可能不公开，这里提供一个框架
            # 实际使用时可能需要使用Selenium来模拟搜索
            
            self.log_auto_result("注意：自动搜索功能需要根据JobsDB的实际网页结构进行定制开发\n")
            self.log_auto_result("当前版本建议使用「手动单岗处理」功能\n")
            
        except Exception as e:
            self.log_auto_result(f"错误: {str(e)}\n")
        finally:
            self.is_auto_running = False
            self.root.after(0, lambda: self.start_auto_btn.config(text=self.texts['button_start_auto']))
            self.root.after(0, lambda: self.pause_button.config(state="disabled"))
    
    def log_auto_result(self, message):
        """在自动求职结果区域添加日志"""
        self.root.after(0, lambda: self.auto_result_text.insert(tk.END, message))
        self.root.after(0, lambda: self.auto_result_text.see(tk.END))
    
    def on_pause_click(self):
        """暂停/继续"""
        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.pause_button.config(text=self.texts['button_pause'])
            self.update_status("已继续")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.pause_button.config(text=self.texts['button_resume'])
            self.update_status("已暂停")
    
    def update_status(self, message):
        """更新状态栏"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def create_tab_manual(self):
        """创建标签3：手动单岗处理"""
        # 岗位链接
        url_row = ttk.Frame(self.tab_manual)
        url_row.pack(fill=tk.X, pady=5)
        ttk.Label(url_row, text=self.texts['label_job_url']).pack(side=tk.LEFT)
        self.job_url_entry = ttk.Entry(url_row, width=60)
        self.job_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        fetch_btn = ttk.Button(url_row, text=self.texts['button_fetch_job'], 
                               command=self.on_fetch_job_click)
        fetch_btn.pack(side=tk.LEFT, padx=5)
        
        # 岗位描述
        desc_label = ttk.Label(self.tab_manual, text=self.texts['label_job_description'])
        desc_label.pack(anchor=tk.W, pady=(10, 5))
        self.job_description_text = scrolledtext.ScrolledText(self.tab_manual, height=8, wrap=tk.WORD)
        self.job_description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 原始简历区域
        resume_frame = ttk.LabelFrame(self.tab_manual, text="原始简历", padding="10")
        resume_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 简历语言选择
        lang_row = ttk.Frame(resume_frame)
        lang_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(lang_row, text=self.texts['label_resume_language']).pack(side=tk.LEFT)
        self.resume_language_var = tk.StringVar(value="auto")
        lang_combo = ttk.Combobox(lang_row, textvariable=self.resume_language_var,
                                  values=["auto", "zh", "en"], width=15, state="readonly")
        lang_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(lang_row, text="（auto=自动检测）", foreground="gray").pack(side=tk.LEFT)
        
        # 简历文本区域和按钮
        resume_btn_row = ttk.Frame(resume_frame)
        resume_btn_row.pack(fill=tk.X, pady=(0, 5))
        upload_word_btn = ttk.Button(resume_btn_row, text=self.texts['button_upload_word'],
                                     command=self.on_upload_word_click)
        upload_word_btn.pack(side=tk.LEFT, padx=5)
        preview_btn = ttk.Button(resume_btn_row, text=self.texts['button_preview'],
                                 command=self.on_preview_resume_click)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        self.resume_text = scrolledtext.ScrolledText(resume_frame, height=10, wrap=tk.WORD)
        self.resume_text.pack(fill=tk.BOTH, expand=True)
        if 'resume_content' in self.config:
            self.resume_text.insert("1.0", self.config['resume_content'])
        
        # 操作按钮区域
        action_frame = ttk.Frame(self.tab_manual)
        action_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = tk.Button(action_frame, text=self.texts['button_generate'],
                                command=self.on_generate_click,
                                bg="#4A90E2", fg="white", font=("Arial", 11, "bold"),
                                padx=20, pady=5, cursor="hand2")
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        export_pdf_btn = ttk.Button(action_frame, text=self.texts['button_export_pdf'],
                                    command=self.on_export_pdf_click)
        export_pdf_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(action_frame, text=self.texts['button_clear'],
                              command=self.on_clear_click)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 生成结果区域
        result_label = ttk.Label(self.tab_manual, text="生成的定制简历：")
        result_label.pack(anchor=tk.W, pady=(10, 5))
        self.result_text = scrolledtext.ScrolledText(self.tab_manual, height=12, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def on_fetch_job_click(self):
        """抓取岗位信息"""
        job_url = self.job_url_entry.get().strip()
        if not job_url:
            messagebox.showerror(self.texts['error'], "请输入岗位链接")
            return
        
        self.update_status("正在抓取岗位信息...")
        
        def fetch_worker():
            try:
                job_info, error = self.fetch_job_info(job_url)
                if error:
                    self.root.after(0, lambda: messagebox.showerror(self.texts['error'], error))
                    self.root.after(0, lambda: self.update_status(self.texts['status_ready']))
                else:
                    # 更新UI
                    self.root.after(0, lambda: self.job_description_text.delete("1.0", tk.END))
                    self.root.after(0, lambda: self.job_description_text.insert("1.0", job_info['description']))
                    self.root.after(0, lambda: self.update_status(f"已抓取：{job_info['title']}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self.texts['error'], str(e)))
                self.root.after(0, lambda: self.update_status(self.texts['status_ready']))
        
        thread = threading.Thread(target=fetch_worker, daemon=True)
        thread.start()
    
    def on_upload_word_click(self):
        """上传Word简历"""
        if not DOCX_AVAILABLE:
            messagebox.showerror(self.texts['error'], 
                               "未安装python-docx库，请运行: pip install python-docx")
            return
        
        file_path = filedialog.askopenfilename(
            title="选择Word简历文件",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                doc = Document(file_path)
                text_content = "\n".join([para.text for para in doc.paragraphs])
                
                self.resume_text.delete("1.0", tk.END)
                self.resume_text.insert("1.0", text_content)
                
                # 保存到配置
                self.config['resume_content'] = text_content
                self.save_config()
                
                messagebox.showinfo(self.texts['success'], "简历已上传")
            except Exception as e:
                messagebox.showerror(self.texts['error'], f"读取文件失败: {str(e)}")
    
    def on_preview_resume_click(self):
        """预览简历"""
        resume_content = self.resume_text.get("1.0", tk.END).strip()
        if not resume_content:
            messagebox.showwarning(self.texts['warning'], "简历内容为空")
            return
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("简历预览")
        preview_window.geometry("600x700")
        
        text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=("Arial", 11))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", resume_content)
        text_widget.config(state=tk.DISABLED)
    
    def on_generate_click(self):
        """生成定制简历"""
        # 检查必要信息
        if not self.config.get('api_key'):
            messagebox.showerror(self.texts['error'], "请先配置API Key")
            return
        
        job_description = self.job_description_text.get("1.0", tk.END).strip()
        if not job_description:
            messagebox.showerror(self.texts['error'], "请输入岗位描述")
            return
        
        original_resume = self.resume_text.get("1.0", tk.END).strip()
        if not original_resume:
            messagebox.showerror(self.texts['error'], "请输入或上传原始简历")
            return
        
        resume_language = self.resume_language_var.get()
        
        self.update_status("正在生成定制简历...")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "正在生成，请稍候...")
        
        def generate_worker():
            try:
                custom_resume, error = self.generate_custom_resume(
                    job_description, original_resume, resume_language
                )
                
                if error:
                    self.root.after(0, lambda: messagebox.showerror(self.texts['error'], error))
                    self.root.after(0, lambda: self.result_text.delete("1.0", tk.END))
                    self.root.after(0, lambda: self.update_status(self.texts['status_ready']))
                else:
                    # 计算匹配度
                    match_score = self.calculate_match_score(job_description, custom_resume)
                    
                    # 更新UI
                    self.root.after(0, lambda: self.result_text.delete("1.0", tk.END))
                    self.root.after(0, lambda: self.result_text.insert("1.0", custom_resume))
                    self.root.after(0, lambda: self.update_status(f"生成完成，匹配度: {match_score}%"))
                    self.root.after(0, lambda: messagebox.showinfo(
                        self.texts['success'], 
                        f"简历生成成功！匹配度: {match_score}%"
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self.texts['error'], str(e)))
                self.root.after(0, lambda: self.update_status(self.texts['status_ready']))
        
        thread = threading.Thread(target=generate_worker, daemon=True)
        thread.start()
    
    def on_export_pdf_click(self):
        """导出PDF"""
        resume_content = self.result_text.get("1.0", tk.END).strip()
        if not resume_content:
            messagebox.showwarning(self.texts['warning'], "没有可导出的简历内容")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                # 设置中文字体（需要支持中文的字体）
                try:
                    pdf.add_font('SimSun', '', 'simsun.ttc', uni=True)
                    pdf.set_font('SimSun', '', 12)
                except:
                    # 如果没有中文字体，使用默认字体
                    pdf.set_font('Arial', '', 12)
                
                # 添加内容（处理换行）
                lines = resume_content.split('\n')
                for line in lines:
                    if line.strip():
                        pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=1)
                    else:
                        pdf.ln(5)
                
                pdf.output(file_path)
                messagebox.showinfo(self.texts['success'], "PDF已导出")
            except Exception as e:
                messagebox.showerror(self.texts['error'], f"导出失败: {str(e)}")
    
    def on_clear_click(self):
        """清空"""
        self.job_url_entry.delete(0, tk.END)
        self.job_description_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
    
    def create_tab_records(self):
        """创建标签4：投递记录查询"""
        # 记录列表标题
        records_label = ttk.Label(self.tab_records, text="投递记录列表", 
                                  font=("Arial", 10, "bold"))
        records_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建Treeview显示记录
        columns = ('岗位名称', '公司', '投递日期', '匹配度', '状态')
        self.records_tree = ttk.Treeview(self.tab_records, columns=columns, show='headings', height=20)
        
        # 设置列标题
        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.tab_records, orient=tk.VERTICAL, 
                                  command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        tree_frame = ttk.Frame(self.tab_records)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        records_button_frame = ttk.Frame(self.tab_records)
        records_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_btn = ttk.Button(records_button_frame, text="刷新记录",
                                 command=self.refresh_records, width=15)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(records_button_frame, text=self.texts['button_export_records'],
                                command=self.export_records, width=15)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始加载记录
        self.refresh_records()
    
    def refresh_records(self):
        """刷新投递记录"""
        # 清空现有记录
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # 从文件加载记录
        records_file = "application_records.json"
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    for record in records:
                        self.records_tree.insert('', tk.END, values=(
                            record.get('job_title', ''),
                            record.get('company', ''),
                            record.get('apply_date', ''),
                            record.get('match_score', ''),
                            record.get('status', '')
                        ))
            except Exception as e:
                print(f"加载记录失败: {e}")
    
    def export_records(self):
        """导出投递记录"""
        records_file = "application_records.json"
        if not os.path.exists(records_file):
            messagebox.showwarning(self.texts['warning'], "没有投递记录")
            return
        
        try:
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            if not records:
                messagebox.showwarning(self.texts['warning'], "没有投递记录")
                return
            
            # 选择导出格式
            file_path = filedialog.asksaveasfilename(
                title="导出投递记录",
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
            )
            
            if file_path:
                df = pd.DataFrame(records)
                
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False, engine='openpyxl')
                else:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                messagebox.showinfo(self.texts['success'], "记录已导出")
        except Exception as e:
            messagebox.showerror(self.texts['error'], f"导出失败: {str(e)}")
    
    def setup_auto_save(self):
        """设置自动保存"""
        # 绑定输入框变化事件，自动保存配置
        self.api_key_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
        self.chrome_dir_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
        self.chrome_profile_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
        self.user_name_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
        self.user_email_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
        self.user_phone_entry.bind('<FocusOut>', lambda e: self.auto_save_config())
    
    def auto_save_config(self):
        """自动保存配置"""
        self.config['api_key'] = self.api_key_entry.get()
        self.config['chrome_user_data_dir'] = self.chrome_dir_entry.get()
        self.config['chrome_profile'] = self.chrome_profile_entry.get()
        self.config['user_name'] = self.user_name_entry.get()
        self.config['user_email'] = self.user_email_entry.get()
        self.config['user_phone'] = self.user_phone_entry.get()
        # 保存搜索条件
        if hasattr(self, 'region_var'):
            self.config['region'] = self.region_var.get()
        if hasattr(self, 'search_keyword_entry'):
            self.config['search_keyword'] = self.search_keyword_entry.get()
        if hasattr(self, 'search_location_entry'):
            self.config['search_location'] = self.search_location_entry.get()
        if hasattr(self, 'match_threshold_entry'):
            try:
                self.config['match_threshold'] = int(self.match_threshold_entry.get())
            except:
                pass
        self.config['language'] = self.language
        self.save_config()
    
    def toggle_language(self):
        """切换中英文"""
        self.language = "en" if self.language == "zh" else "zh"
        self.texts = self.get_texts(self.language)
        self.config['language'] = self.language
        self.save_config()
        
        # 更新界面文字
        self.root.title(self.texts['app_title'])
        self.status_label.config(text=self.texts['status_ready'])
        self.lang_button.config(text="EN" if self.language == "zh" else "中文")
        
        # 更新标签页标题
        self.notebook.tab(0, text=self.texts['tab_init'])
        self.notebook.tab(1, text=self.texts['tab_auto'])
        self.notebook.tab(2, text=self.texts['tab_manual'])
        self.notebook.tab(3, text=self.texts['tab_records'])
        
        messagebox.showinfo(self.texts['success'], 
                          "语言已切换" if self.language == "zh" else "Language switched")
    
    # ========== 核心功能函数 ==========
    
    def generate_custom_resume(self, job_description, original_resume, resume_language="auto"):
        """使用DeepSeek API生成定制简历"""
        api_key = self.config.get('api_key', '')
        if not api_key:
            return None, "API Key未配置"
        
        # 检测简历语言
        if resume_language == "auto":
            # 简单检测：如果中文字符超过30%，认为是中文简历
            chinese_chars = len([c for c in original_resume if '\u4e00' <= c <= '\u9fff'])
            resume_language = "zh" if chinese_chars / max(len(original_resume), 1) > 0.3 else "en"
        
        # 构建Prompt
        if resume_language == "zh":
            prompt = f"""你是一位专业的求职顾问。请根据下面的【岗位描述】，重写我的【原始简历】，突出与岗位最匹配的技能和经验。

要求：
1. 保持简历的专业性和真实性
2. 突出与岗位要求最相关的经验和技能
3. 使用专业、简洁的语言
4. 保持简历结构清晰，不要超过一页
5. 保留原始简历中的关键信息（姓名、联系方式、教育背景等）

【岗位描述】
{job_description}

【原始简历】
{original_resume}

请生成定制后的简历："""
        else:
            prompt = f"""You are a professional career consultant. Please rewrite my original resume based on the job description below, highlighting the skills and experiences that best match the position.

Requirements:
1. Maintain professionalism and authenticity
2. Highlight the most relevant experiences and skills for the job requirements
3. Use professional and concise language
4. Keep the resume structure clear, not exceeding one page
5. Retain key information from the original resume (name, contact, education, etc.)

【Job Description】
{job_description}

【Original Resume】
{original_resume}

Please generate the customized resume:"""
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                generated_resume = result['choices'][0]['message']['content']
                return generated_resume, None
            else:
                return None, "API返回格式错误"
                
        except requests.exceptions.RequestException as e:
            return None, f"网络错误: {str(e)}"
        except Exception as e:
            return None, f"生成失败: {str(e)}"
    
    def fetch_job_info(self, job_url):
        """抓取岗位信息"""
        try:
            # 根据地区确定JobsDB域名
            region = self.config.get('region', '香港 (hk)')
            if 'hk' in region:
                base_url = 'https://hk.jobsdb.com'
            elif 'sg' in region:
                base_url = 'https://sg.jobsdb.com'
            elif 'my' in region:
                base_url = 'https://my.jobsdb.com'
            elif 'ph' in region:
                base_url = 'https://ph.jobsdb.com'
            else:
                base_url = 'https://hk.jobsdb.com'
            
            # 如果URL不完整，补全
            if not job_url.startswith('http'):
                job_url = urljoin(base_url, job_url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(job_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取岗位描述（JobsDB的HTML结构可能变化，这里提供基础版本）
            job_title = ""
            job_description = ""
            
            # 查找标题
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                job_title = title_elem.get_text(strip=True)
            
            # 查找描述（常见的选择器）
            desc_selectors = [
                'div[data-automation="jobDescription"]',
                '.job-description',
                '#jobDescription',
                'div.jobDescription'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    job_description = desc_elem.get_text(strip=True)
                    break
            
            # 如果没找到，尝试查找包含"description"的div
            if not job_description:
                for div in soup.find_all('div', class_=lambda x: x and 'description' in x.lower()):
                    job_description = div.get_text(strip=True)
                    if len(job_description) > 100:
                        break
            
            return {
                'title': job_title,
                'description': job_description,
                'url': job_url
            }, None
            
        except Exception as e:
            return None, f"抓取失败: {str(e)}"
    
    def get_chrome_driver(self):
        """获取Chrome浏览器驱动"""
        chrome_options = Options()
        
        # 如果配置了用户数据目录，使用现有Chrome配置（保持登录状态）
        user_data_dir = self.config.get('chrome_user_data_dir', '')
        profile_name = self.config.get('chrome_profile', 'Default')
        
        if user_data_dir:
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
            chrome_options.add_argument(f'--profile-directory={profile_name}')
        
        # 其他选项
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver, None
        except Exception as e:
            return None, f"启动Chrome失败: {str(e)}"
    
    def auto_apply_job(self, job_url, custom_resume, user_info):
        """自动投递岗位"""
        driver, error = self.get_chrome_driver()
        if error:
            return False, error
        
        try:
            driver.get(job_url)
            time.sleep(3)  # 等待页面加载
            
            # 尝试填写表单（JobsDB的表单结构可能变化，这里提供基础版本）
            # 查找并填写姓名
            name_selectors = ['input[name*="name"]', 'input[id*="name"]', 'input[placeholder*="name" i]']
            for selector in name_selectors:
                try:
                    name_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name_input.clear()
                    name_input.send_keys(user_info.get('name', ''))
                    break
                except:
                    continue
            
            # 填写邮箱
            email_selectors = ['input[type="email"]', 'input[name*="email"]', 'input[id*="email"]']
            for selector in email_selectors:
                try:
                    email_input = driver.find_element(By.CSS_SELECTOR, selector)
                    email_input.clear()
                    email_input.send_keys(user_info.get('email', ''))
                    break
                except:
                    continue
            
            # 填写电话
            phone_selectors = ['input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]']
            for selector in phone_selectors:
                try:
                    phone_input = driver.find_element(By.CSS_SELECTOR, selector)
                    phone_input.clear()
                    phone_input.send_keys(user_info.get('phone', ''))
                    break
                except:
                    continue
            
            # 填写简历/自我介绍
            resume_selectors = ['textarea[name*="resume"]', 'textarea[id*="resume"]', 
                              'textarea[name*="cover"]', 'textarea[id*="cover"]',
                              'textarea[name*="description"]', 'textarea[id*="description"]']
            for selector in resume_selectors:
                try:
                    resume_textarea = driver.find_element(By.CSS_SELECTOR, selector)
                    resume_textarea.clear()
                    resume_textarea.send_keys(custom_resume)
                    break
                except:
                    continue
            
            # 注意：这里不自动提交，让用户手动确认
            # 如果需要自动提交，可以取消下面的注释
            # submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            # submit_button.click()
            
            return True, "表单已填写，请手动确认提交"
            
        except Exception as e:
            return False, f"自动投递失败: {str(e)}"
        finally:
            # 不关闭浏览器，让用户查看和确认
            pass
    
    def calculate_match_score(self, job_description, resume):
        """计算简历与岗位的匹配度（简单版本）"""
        # 提取关键词（简单实现）
        job_keywords = set(re.findall(r'\b\w{4,}\b', job_description.lower()))
        resume_keywords = set(re.findall(r'\b\w{4,}\b', resume.lower()))
        
        if not job_keywords:
            return 0
        
        # 计算匹配的关键词比例
        matched = len(job_keywords & resume_keywords)
        match_score = int((matched / len(job_keywords)) * 100)
        
        return min(match_score, 100)
    
    def save_application_record(self, job_title, company, job_url, match_score, status="已投递"):
        """保存投递记录"""
        records_file = "application_records.json"
        records = []
        
        if os.path.exists(records_file):
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                records = []
        
        record = {
            'job_title': job_title,
            'company': company,
            'job_url': job_url,
            'apply_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'match_score': f"{match_score}%",
            'status': status
        }
        
        records.append(record)
        
        try:
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存记录失败: {e}")
            return False


def main():
    """主函数"""
    root = tk.Tk()
    app = ResumeGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

