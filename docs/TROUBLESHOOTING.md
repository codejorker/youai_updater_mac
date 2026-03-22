# GitHub Actions 故障排查指南

## 📊 当前状态

根据检查，你的仓库有以下运行记录：

### 失败的运行
- ✅ **运行次数**: 5 次
- ❌ **全部失败**: failure
- 📅 **最近一次**: 2026-03-22T17:26:39Z

### 失败的工作流
1. **Python package** - 失败（这是 GitHub 自动创建的）
2. **🎁 有爱插件自动打包** - 失败（这个是我们需要的）

---

## 🔧 常见问题及解决方案

### 问题 1: Workflows 未启用

**症状**: 
- API 返回 "Workflow does not have 'workflow_dispatch' trigger"
- 页面显示需要启用

**解决**:
1. 访问：https://github.com/codejorker/youai_updater_mac/actions/new
2. 点击绿色按钮："I understand my workflows, go ahead and enable them"

---

### 问题 2: 权限不足

**症状**:
- 403 Forbidden
- Token 权限错误

**解决**:
1. 访问：https://github.com/settings/tokens
2. 编辑你的 Token
3. 确保勾选了这些权限：
   - ✅ `repo` (完全控制)
   - ✅ `workflow` (更新工作流文件)
   - ✅ `admin:repo_hook` (管理钩子)

---

### 问题 3: 工作流配置错误

**症状**:
- YAML 语法错误
- 步骤执行失败

**检查清单**:
```bash
# 在本地验证 YAML 语法
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/auto-release.yml'))"
```

常见错误：
- ❌ 缩进不正确（必须用空格，不能用 Tab）
- ❌ 缺少必要的字段
- ❌ 引用了不存在的 Action

---

### 问题 4: Windows 环境问题

**症状**:
- `runs-on: windows-latest` 失败
- 找不到 7z 或其他工具

**解决**:
检查工作流中是否正确安装了必要工具：
```yaml
- name: 安装 7-Zip
  run: choco install 7zip -y
```

---

### 问题 5: 网络超时

**症状**:
- 下载有爱插件超时
- curl 或 requests 失败

**解决**:
增加超时时间或使用镜像源：
```yaml
- name: 下载有爱插件
  run: |
    # 使用国内镜像或备用下载地址
    curl --connect-timeout 30 --retry 3 $DOWNLOAD_URL
```

---

## 🎯 立即查看详细日志

### 方法 1: 在 GitHub 页面查看（推荐）

1. **访问运行记录页面**:
   ```
   https://github.com/codejorker/youai_updater_mac/actions/runs/23408445482
   ```

2. **点击具体的任务**:
   - 找到 "check-and-package"
   - 点击查看详情

3. **展开每个步骤**:
   - 查看哪个步骤失败了
   - 阅读错误信息

### 方法 2: 使用 CLI 工具

```bash
# 安装 GitHub CLI
brew install gh

# 查看运行日志
gh run view 23408445482 --log
```

---

## 💡 快速修复方案

### 方案 A: 删除 Python package 工作流

GitHub 自动创建的那个可能会干扰，可以删除它：

```bash
cd /Users/zhanghu/youai_updater
rm .github/workflows/python-package.yml 2>/dev/null || true
git add -A
git commit -m "删除自动创建的 Python 工作流"
git push origin main
```

### 方案 B: 简化自动打包工作流

创建一个更简单的版本测试：

```yaml
name: 🎁 有爱插件自动打包（简化版）

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: 测试环境
      run: |
        echo "✅ Windows 环境正常"
        echo "Runner: ${{ runner.os }}"
        
    - name: 创建测试文件
      run: |
        mkdir output
        echo "测试成功" > output/test.txt
        
    - name: 上传测试文件
      uses: actions/upload-artifact@v4
      with:
        name: test-output
        path: output/
```

### 方案 C: 手动创建第一个 Release

如果 Actions 一直失败，可以手动创建：

1. 访问：https://github.com/codejorker/youai_updater_mac/releases/new
2. Tag version: `plugin-v1.0.0`
3. Title: `有爱插件 v1.0.0`
4. 上传一个测试文件（暂时跳过）
5. 点击 "Publish release"

---

## 📞 需要更多信息

请告诉我：

1. **你在 GitHub 页面看到什么错误？**
   - 访问：https://github.com/codejorker/youai_updater_mac/actions
   - 点击红色的失败记录
   - 截图或复制错误信息

2. **具体哪个步骤失败？**
   - 是检出代码？
   - 下载插件？
   - 还是发布 Release？

3. **错误信息是什么？**
   - 404 Not Found？
   - 超时 Timeout？
   - 还是其他？

---

**把具体的错误信息发给我，我能给你更精确的解决方案！** 😊
