#!/bin/bash
# 有爱插件 Mac 更新器 - 初始化脚本

set -e

echo "======================================"
echo "有爱插件 Mac 更新器 - 初始化"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 安装依赖
echo "📦 正在安装 Python 依赖..."
pip3 install -r requirements.txt

echo ""
echo "✅ 依赖安装完成！"
echo ""

# Git 配置提示
echo "🔧 接下来请按照以下步骤操作："
echo ""
echo "1️⃣  创建 GitHub 仓库"
echo "   访问：https://github.com/new"
echo "   仓库名：youai_updater"
echo "   可见性：Public（推荐）"
echo ""

echo "2️⃣  初始化 Git 并推送"
echo "   运行以下命令："
echo ""
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit: 有爱插件 Mac 更新器'"
echo "   git remote add origin https://github.com/codejorker/youai_updater.git"
echo "   git push -u origin main"
echo ""

echo "3️⃣  测试 GitHub Actions"
echo "   访问：https://github.com/codejorker/youai_updater/actions"
echo "   点击 '🎁 有爱插件自动打包'"
echo "   点击 'Run workflow' 按钮"
echo ""

echo "4️⃣  本地测试运行（可选）"
echo "   python3 src/updater.py"
echo ""

echo "======================================"
echo "✨ 初始化完成！"
echo "======================================"
echo ""
