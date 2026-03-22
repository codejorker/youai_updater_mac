#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有爱插件版本检测脚本
用于从官网或第三方网站获取最新版本信息
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

# 配置项
CONFIG = {
    'official_site': 'https://dd.163.com',
    'third_party_sites': [
        {
            'name': '游侠网',
            'url': 'https://soft.ali213.net/down/739.html',
            'version_pattern': r'最新版本：([0-9.]+)',
            'download_pattern': None  # 需要特殊处理
        },
        {
            'name': '多多软件站',
            'url': 'https://m.ddooo.com/softdown/237309.htm',
            'version_pattern': r'v([0-9.]+)官方版',
            'download_pattern': None
        }
    ],
    'cache_dir': './cache',
    'timeout': 30
}


def check_official_site():
    """
    检查官网获取版本信息
    返回：(version, download_url) 或 (None, None)
    """
    print("🔍 正在检查官网...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(CONFIG['official_site'], headers=headers, timeout=CONFIG['timeout'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试查找版本信息
        # 注意：官网可能使用动态加载，这里可能需要调整
        
        # 查找下载链接
        download_links = soup.find_all('a', href=re.compile(r'download|down'))
        if download_links:
            print(f"✅ 找到 {len(download_links)} 个下载链接")
            # 这里需要根据实际页面结构调整
            
        # 查找版本号
        version_text = soup.find(string=re.compile(r'版本|Version'))
        if version_text:
            print(f"✅ 找到版本信息：{version_text.strip()}")
            
        return None, None  # 暂时返回 None，需要实际测试后调整
        
    except Exception as e:
        print(f"❌ 官网检查失败：{e}")
        return None, None


def check_third_party_site(site_info):
    """
    检查第三方网站获取版本信息
    """
    print(f"🔍 正在检查 {site_info['name']}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(site_info['url'], headers=headers, timeout=CONFIG['timeout'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取版本号
        version = None
        version_pattern = site_info.get('version_pattern')
        
        if version_pattern:
            match = re.search(version_pattern, str(soup))
            if match:
                version = match.group(1)
                print(f"✅ {site_info['name']} - 版本号：{version}")
        
        # 提取下载地址（如果需要）
        download_url = None
        
        return version, download_url
        
    except Exception as e:
        print(f"❌ {site_info['name']} 检查失败：{e}")
        return None, None


def get_latest_release_from_github():
    """
    从 GitHub Releases 获取已发布的最新版本
    """
    try:
        # 需要从环境变量或配置文件获取仓库信息
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        if not repo:
            print("⚠️ 未设置 GITHUB_REPOSITORY 环境变量")
            return None
            
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get('tag_name', '')
            print(f"✅ GitHub 最新版本：{tag_name}")
            return tag_name
        else:
            print(f"⚠️ GitHub API 返回 {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ GitHub 版本检查失败：{e}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("有爱插件版本检测")
    print("=" * 60)
    print(f"🕐 检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 确保缓存目录存在
    os.makedirs(CONFIG['cache_dir'], exist_ok=True)
    
    # 1. 先检查 GitHub 已有版本
    print("📊 步骤 1: 检查 GitHub 已发布版本")
    github_version = get_latest_release_from_github()
    print()
    
    # 2. 检查第三方网站
    print("📊 步骤 2: 检查第三方网站版本")
    latest_version = None
    download_url = None
    
    for site in CONFIG['third_party_sites']:
        version, url = check_third_party_site(site)
        if version and (not latest_version or version > latest_version):
            latest_version = version
            download_url = url
    
    print()
    
    # 3. 如果官网可以获取，检查官网
    print("📊 步骤 3: 检查官网版本")
    official_version, official_url = check_official_site()
    
    if official_version:
        latest_version = official_version
        download_url = official_url
    
    print()
    
    # 4. 对比版本
    print("📊 步骤 4: 版本对比")
    if latest_version and github_version:
        if latest_version > github_version.replace('plugin-', ''):
            print(f"✅ 发现新版本：{latest_version}")
            print(f"   当前版本：{github_version}")
            need_update = True
        else:
            print(f"ℹ️ 已是最新版本：{latest_version}")
            need_update = False
    elif latest_version:
        print(f"✅ 检测到版本：{latest_version}")
        need_update = True
    else:
        print("⚠️ 未能获取版本信息，使用时间戳策略")
        latest_version = f"weekly-{datetime.now().strftime('%Y%m%d')}"
        need_update = True
    
    print()
    
    # 5. 保存版本信息到缓存文件
    print("📊 步骤 5: 保存版本信息")
    version_file = os.path.join(CONFIG['cache_dir'], 'version_info.txt')
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(f"{latest_version}\n")
        f.write(f"{download_url or ''}\n")
    
    print(f"✅ 版本信息已保存到：{version_file}")
    print()
    
    # 6. 输出结果
    print("=" * 60)
    print("检测结果:")
    print(f"  最新版本：{latest_version}")
    print(f"  下载地址：{download_url or 'N/A'}")
    print(f"  需要更新：{'是' if need_update else '否'}")
    print("=" * 60)
    
    return 0 if need_update else 1


if __name__ == '__main__':
    exit(main())
