#!/bin/bash
# 本地USD环境配置脚本

# 获取脚本所在目录
BASEPATH=$(dirname "$0")

# 设置环境变量
export PATH="$PATH:$BASEPATH/usdzconvert"
export PYTHONPATH="$PYTHONPATH:$BASEPATH/usdzconvert"

# 设置PXR插件路径以避免冲突
export PXR_PLUGINPATH_NAME="$BASEPATH/usdzconvert"

# 使用系统的usdpython环境来运行工具
# 因为本地环境缺少完整的USD库文件
echo "使用系统usdpython环境运行usdARKitChecker..."
cd /Applications/usdpython
source USD.command
export PXR_PLUGINPATH_NAME="/Applications/usdpython/usdzconvert"

# 运行验证工具
if [ $# -eq 0 ]; then
    echo "用法: $0 <usdz文件路径>"
    echo "示例: $0 /path/to/file.usdz"
else
    usdARKitChecker "$1"
fi