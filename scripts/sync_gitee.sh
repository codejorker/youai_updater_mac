#!/bin/bash
# 双仓库同步脚本 - GitHub + Gitee

set -e

echo "======================================"
echo "有爱插件更新器 - 双仓库同步"
echo "======================================"
echo ""

# 检查是否配置了码云远程仓库
if ! git remote | grep -q gitee; then
    echo "❌ 未配置码云远程仓库"
    echo ""
    read -p "请输入你的码云用户名：" gitee_user
    git remote add gitee https://gitee.com/$gitee_user/youai_updater_mac.git
    echo "✅ 已添加码云远程仓库"
fi

echo ""
echo "📊 当前远程仓库:"
git remote -v
echo ""

# 获取最新代码
echo "🔄 正在从 GitHub 拉取最新代码..."
git pull origin main

# 推送到码云
echo "🚀 正在推送到码云..."
git push gitee main

echo ""
echo "======================================"
echo "✨ 同步完成！"
echo "======================================"
echo ""
echo "GitHub: https://github.com/codejorker/youai_updater_mac"
echo "Gitee:  https://gitee.com/YOUR_USERNAME/youai_updater_mac"
echo ""
