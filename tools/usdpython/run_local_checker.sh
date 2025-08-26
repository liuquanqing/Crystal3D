#!/bin/bash
# 纯本地USD环境验证脚本

# 获取脚本所在目录
BASEPATH=$(dirname "$0")

# 设置本地环境变量
export PYTHONPATH="$PYTHONPATH:$BASEPATH/usdzconvert"
export PATH="$PATH:$BASEPATH/usdzconvert"

# 尝试使用本地Python运行usdARKitChecker
echo "尝试使用本地环境运行usdARKitChecker..."

if [ $# -eq 0 ]; then
    echo "用法: $0 <usdz文件路径>"
    echo "示例: $0 /path/to/file.usdz"
    exit 1
fi

# 检查文件是否存在
if [ ! -f "$1" ]; then
    echo "错误: 文件 '$1' 不存在"
    exit 1
fi

# 尝试运行验证
echo "验证文件: $1"
python3 "$BASEPATH/usdzconvert/usdARKitChecker" "$1"
result=$?

if [ $result -eq 0 ]; then
    echo "✅ USDZ文件验证通过"
else
    echo "❌ USDZ文件验证失败 (退出码: $result)"
fi

exit $result