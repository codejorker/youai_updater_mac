# 码云 Gitee 部署指南

## 🎯 为什么使用码云？

- ✅ 国内访问速度快
- ✅ 中文界面友好
- ✅ Releases 下载速度快
- ✅ 免费私有仓库

## ⚠️ 注意事项

由于本项目依赖 **GitHub Actions 的 Windows 环境**进行自动打包，建议采用以下方案：

### 推荐方案：双仓库同步

```
GitHub (主仓库)          码云 (镜像仓库)
    ↓                        ↓
├─ 代码仓库              ├─ 代码镜像
├─ Actions 打包           ├─ 快速下载
└─ Release 存储           └─ 国内加速
```

---

## 📋 部署步骤

### 第一步：创建码云仓库

1. 访问：https://gitee.com/new
2. 仓库名：`youai_updater_mac`
3. 可见性：公开或私有均可
4. 点击"创建"

### 第二步：推送到码云

```bash
cd /Users/zhanghu/youai_updater

# 添加码云远程仓库
git remote add gitee https://gitee.com/YOUR_USERNAME/youai_updater_mac.git

# 推送到码云
git push -u gitee main
```

### 第三步：配置自动同步（可选）

在码云仓库设置中：
1. 进入「管理」→「基本设置」
2. 找到「同步功能」
3. 绑定 GitHub 账号
4. 开启自动同步

或者手动同步：
```bash
# 从 GitHub 拉取最新代码
git pull origin main

# 推送到码云
git push gitee main
```

---

## 🔄 修改项目配置

### 1. 修改 updater.py 中的配置

打开 `src/updater.py`，找到第 36 行附近：

```python
'github': {
    'repo': 'codejorker/youai_updater_mac',  # 保持不变（用于 Actions）
    'api_base': 'https://api.github.com/repos'
},
'download': {
    'mirror': 'gitee',  # 新增：下载源选择
    'gitee_url': 'https://gitee.com/YOUR_USERNAME/youai_updater_mac/releases/download'
}
```

### 2. 添加 Gitee 下载逻辑

在 `src/updater.py` 的 `check_latest_version()` 方法中添加：

```python
def check_latest_version(self):
    """从 GitHub API 获取最新版本信息"""
    try:
        repo = self.config.get('github', 'repo')
        
        # 优先从码云获取（如果配置了）
        if self.config.get('download', 'mirror') == 'gitee':
            gitee_user = 'YOUR_USERNAME'
            gitee_repo = 'youai_updater_mac'
            api_url = f"https://gitee.com/api/v5/repos/{gitee_user}/{gitee_repo}/releases/latest"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'version': data.get('tag_name', ''),
                'name': data.get('name', ''),
                'url': data.get('html_url', ''),
                'assets': data.get('assets', []),
                'published_at': data.get('created_at', ''),
                'body': data.get('body', '')
            }
        
        # 否则从 GitHub 获取
        api_url = f"{self.config.get('github', 'api_base')}/{repo}/releases/latest"
        # ... 原有代码
```

---

## 🚀 完整工作流程

### 代码更新流程

```bash
# 1. 本地修改代码
git add .
git commit -m "修复 bug"

# 2. 推送到 GitHub（触发 Actions）
git push origin main

# 3. 同步到码云
git push gitee main
```

### 自动打包流程

```
GitHub Actions (每周一)
    ↓
打包插件 → 发布到 GitHub Releases
    ↓
自动/手动同步到码云 Releases
```

### Mac 用户下载流程

```
Mac 更新器
    ↓
检查码云/GitHub Releases
    ↓
从快的源下载
```

---

## 📝 简化方案（推荐新手）

如果你觉得双仓库太复杂，可以：

### 只用码云 + 手动打包

1. **在本地 Windows 电脑打包**（或找朋友帮忙）
2. **手动上传到码云 Releases**
3. **Mac 更新器从码云下载**

这样就不需要 GitHub Actions 了，但需要手动操作。

---

## 🔧 纯码云方案（不推荐）

如果你坚持完全使用码云：

### 限制

- ❌ 码云 CI/CD 没有免费的 Windows 环境
- ❌ 需要自己准备 Windows 机器打包
- ✅ 适合手动打包发布

### 步骤

1. **手动打包插件**
   - 在 Windows 电脑下载安装包
   - 提取 Interface/AddOns
   - 压缩成 ZIP

2. **上传到码云 Releases**
   - 访问：https://gitee.com/YOUR_USERNAME/youai_updater_mac/releases
   - 新建 Release
   - 上传文件

3. **修改更新器配置**
   - 指向码云 API

---

## 💡 我的建议

基于你的需求（Mac 用户 + 自动更新），我强烈推荐：

### GitHub Actions + 码云镜像

**优点**：
- ✅ 自动打包（利用 GitHub 免费 Windows 环境）
- ✅ 代码托管在码云（访问快）
- ✅ Releases 同步到码云（下载快）
- ✅ 两全其美

**操作流程**：
```bash
# 一次性配置
git remote add gitee https://gitee.com/YOUR_USERNAME/youai_updater_mac.git

# 每次更新代码时
git push origin main    # 推送到 GitHub（触发 Actions）
git push gitee main     # 推送到码云（国内访问）
```

---

## ❓ 常见问题

### Q: 可以只用码云吗？

A: 可以，但需要手动打包。码云没有免费的 Windows CI 环境。

### Q: GitHub Actions 会被墙吗？

A: 偶尔会慢，但通常能访问。Actions 执行不受影响。

### Q: 需要同步两个仓库吗？

A: 建议同步，保持代码一致。可以设置自动同步或手动同步。

### Q: Mac 更新器从哪里下载？

A: 
- 方案 1：从码云 Releases 下载（推荐，速度快）
- 方案 2：从 GitHub Releases 下载（备选）

---

## 🎯 下一步

如果你决定使用码云，请告诉我：

1. 你的码云用户名是什么？
2. 是否创建了码云仓库？
3. 需要我帮你修改配置文件吗？

我可以立即帮你：
- 修改所有配置文件指向码云
- 添加双仓库同步脚本
- 配置自动同步

---

**你觉得哪个方案更适合你？** 😊
