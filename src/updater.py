#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有爱插件 Mac 更新器 - 主程序
功能：检查更新、下载、安装、GUI 界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import sys
import hashlib
import zipfile
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import requests
import threading
import webbrowser


class Config:
    """配置管理"""
    
    def __init__(self):
        self.config_file = Path.home() / 'Library' / 'Preferences' / 'YouAiUpdater' / 'config.json'
        self.default_config = {
            'app': {
                'version': '1.0.0',
                'check_interval_days': 7,
                'last_check': None,
                'auto_check': True
            },
            'github': {
                'repo': 'codejorker/youai_updater_mac',  # GitHub 仓库（用于 Actions）
                'api_base': 'https://api.github.com/repos'
            },
            'gitee': {
                'enabled': True,  # 是否启用码云镜像
                'user': 'YOUR_USERNAME',  # 需要替换为你的码云用户名
                'repo': 'youai_updater_mac',
                'api_base': 'https://gitee.com/api/v5/repos'
            },
            'plugin': {
                'name': 'youai-plugin',
                'target_folders': ['_retail_', '_classic_']
            },
            'paths': {
                'wow_path': None,
                'cache_dir': str(Path.home() / 'Library' / 'Caches' / 'YouAiUpdater'),
                'backup_dir': str(Path.home() / 'Library' / 'Application Support' / 'YouAiUpdater' / 'Backups')
            },
            'features': {
                'backup_before_update': True,
                'sha256_verify': True,
                'auto_restart_game': False
            }
        }
        self.config = self.load()
    
    def load(self):
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败：{e}")
        
        # 创建默认配置
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.default_config, f, indent=2, ensure_ascii=False)
        
        return self.default_config
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败：{e}")
    
    def get(self, *keys, default=None):
        """获取配置值"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """设置配置值"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()


