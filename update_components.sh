#!/bin/bash

# Crystal3D 组件更新脚本
# 用于更新项目中的各种组件和依赖

set -e

echo "🔄 开始更新 Crystal3D 组件..."

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 更新 Python 依赖
echo "📦 更新 Python 依赖包..."
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# 更新前端静态资源
echo "🌐 检查前端资源更新..."
if [ -d "static/js/three" ]; then
    echo "✅ Three.js 资源已存在"
else
    echo "⚠️  Three.js 资源缺失，请手动下载"
fi

if [ -d "static/css/bootstrap" ]; then
    echo "✅ Bootstrap 资源已存在"
else
    echo "⚠️  Bootstrap 资源缺失，请手动下载"
fi

# 检查 USD 工具
echo "🔧 检查 USD 工具状态..."
if command -v usdzconvert &> /dev/null; then
    echo "✅ Apple USD 工具已安装"
else
    echo "⚠️  Apple USD 工具未安装，请运行 scripts/install_apple_usd_tools.py"
fi

# 检查 Pixar USD
if python -c "import pxr" &> /dev/null; then
    echo "✅ Pixar USD 已安装"
else
    echo "⚠️  Pixar USD 未安装，请参考文档安装"
fi

# 更新版本信息
echo "📋 更新组件版本信息..."
python -c "
import utils.app_version as av
print('当前版本信息:')
for name, info in av.get_all_component_versions().items():
    status = '✅' if info['available'] else '❌'
    print(f'{status} {name}: {info["version"]}')
"

# 清理缓存
echo "🧹 清理缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

echo "✅ 组件更新完成！"
echo ""
echo "📝 下一步建议："
echo "   1. 运行 python main.py 启动服务"
echo "   2. 访问 http://localhost:5000 测试功能"
echo "   3. 如有问题，请检查日志文件"