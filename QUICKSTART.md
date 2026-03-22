# 快速开始指南

## 🎯 10 分钟上手

### 第一步：配置 GitHub 仓库（5 分钟）

1. **创建 GitHub 仓库**
   ```bash
   # 访问 https://github.com/new
   # 仓库名：youai_updater
   # 可见性：Public（推荐）
   ```

2. **修改配置文件**
   
   打开 `src/updater.py`，找到第 36 行：
   ```python
   'github': {
       'repo': 'codejorker/youai_updater',  # 改成你的用户名
   },
   ```
   
   将 `YOUR_USERNAME` 替换为你的 GitHub 用户名

3. **修改 Actions 工作流**
   
   打开 `.github/workflows/auto-release.yml`，搜索 `YOUR_USERNAME`，全部替换为你的用户名（共 2 处）

### 第二步：提交到 GitHub（2 分钟）

```bash
# 初始化仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 有爱插件 Mac 更新器"

# 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/codejorker/youai_updater.git

# 推送
git push -u origin main
```

### 第三步：测试 GitHub Actions（3 分钟）

1. **手动触发一次工作流**
   - 访问：https://github.com/codejorker/youai_updater/actions
   - 点击 "🎁 有爱插件自动打包"
   - 点击 "Run workflow" 按钮
   - 等待完成（约 5-10 分钟）

2. **查看 Release**
   - 访问：https://github.com/codejorker/youai_updater/releases
   - 应该能看到新发布的版本

### 第四步：本地测试（可选）

```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行程序
python3 src/updater.py
```

### 第五步：封装为 .app（可选）

```bash
# 执行封装脚本
chmod +x scripts/build_app.sh
./scripts/build_app.sh

# 生成的应用在 dist/有爱插件更新器.app
```

---

## ⚙️ 高级配置

### 修改检查频率

编辑 `src/updater.py` 第 27 行：
```python
'check_interval_days': 7,  # 改为其他数字
```

### 修改打包时间

编辑 `.github/workflows/auto-release.yml` 第 5 行：
```yaml
- cron: '0 2 * * 1'  # 周一 10:00 (UTC+8)
# 格式：分 时 日 月 周
```

### 保留更多版本

编辑 `.github/workflows/auto-release.yml` 第 195 行：
```yaml
keep_latest: 5  # 改为其他数字
```

---

## 🐛 故障排查

### Actions 运行失败

1. 检查 Python 脚本语法
   ```bash
   python3 -m py_compile scripts/check_version.py
   ```

2. 查看错误日志
   - 在 Actions 页面点击失败的 run
   - 展开各个步骤查看详情

### 本地运行报错

1. 检查 Python 版本
   ```bash
   python3 --version  # 需要 3.9+
   ```

2. 重新安装依赖
   ```bash
   pip3 install -r requirements.txt --force-reinstall
   ```

### 检测不到魔兽路径

1. 手动指定路径
   - 点击"浏览..."按钮
   - 选择包含 `_retail_` 或 `_classic_` 的目录

2. 检查权限
   ```bash
   ls -ld /Applications/World\ of\ Warcraft
   ```

---

## 📞 获取帮助

- 查看 [README.md](README.md) 了解更多功能
- 查看 [常见问题](README.md#常见问题)
- 提交 Issue

---

**祝你使用愉快！🎮**
