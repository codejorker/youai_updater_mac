# 📦 手动打包指南

如果 GitHub Actions 无法触发，可以使用此方法手动打包。

## 方法一：在 Windows 电脑本地打包

### 步骤：

1. **下载有爱插件安装包**
   - 访问：https://dd.163.com
   - 或使用第三方下载站（游侠网、多多网等）
   - 下载最新版本

2. **解压安装包**
   ```powershell
   # 使用 7-Zip 解压
   7z x YouAiSetup.exe -o./extracted -y
   ```

3. **提取 Interface文件夹**
   ```powershell
   # 查找并复制 Interface文件夹
   $interface = Get-ChildItem -Path ./extracted -Recurse -Directory -Filter "Interface" | Select-Object -First 1
   Copy-Item -Path "$($interface.FullName)\*" -Destination "./output/Interface" -Recurse
   ```

4. **生成说明文件**
   ```powershell
   @"
   =====================================
   有爱插件 Mac 更新器 - 手动打包版本
   =====================================
   
   📦 版本号：manual-20260322
   🕐 打包时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
   🖥️ 打包环境：手动打包
   
   📁 内容说明:
   - Interface/AddOns/: 包含所有有爱插件文件
   
   📝 使用说明:
   1. 将 Interface文件夹复制到你的魔兽安装目录
   2. 路径示例：/Applications/World of Warcraft/_retail_/Interface/
   
   =====================================
   "@ | Out-File -FilePath "./output/README.txt" -Encoding UTF8
   ```

5. **压缩成 ZIP**
   ```powershell
   Compress-Archive -Path "./output/*" -DestinationPath "youai-plugin-manual-20260322.zip" -Force
   ```

6. **计算 SHA256**
   ```powershell
   Get-FileHash "youai-plugin-manual-20260322.zip" -Algorithm SHA256 | Format-List
   ```

7. **上传到 Releases**
   - GitHub: https://github.com/codejorker/youai_updater_mac/releases/new
   - 码云：https://gitee.com/codejorker/youai_updater_mac/releases/new

---

## 方法二：使用 GitHub Actions 但手动触发

### 问题原因

GitHub Actions 的 `workflow_dispatch` 触发器可能需要先在页面启用。

### 解决步骤

1. **访问 Actions 页面**
   - https://github.com/codejorker/youai_updater_mac/actions

2. **首次使用需要启用**
   - 如果看到绿色按钮 "I understand my workflows, go ahead and enable them"
   - 点击它

3. **然后点击工作流名称**
   - 点击 "🎁 有爱插件自动打包"

4. **现在应该能看到 "Run workflow" 按钮**
   - 点击右上角的 "Run workflow"
   - 选择 `main` 分支
   - 再次点击 "Run workflow"

5. **等待完成**
   - 大约 5-10 分钟
   - 完成后会在 Releases 页面看到发布的文件

---

## 方法三：修改工作流添加更多触发方式

如果 `workflow_dispatch` 不工作，可以添加其他触发方式：

### 修改 `.github/workflows/auto-release.yml`

```yaml
on:
  schedule:
    - cron: '0 2 * * 1'
  
  workflow_dispatch:  # 当前这个不工作
  
  push:
    branches:
      - main
    paths:
      - '.github/workflows/trigger.txt'  # 创建这个文件就触发
```

然后创建 `.github/workflows/trigger.txt` 文件并提交推送来触发。

---

## 🎯 推荐方案

**目前最可靠的方法：**

1. 在浏览器访问 GitHub Actions 页面
2. 手动点击 "Run workflow" 按钮
3. 或等待下周一自动执行

---

## ❓ 常见问题

### Q: 为什么 API 触发失败？

A: 可能原因：
- Workflows 未在页面启用
- Token 权限不足
- GitHub 缓存问题

### Q: 能否用其他方式触发？

A: 可以：
- 页面手动点击（推荐）
- 创建特定文件触发（需修改工作流）
- 定时任务自动执行

### Q: 着急使用怎么办？

A: 
1. 找有 Windows 的朋友帮忙打包
2. 或在网吧/学校的 Windows 电脑上操作
3. 使用虚拟机（VMware/VirtualBox）

---

**祝你打包成功！🎉**
