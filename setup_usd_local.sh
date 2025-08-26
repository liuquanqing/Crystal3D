#!/bin/bash
# Crystal3D - USD本地环境一键安装脚本
# 适用于macOS和Linux系统
# 版本: v2.0

set -e  # 遇到错误立即退出

echo "🚀 Crystal3D - USD本地环境一键安装脚本 v2.0"
echo "=============================================="
echo "📋 系统信息: $(uname -s) $(uname -m)"
echo "📅 安装时间: $(date)"
echo "=============================================="
echo

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    echo
    echo "💡 安装指南:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   macOS: brew install python"
        echo "   或访问: https://www.python.org/downloads/"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "   或访问: https://www.python.org/downloads/"
    fi
    echo
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 检查Python版本是否满足要求 (3.8+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python版本过低，需要Python 3.8+，当前版本: $PYTHON_VERSION"
    echo "💡 请升级Python版本后重新运行此脚本"
    exit 1
fi

# 检查pip
echo "📦 检查pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip不可用，尝试安装..."
    python3 -m ensurepip --upgrade || {
        echo "❌ pip安装失败，请手动安装pip"
        exit 1
    }
fi
echo "✅ pip检查通过"

# 升级pip
echo "📦 升级pip到最新版本..."
python3 -m pip install --upgrade pip --quiet || {
    echo "⚠️  pip升级失败，继续使用当前版本"
}
echo "✅ pip准备就绪"

# 智能依赖安装
echo
echo "📦 智能安装项目依赖..."

# 安装策略：优化 -> 最小 -> 完整 -> 手动
INSTALL_SUCCESS=false

# 1. 尝试优化依赖
if [ -f "requirements_optimal.txt" ]; then
    echo "📌 [1/4] 尝试优化依赖包（生产推荐）..."
    if python3 -m pip install -r requirements_optimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet; then
        echo "✅ 优化依赖安装成功"
        INSTALL_SUCCESS=true
    else
        echo "⚠️  优化依赖安装失败，尝试下一种方案..."
    fi
fi

# 2. 尝试最小依赖
if [ "$INSTALL_SUCCESS" = false ] && [ -f "requirements_minimal.txt" ]; then
    echo "📌 [2/4] 尝试最小依赖包（快速安装）..."
    if python3 -m pip install -r requirements_minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet; then
        echo "✅ 最小依赖安装成功"
        INSTALL_SUCCESS=true
    else
        echo "⚠️  最小依赖安装失败，尝试下一种方案..."
    fi
fi

# 3. 尝试完整依赖
if [ "$INSTALL_SUCCESS" = false ] && [ -f "requirements.txt" ]; then
    echo "📌 [3/4] 尝试完整依赖包..."
    if python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet; then
        echo "✅ 完整依赖安装成功"
        INSTALL_SUCCESS=true
    else
        echo "⚠️  完整依赖安装失败，尝试手动安装核心包..."
    fi
fi

# 4. 手动安装核心包
if [ "$INSTALL_SUCCESS" = false ]; then
    echo "📌 [4/4] 手动安装核心包（最后备用方案）..."
    if python3 -m pip install fastapi uvicorn python-multipart aiofiles ase pillow loguru qrcode -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet; then
        echo "✅ 核心包安装成功"
        INSTALL_SUCCESS=true
    fi
fi

# 检查安装结果
if [ "$INSTALL_SUCCESS" = false ]; then
    echo "❌ 所有安装方式都失败"
    echo
    echo "💡 故障排除指南:"
    echo "   1. 检查网络连接是否正常"
    echo "   2. 升级pip: python3 -m pip install --upgrade pip"
    echo "   3. 清理pip缓存: python3 -m pip cache purge"
    echo "   4. 使用虚拟环境:"
    echo "      python3 -m venv venv"
    echo "      source venv/bin/activate"
    echo "      pip install -r requirements_minimal.txt"
    echo "   5. 手动配置清华源:"
    echo "      pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/"
    echo "   6. 重新运行此脚本"
    echo
    echo "📞 如需技术支持，请查看README.md或提交Issue"
    exit 1
else
    echo "✅ 依赖安装完成！"
fi

# 验证核心库安装
echo
echo "🔍 验证核心库安装..."

# 验证Web框架
if python3 -c "import fastapi, uvicorn; print('✅ Web框架验证成功')" 2>/dev/null; then
    echo "✅ Web框架 (FastAPI/Uvicorn) 安装成功"
else
    echo "⚠️  Web框架验证失败"
fi

# 验证材料科学库
if python3 -c "import ase; print('✅ 材料科学库验证成功')" 2>/dev/null; then
    echo "✅ 材料科学库 (ASE) 安装成功"
else
    echo "⚠️  材料科学库验证失败，部分功能可能受限"
fi

# 验证USD库（可选）
if python3 -c "from pxr import Usd; print('✅ USD库验证成功')" 2>/dev/null; then
    echo "✅ USD库安装并验证成功"
else
    echo "⚠️  USD库验证失败，如需USD功能请手动安装: pip install usd-core"
fi

# 测试验证工具
echo "🧪 测试验证工具..."
if [ -f "usd_checker.py" ]; then
    chmod +x usd_checker.py
    echo "✅ USD验证工具准备就绪"
    echo "📖 使用方法: python3 usd_checker.py <usdz文件路径>"
else
    echo "⚠️  usd_checker.py未找到"
fi

# 显示安装信息
echo
echo "🎉 Crystal3D安装完成！"
echo "========================"
echo "📖 快速启动:"
echo "   ./一键启动.bat                     # Windows用户"
echo "   python3 main.py                    # 直接启动"
echo "   chmod +x setup_usd_local.sh && ./setup_usd_local.sh  # 重新安装"
echo
echo "🌐 服务地址:"
echo "   Web界面: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   移动端: http://localhost:8000 (手机浏览器)"
echo
echo "💡 功能特性:"
echo "   ✓ 支持拖拽上传CIF文件"
echo "   ✓ 自动3D预览晶体结构"
echo "   ✓ 一键转换为USDZ格式"
echo "   ✓ iPhone扫码AR预览"
echo
echo "🔧 USD验证工具 (可选):"
echo "   usdview --help                     # USD查看器帮助"
echo "   usdcat --help                      # USD文件工具帮助"
echo
echo "📋 安装信息:"
echo "   Python版本: $PYTHON_VERSION"
echo "   安装时间: $(date)"
echo "   系统信息: $(uname -s) $(uname -m)"
echo "   脚本版本: v2.0"
echo
echo "📞 技术支持:"
echo "   README.md - 详细文档"
echo "   GitHub Issues - 问题反馈"
echo
echo "🚀 现在可以运行 'python3 main.py' 启动服务！"