class YouAiUpdater:
    """有爱插件更新器核心逻辑"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = Path(self.config.config['paths']['cache_dir'])
        self.backup_dir = Path(self.config.config['paths']['backup_dir'])
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def check_latest_version(self):
        """从 GitHub 或码云 API 获取最新版本信息"""
        try:
            # 优先使用码云（如果启用）
            if self.config.get('gitee', 'enabled'):
                gitee_user = self.config.get('gitee', 'user')
                gitee_repo = self.config.get('gitee', 'repo')
                
                # 跳过占位符用户名
                if gitee_user != 'YOUR_USERNAME':
                    try:
                        api_url = f"{self.config.get('gitee', 'api_base')}/{gitee_user}/{gitee_repo}/releases/latest"
                        print(f"🔍 正在检查码云版本...")
                        
                        response = requests.get(api_url, timeout=10)
                        response.raise_for_status()
                        
                        data = response.json()
                        print(f"✅ 码云版本：{data.get('tag_name', 'N/A')}")
                        return {
                            'version': data.get('tag_name', ''),
                            'name': data.get('name', ''),
                            'url': data.get('html_url', ''),
                            'assets': data.get('assets', []),
                            'published_at': data.get('created_at', ''),
                            'body': data.get('body', '')
                        }
                    except Exception as e:
                        print(f"⚠️ 码云检查失败，切换到 GitHub: {e}")
            
            # 从 GitHub 获取
            repo = self.config.get('github', 'repo')
            api_url = f"{self.config.get('github', 'api_base')}/{repo}/releases/latest"
            print(f"🔍 正在检查 GitHub 版本...")
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ GitHub 版本：{data.get('tag_name', 'N/A')}")
            return {
                'version': data.get('tag_name', ''),
                'name': data.get('name', ''),
                'url': data.get('html_url', ''),
                'assets': data.get('assets', []),
                'published_at': data.get('published_at', ''),
                'body': data.get('body', '')
            }
        except Exception as e:
            print(f"检查版本失败：{e}")
            return None
    
    def detect_installed_plugin(self, wow_path: str = None):
        """检测已安装的插件版本"""
        if not wow_path:
            wow_path = self.config.get('paths', 'wow_path')
        
        if not wow_path:
            return None
        
        try:
            # 查找 Interface/AddOns目录
            interface_dir = Path(wow_path) / 'Interface' / 'AddOns'
            
            if not interface_dir.exists():
                return None
            
            # 尝试读取 TOC 文件获取版本信息
            for addon_dir in interface_dir.iterdir():
                if addon_dir.is_dir():
                    toc_file = addon_dir / f"{addon_dir.name}.toc"
                    if toc_file.exists():
                        with open(toc_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.startswith('## Version:'):
                                    return line.split(':')[1].strip()
            
            return '已安装 (未知版本)'
        except Exception as e:
            print(f"检测已安装插件失败：{e}")
            return None
    
    def find_wow_installation(self):
        """自动扫描魔兽安装路径"""
        default_paths = [
            Path('/Applications/World of Warcraft'),
            Path.home() / 'Games' / 'World of Warcraft',
            Path.home() / 'Documents' / 'World of Warcraft'
        ]
        
        found_paths = []
        for base_path in default_paths:
            if base_path.exists():
                # 检查是否包含 _retail_ 或 _classic_
                for folder in self.config.get('plugin', 'target_folders'):
                    game_path = base_path / folder
                    if game_path.exists():
                        found_paths.append(str(base_path))
                        break
        
        return found_paths
    
    def download_update(self, asset_url: str, progress_callback=None):
        """下载更新文件，返回本地路径"""
        try:
            filename = asset_url.split('/')[-1]
            local_path = self.cache_dir / filename
            
            response = requests.get(asset_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return str(local_path)
        except Exception as e:
            print(f"下载更新失败：{e}")
            return None
    
    def verify_file_hash(self, file_path: str, expected_hash: str = None):
        """SHA256 校验"""
        if not expected_hash:
            return True  # 没有期望哈希值时跳过校验
        
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            calculated_hash = sha256_hash.hexdigest()
            return calculated_hash.lower() == expected_hash.lower()
        except Exception as e:
            print(f"文件校验失败：{e}")
            return False
    
    def backup_current_plugin(self, wow_path: str):
        """备份当前插件版本"""
        try:
            interface_dir = Path(wow_path) / 'Interface'
            if not interface_dir.exists():
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            shutil.copytree(interface_dir, backup_path)
            print(f"✅ 备份完成：{backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"备份失败：{e}")
            return None
    
    def install_update(self, zip_path: str, wow_path: str, progress_callback=None):
        """解压并安装更新"""
        try:
            target_interface = Path(wow_path) / 'Interface'
            
            # 备份旧的 AddOns（如果存在）
            old_addons = target_interface / 'AddOns'
            if old_addons.exists() and self.config.get('features', 'backup_before_update'):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.backup_dir / f"addons_backup_{timestamp}"
                shutil.copytree(old_addons, backup_path)
            
            # 解压新文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                members = zip_ref.namelist()
                total_members = len(members)
                
                for i, member in enumerate(members):
                    # 只解压 Interface文件夹
                    if member.startswith('Interface/'):
                        zip_ref.extract(member, self.cache_dir / 'temp_extract')
                    
                    if progress_callback:
                        progress = (i / total_members) * 100
                        progress_callback(progress)
            
            # 复制文件到目标位置
            extracted_interface = self.cache_dir / 'temp_extract' / 'Interface'
            if extracted_interface.exists():
                # 确保目标目录存在
                target_interface.mkdir(parents=True, exist_ok=True)
                
                # 复制整个 Interface文件夹
                if (extracted_interface / 'AddOns').exists():
                    target_addons = target_interface / 'AddOns'
                    if target_addons.exists():
                        shutil.rmtree(target_addons)
                    shutil.copytree(extracted_interface / 'AddOns', target_addons)
                
                print("✅ 安装完成")
                return True
            
            return False
            
        except Exception as e:
            print(f"安装更新失败：{e}")
            return False
        finally:
            # 清理临时文件
            temp_dir = self.cache_dir / 'temp_extract'
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def cleanup_old_backups(self, keep_count=3):
        """清理旧备份，保留最近 keep_count 个"""
        try:
            backups = sorted(self.backup_dir.glob('backup_*'))
            
            if len(backups) > keep_count:
                for old_backup in backups[:-keep_count]:
                    shutil.rmtree(old_backup)
                    print(f"🗑️ 清理旧备份：{old_backup}")
        except Exception as e:
            print(f"清理备份失败：{e}")


class UpdaterGUI:
    """更新器 GUI 界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("❤️ 有爱插件 Mac 更新器")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # 初始化
        self.config = Config()
        self.updater = YouAiUpdater(self.config)
        self.latest_version = None
        self.download_path = None
        
        # 构建界面
        self.setup_ui()
        
        # 启动时自动检查更新
        self.root.after(500, self.auto_check_update)
    
    def setup_ui(self):
        """构建 GUI 界面"""
        # 标题区域
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="❤️ 有爱插件 Mac 更新器",
            font=("Arial", 18, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="自动更新工具 - 每周一检查更新",
            font=("Arial", 10)
        )
        subtitle_label.pack()
        
        # 版本信息区域
        version_frame = ttk.LabelFrame(self.root, text="版本信息", padding="10")
        version_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 当前版本
        self.current_version_var = tk.StringVar(value="检测中...")
        ttk.Label(version_frame, text="当前安装:", width=12).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(version_frame, textvariable=self.current_version_var).grid(row=0, column=1, sticky=tk.W)
        
        # 最新版本
        self.latest_version_var = tk.StringVar(value="未检查")
        ttk.Label(version_frame, text="最新版本:", width=12).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(version_frame, textvariable=self.latest_version_var, foreground="blue").grid(row=1, column=1, sticky=tk.W)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(version_frame, textvariable=self.status_var, foreground="green")
        status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            version_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(self.root, text="魔兽安装路径", padding="10")
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        path_frame.columnconfigure(0, weight=1)
        
        browse_button = ttk.Button(path_frame, text="浏览...", command=self.on_browse_path)
        browse_button.grid(row=0, column=1)
        
        auto_detect_button = ttk.Button(path_frame, text="自动检测", command=self.on_auto_detect)
        auto_detect_button.grid(row=0, column=2, padx=(5, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.check_update_button = ttk.Button(
            button_frame,
            text="🔍 检查更新",
            command=self.on_check_update,
            width=15
        )
        self.check_update_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(
            button_frame,
            text="⬇️ 立即更新",
            command=self.on_update,
            width=15,
            state=tk.DISABLED
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        settings_button = ttk.Button(
            button_frame,
            text="⚙️ 设置",
            command=self.on_settings,
            width=15
        )
        settings_button.pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="更新日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部状态栏
        status_bar_frame = ttk.Frame(self.root)
        status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        last_check_label = ttk.Label(
            status_bar_frame,
            text=f"上次检查：{self.config.get('app', 'last_check') or '从未'}",
            font=("Arial", 9)
        )
        last_check_label.pack(side=tk.LEFT, padx=10)
        
        # 菜单
        self.create_menu()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="检查更新", command=self.on_check_update)
        tools_menu.add_command(label="查看更新日志", command=self.show_release_notes)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def log(self, message, level="info"):
        """添加日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        colors = {
            'info': 'black',
            'success': 'green',
            'warning': 'orange',
            'error': 'red'
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        
        # 设置颜色标签
        self.log_text.tag_config('timestamp', foreground='gray')
        self.log_text.tag_config(level, foreground=colors.get(level, 'black'))
    
    def on_browse_path(self):
        """浏览选择路径"""
        path = filedialog.askdirectory(title="选择魔兽安装路径")
        if path:
            self.path_var.set(path)
            self.config.set('paths', 'wow_path', value=path)
            self.log(f"选择路径：{path}")
    
    def on_auto_detect(self):
        """自动检测魔兽路径"""
        self.log("正在自动检测魔兽安装路径...")
        paths = self.updater.find_wow_installation()
        
        if paths:
            self.path_var.set(paths[0])
            self.config.set('paths', 'wow_path', value=paths[0])
            self.log(f"✅ 检测到 {len(paths)} 个安装", 'success')
            for path in paths:
                self.log(f"  - {path}", 'info')
        else:
            self.log("❌ 未找到魔兽安装", 'error')
            messagebox.showwarning("未找到", "未能自动检测到魔兽安装路径，请手动选择。")
    
    def on_check_update(self):
        """检查更新按钮处理"""
        self.log("开始检查更新...")
        self.status_var.set("检查更新中...")
        self.check_update_button.config(state=tk.DISABLED)
        
        # 在新线程中执行，避免阻塞 UI
        def check_thread():
            try:
                self.latest_version = self.updater.check_latest_version()
                
                if self.latest_version:
                    self.latest_version_var.set(self.latest_version['version'])
                    
                    # 检测已安装版本
                    wow_path = self.path_var.get() or self.config.get('paths', 'wow_path')
                    current = self.updater.detect_installed_plugin(wow_path)
                    self.current_version_var.set(current or "未检测到")
                    
                    # 对比版本
                    if current and self.latest_version['version'] > current:
                        self.status_var.set("✅ 发现新版本!")
                        self.log(f"发现新版本：{self.latest_version['version']}", 'success')
                        self.update_button.config(state=tk.NORMAL)
                        self.download_path = None  # 重置下载路径
                        
                        # 查找下载链接
                        for asset in self.latest_version['assets']:
                            if asset['name'].endswith('.zip'):
                                self.download_path = asset['browser_download_url']
                                break
                    else:
                        self.status_var.set("已是最新版本", 'success')
                        self.log("已是最新版本", 'success')
                        self.update_button.config(state=tk.DISABLED)
                else:
                    self.status_var.set("检查失败")
                    self.log("无法获取版本信息", 'error')
                    
            except Exception as e:
                self.status_var.set("检查失败")
                self.log(f"检查更新失败：{e}", 'error')
            finally:
                self.check_update_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
    
    def on_update(self):
        """立即更新按钮处理"""
        if not self.download_path:
            messagebox.showerror("错误", "未找到下载地址")
            return
        
        wow_path = self.path_var.get()
        if not wow_path:
            messagebox.showerror("错误", "请先选择魔兽安装路径")
            return
        
        if not messagebox.askyesno("确认", f"确定要更新到 {self.latest_version['version']} 吗？"):
            return
        
        self.log("开始下载更新...")
        self.status_var.set("下载中...")
        self.progress_var.set(0)
        self.update_button.config(state=tk.DISABLED)
        
        # 下载线程
        def download_thread():
            try:
                # 下载
                local_path = self.updater.download_update(
                    self.download_path,
                    lambda p: self.progress_var.set(p)
                )
                
                if not local_path:
                    raise Exception("下载失败")
                
                self.log(f"✅ 下载完成：{local_path}", 'success')
                self.status_var.set("安装中...")
                
                # 备份
                if self.config.get('features', 'backup_before_update'):
                    self.log("正在备份当前版本...")
                    self.updater.backup_current_plugin(wow_path)
                
                # 安装
                self.log("正在安装更新...")
                success = self.updater.install_update(
                    local_path,
                    wow_path,
                    lambda p: self.progress_var.set(50 + p * 0.5)
                )
                
                if success:
                    self.progress_var.set(100)
                    self.status_var.set("✅ 更新完成!", 'success')
                    self.log("更新成功！请重启游戏。", 'success')
                    messagebox.showinfo("成功", "更新已完成！请重启魔兽世界。")
                else:
                    raise Exception("安装失败")
                    
            except Exception as e:
                self.status_var.set("更新失败")
                self.log(f"更新失败：{e}", 'error')
                messagebox.showerror("更新失败", str(e))
            finally:
                self.update_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def on_settings(self):
        """设置按钮处理"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x300")
        
        # 自动检查更新
        auto_check_var = tk.BooleanVar(value=self.config.get('app', 'auto_check'))
        auto_check_cb = ttk.Checkbutton(
            settings_window,
            text="启动时自动检查更新",
            variable=auto_check_var,
            command=lambda: self.config.set('app', 'auto_check', value=auto_check_var.get())
        )
        auto_check_cb.pack(pady=5, anchor=tk.W)
        
        # 更新前备份
        backup_var = tk.BooleanVar(value=self.config.get('features', 'backup_before_update'))
        backup_cb = ttk.Checkbutton(
            settings_window,
            text="更新前自动备份",
            variable=backup_var,
            command=lambda: self.config.set('features', 'backup_before_update', value=backup_var.get())
        )
        backup_cb.pack(pady=5, anchor=tk.W)
        
        # 清理缓存按钮
        clear_cache_btn = ttk.Button(
            settings_window,
            text="清理缓存",
            command=lambda: self.clear_cache()
        )
        clear_cache_btn.pack(pady=10)
        
        # GitHub 仓库配置（高级）
        ttk.Label(settings_window, text="GitHub 仓库 (格式：user/repo):").pack(pady=(20, 5))
        repo_var = tk.StringVar(value=self.config.get('github', 'repo'))
        repo_entry = ttk.Entry(settings_window, textvariable=repo_var, width=40)
        repo_entry.pack()
        
        def save_repo():
            self.config.set('github', 'repo', value=repo_var.get())
            settings_window.destroy()
        
        save_btn = ttk.Button(settings_window, text="保存", command=save_repo)
        save_btn.pack(pady=10)
    
    def clear_cache(self):
        """清理缓存"""
        try:
            cache_dir = Path(self.config.config['paths']['cache_dir'])
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir()
                self.log("✅ 缓存已清理", 'success')
                messagebox.showinfo("完成", "缓存已清理")
        except Exception as e:
            self.log(f"清理缓存失败：{e}", 'error')
    
    def auto_check_update(self):
        """启动时自动检查更新"""
        if self.config.get('app', 'auto_check'):
            last_check = self.config.get('app', 'last_check')
            
            if last_check:
                last_check_date = datetime.fromisoformat(last_check)
                days_since = (datetime.now() - last_check_date).days
                
                if days_since >= self.config.get('app', 'check_interval_days'):
                    self.log("到达检查周期，自动检查更新...")
                    self.on_check_update()
                    
                    # 更新最后检查时间
                    self.config.set('app', 'last_check', value=datetime.now().isoformat())
            else:
                # 第一次运行
                self.log("首次运行，检查更新...")
                self.on_check_update()
                self.config.set('app', 'last_check', value=datetime.now().isoformat())
    
    def show_release_notes(self):
        """显示更新日志"""
        if self.latest_version:
            notes_window = tk.Toplevel(self.root)
            notes_window.title("更新日志")
            notes_window.geometry("500x400")
            
            text = scrolledtext.ScrolledText(notes_window, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text.insert(tk.END, self.latest_version.get('body', '无更新日志'))
            text.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("提示", "请先检查更新")
    
    def show_help(self):
        """显示帮助"""
        help_text = """
有爱插件 Mac 更新器 - 使用说明

1. 首次使用:
   - 点击"自动检测"或手动选择魔兽安装路径
   - 点击"检查更新"

2. 更新插件:
   - 检测到新版本后，"立即更新"按钮会启用
   - 点击即可自动下载安装

3. 自动检查:
   - 默认每周一检查一次
   - 可在设置中调整

4. 注意事项:
   - 需要网络连接
   - 更新前会自动备份
   - 更新后请重启游戏

如有问题，请访问 GitHub 仓库。
        """
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于"""
        about_text = f"""
有爱插件 Mac 更新器
版本：{self.config.get('app', 'version')}

为 Mac 玩家提供的有爱插件自动更新工具

GitHub: https://github.com/YOUR_USERNAME/youai_updater

© 2026 | 用爱发电 ❤️
        """
        messagebox.showinfo("关于", about_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = UpdaterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
