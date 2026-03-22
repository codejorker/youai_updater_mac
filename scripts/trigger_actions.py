#!/usr/bin/env python3
"""手动触发 GitHub Actions"""

import requests

TOKEN = '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'
REPO = 'codejorker/youai_updater_mac'
WORKFLOW_ID = '249714746'  # auto-release.yml 的 ID

url = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

data = {'ref': 'main'}

print(f"🔍 正在触发 Actions...")
print(f"URL: {url}")

response = requests.post(url, headers=headers, json=data)

print(f"\n状态码：{response.status_code}")
print(f"响应内容：{response.text}")

if response.status_code == 204:
    print("\n✅ Actions 触发成功！")
    print("请访问 https://github.com/codejorker/youai_updater_mac/actions 查看进度")
else:
    print(f"\n❌ 触发失败：{response.status_code}")
    print("\n建议:")
    print("1. 在浏览器访问：https://github.com/codejorker/youai_updater_mac/actions")
    print("2. 点击 'I understand my workflows, go ahead and enable them' 按钮（如果有）")
    print("3. 然后点击 'Run workflow' 按钮")
