# ❤️ 有爱插件 Mac 更新器

为 Mac 玩家提供的网易有爱插件自动更新工具，通过 GitHub Actions 实现每周自动打包发布。

## 📖 项目说明

由于网易有爱官网没有提供 Mac 版本，本项目通过以下方式解决：

1. **GitHub Actions** - 每周一在 Windows 环境自动打包有爱插件
2. **GitHub Releases** - 存储发布的插件文件
3. **Mac 更新器** - 提供 GUI 界面，一键下载安装

## 🎯 功能特性

- ✅ **自动打包** - 每周一上午 10 点自动执行
- ✅ **GUI 界面** - 简洁易用，双击即可运行
- ✅ **智能检测** - 自动扫描魔兽安装路径
- ✅ **安全备份** - 更新前自动备份，支持回滚
- ✅ **增量更新** - 只下载必要的文件
- ✅ **版本管理** - 保留最近 5 个版本

## 📁 项目结构

```
youai_updater/
├── .github/workflows/
│   └── auto-release.yml        # GitHub Actions 工作流
├── scripts/
│   ├── check_version.py        # 版本检测脚本
│   └── build_app.sh            # 封装 .app 脚本
├── src/
│   ├── updater.py              # 主程序（GUI+ 逻辑）
│   └── update_helper.sh        # 辅助脚本
├── requirements.txt            # Python 依赖
└── README.md                   # 本文件
```

## 🚀 使用方法

### 方式一：直接使用（推荐）

1. **下载应用**
   - 访问 [Releases 页面](https://github.com/codejorker/youai_updater/releases)
   - 下载最新版本的 `YouAiUpdater.dmg` 或 `.zip`

2. **安装运行**
   ```bash
   # 挂载 DMG
   open YouAiUpdater.dmg
   
   # 拖拽到 Applications 文件夹
   # 或直接双击运行
   ```

3. **使用更新器**
   - 打开"有爱插件更新器"
   - 点击"自动检测"选择魔兽路径
   - 点击"检查更新"
   - 点击"立即更新"

### 方式二：源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/codejorker/youai_updater.git
cd youai_updater

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 运行程序
python3 src/updater.py
```

### 方式三：封装为 .app

```bash
# 1. 执行封装脚本
chmod +x scripts/build_app.sh
./scripts/build_app.sh

# 2. 生成的应用在 dist/有爱插件更新器.app
open dist/有爱插件更新器.app
```

## ⚙️ GitHub Actions 配置

### 定时任务

- **时间**: 每周一上午 10:00 (北京时间)
- **触发**: 也支持手动触发

### 工作流程

```yaml
1. 检测最新版本
2. 下载有爱插件安装包
3. 解压提取 Interface/AddOns
4. 打包成 ZIP
5. 发布到 GitHub Releases
6. 清理旧版本（保留 5 个）
```

### 修改仓库配置

在 `src/updater.py` 中修改：

```python
'github': {
    'repo': 'codejorker/youai_updater',  # 改成你的仓库
}
```

## 📝 使用说明

### 首次使用

1. **选择魔兽路径**
   - 点击"自动检测"让程序自动查找
   - 或点击"浏览..."手动选择

2. **检查更新**
   - 点击"检查更新"按钮
   - 程序会对比当前版本和最新版本

3. **开始更新**
   - 如果有新版本，"立即更新"按钮会启用
   - 点击即可自动下载安装

### 设置选项

- **启动时自动检查** - 默认开启
- **更新前自动备份** - 默认开启
- **清理缓存** - 释放磁盘空间

## 🔧 技术细节

### 版本检测策略

由于官网可能无法直接获取版本信息，采用以下策略：

1. **第三方网站** - 从游侠网、多多软件站等获取版本号
2. **时间戳策略** - 如果无法获取，使用 `weekly-YYYYMMDD` 格式
3. **手动触发** - 作为补充

### 文件校验

- SHA256 哈希校验确保文件完整性
- 每个 Release 附带校验文件

### 备份机制

- 更新前自动备份到：`~/Library/Application Support/YouAiUpdater/Backups`
- 保留最近 3 次备份
- 支持手动恢复

## 📸 界面预览

```
┌─────────────────────────────────────────┐
│  ❤️ 有爱插件 Mac 更新器                  │
│     自动更新工具 - 每周一检查更新        │
├─────────────────────────────────────────┤
│  版本信息                                │
│  当前安装：v1.1.8                       │
│  最新版本：v1.1.9 ✅                    │
│  状态：就绪                             │
│  [████████████████] 100%                │
├─────────────────────────────────────────┤
│  魔兽安装路径                            │
│  [/Applications/World of Warcraft] [浏览]│
├─────────────────────────────────────────┤
│  [🔍检查更新] [⬇️立即更新] [⚙️设置]      │
├─────────────────────────────────────────┤
│  更新日志                                │
│  [10:00:00] 开始检查更新...             │
│  [10:00:01] ✅ 发现新版本：v1.1.9       │
│                                         │
└─────────────────────────────────────────┘
```

## 🛠️ 开发相关

### 构建要求

- Python 3.9+
- macOS 10.14+
- Xcode Command Line Tools

### 依赖库

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyinstaller>=6.0.0  # 仅打包时需要
```

### 测试流程

1. 本地运行测试
   ```bash
   python3 src/updater.py
   ```

2. 测试 GitHub Actions
   ```bash
   # 手动触发工作流
   gh workflow run auto-release.yml
   ```

3. 测试安装包
   - 在测试环境验证安装流程

## ❓ 常见问题

### Q: 为什么检测不到版本？

A: 官网可能使用了动态加载，程序会从第三方网站获取信息。如果都失败，会使用周更策略。

### Q: 更新失败怎么办？

A: 
1. 检查网络连接
2. 确认魔兽路径正确
3. 查看日志区域的错误信息
4. 使用备份恢复功能

### Q: 可以自定义更新频率吗？

A: 可以在设置中调整，或修改 GitHub Actions 的 cron 表达式。

### Q: 支持怀旧服吗？

A: 支持！程序会自动检测 `_retail_` 和 `_classic_` 目录。

## 📄 许可证

本项目仅供学习交流使用。

- 有爱插件版权归网易所有
- 本工具仅方便 Mac 用户使用
- 请勿用于商业用途

## 🙏 致谢

- 网易有爱插件团队
- GitHub Actions 提供免费 CI/CD
- 开源社区的优秀库

## 📮 反馈与支持

如有问题或建议，请：

1. 提交 [Issue](https://github.com/codejorker/youai_updater/issues)
2. 加入讨论群
3. 邮件联系

---

**用爱发电 ❤️ | 为 Mac 玩家服务**

*最后更新：2026-03-22*
