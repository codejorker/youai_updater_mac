#!/bin/bash
# 有爱插件 Mac 更新器 - 封装为 .app 应用脚本

set -e

echo "======================================"
echo "有爱插件 Mac 更新器 - 封装工具"
echo "======================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 安装依赖
echo ""
echo "📦 正在安装 Python 依赖..."
pip3 install -r requirements.txt

# 安装 PyInstaller
echo ""
echo "📦 正在安装 PyInstaller..."
pip3 install pyinstaller

# 创建应用图标（可选）
ICON_PATH="./src/assets/icon.icns"
if [ ! -f "$ICON_PATH" ]; then
    echo ""
    echo "⚠️ 警告：未找到应用图标 $ICON_PATH"
    echo "   将继续使用默认图标"
fi

# 清理之前的构建
echo ""
echo "🧹 清理旧的构建文件..."
rm -rf build dist __pycache__

# 使用 PyInstaller 打包
echo ""
echo "🔨 开始打包..."
pyinstaller --windowed \
    --name "有爱插件更新器" \
    --icon="$ICON_PATH" \
    --add-data "src/update_helper.sh:." \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --osx-bundle-identifier=com.youai.updater \
    --clean \
    src/updater.py

# 检查是否成功
if [ -d "dist/有爱插件更新器.app" ]; then
    echo ""
    echo "✅ 打包成功！"
    echo ""
    echo "📦 应用位置：dist/有爱插件更新器.app"
    echo ""
    
    # 显示文件大小
    APP_SIZE=$(du -sh "dist/有爱插件更新器.app" | cut -f1)
    echo "📊 应用大小：$APP_SIZE"
    echo ""
    
    # 创建 DMG（如果安装了 create-dmg）
    if command -v create-dmg &> /dev/null; then
        echo "📀 正在创建 DMG 安装包..."
        create-dmg \
            --volname "有爱插件更新器" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --icon "有爱插件更新器.app" 175 120 \
            --hide-extension "有爱插件更新器.app" \
            --app-drop-link 425 120 \
            "YouAiUpdater.dmg" \
            "dist/有爱插件更新器.app"
        
        echo "✅ DMG 已创建：YouAiUpdater.dmg"
    else
        echo "ℹ️ 提示：安装 create-dmg 可创建 DMG 安装包"
        echo "   brew install create-dmg"
    fi
    
    echo ""
    echo "======================================"
    echo "✨ 完成！"
    echo "======================================"
    echo ""
    echo "下一步:"
    echo "1. 测试运行：open dist/有爱插件更新器.app"
    echo "2. 发布到 GitHub Releases"
    echo ""
else
    echo ""
    echo "❌ 打包失败！请检查错误信息"
    exit 1
fi
