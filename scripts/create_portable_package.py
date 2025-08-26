#!/usr/bin/env python3
"""
创建CIF转USDZ转换工具便携版本包
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path
import subprocess

def create_portable_package():
    """创建便携版本包"""
    print("📦 创建CIF转USDZ转换工具便携版本包")
    print("=" * 60)
    
    # 定义包目录
    package_name = "CIF转USDZ转换工具-便携版"
    package_dir = Path(package_name)
    
    # 清理旧包
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    print(f"📁 创建包目录: {package_dir}")
    
    # 核心文件和目录
    core_items = [
        # Python文件
        "main.py",
        "requirements.txt", 
        "setup.py",
        
        # 源代码目录
        "api/",
        "converter/", 
        "utils/",
        "static/",
        "examples/",
        
        # 配置和文档
        "README.md",

        "INSTALL_USD_TOOLS.md",
        
        # 工具目录
        "tools/",
        
        # 测试脚本
        "test_system.py",

    ]
    
    # 复制文件
    copied_count = 0
    for item in core_items:
        src = Path(item)
        dst = package_dir / item
        
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst)
                print(f"✅ 复制目录: {item}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"✅ 复制文件: {item}")
            copied_count += 1
        else:
            print(f"⚠️ 跳过不存在的: {item}")
    
    print(f"📊 共复制 {copied_count} 个项目")
    
    # 创建Windows启动脚本
    windows_start = """@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    CIF转USDZ转换工具 - 便携版
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 📦 安装依赖包...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

echo.
echo 🚀 启动CIF转USDZ转换服务...
echo 📖 访问地址: http://localhost:8000
echo 🛑 按Ctrl+C停止服务
echo.

python main.py

echo.
echo 👋 服务已停止
pause
"""
    
    with open(package_dir / "启动.bat", "w", encoding="utf-8") as f:
        f.write(windows_start)
    
    # 创建Linux/macOS启动脚本
    unix_start = """#!/bin/bash
echo "========================================"
echo "   CIF转USDZ转换工具 - 便携版"
echo "========================================"
echo

echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python环境正常"

echo
echo "📦 安装依赖包..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

echo
echo "🚀 启动CIF转USDZ转换服务..."
echo "📖 访问地址: http://localhost:8000"
echo "🛑 按Ctrl+C停止服务"
echo

python3 main.py

echo
echo "👋 服务已停止"
"""
    
    start_script = package_dir / "启动.sh"
    with open(start_script, "w", encoding="utf-8") as f:
        f.write(unix_start)
    
    # 设置执行权限
    if os.name != 'nt':
        os.chmod(start_script, 0o755)
    
    # 创建使用说明
    usage_guide = """# CIF转USDZ转换工具 - 便携版使用指南

## 🚀 快速开始

### Windows用户
1. 双击 `启动.bat`
2. 等待依赖安装完成
3. 浏览器访问: http://localhost:8000

### Linux/macOS用户  
1. 运行: `bash 启动.sh`
2. 等待依赖安装完成
3. 浏览器访问: http://localhost:8000

## ✨ 功能特性

- 🔄 **CIF转USDZ**: 完整转换链
- 🎨 **3D预览**: 基于Plotly的专业晶体结构渲染
- 📱 **AR支持**: iPhone扫码AR预览
- 🛠️ **多转换器**: Pymatgen + ASE + USD生成器

## 📋 系统要求

### 必需
- **Python**: 3.8+ 
- **操作系统**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **内存**: 4GB RAM
- **磁盘**: 500MB空间

### 可选（获得最佳效果）
- **Docker**: 可选，用于专业USD转换
- **USD工具**: Apple官方工具

## 🎯 使用流程

1. **启动服务**: 运行启动脚本
2. **打开浏览器**: http://localhost:8000
3. **上传CIF**: 拖拽或点击上传
4. **3D预览**: 自动渲染晶体结构
5. **转换USDZ**: 点击转换按钮
6. **AR预览**: iPhone扫描QR码

## 🔧 高级功能

### 命令行使用
```bash
# 单文件转换
python -m converter.main_converter input.cif output.usdz

# 系统测试
python test_system.py
```

### API调用
```python
import requests

with open('crystal.cif', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/convert',
        files={'file': f}
    )
```

## 🐛 常见问题

### 端口被占用
修改main.py中的端口号，或设置环境变量:
```bash
set PORT=8001  # Windows
export PORT=8001  # Linux/macOS
```

### 依赖安装失败
```bash
# 使用清华源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或使用conda
conda install -c conda-forge pymatgen ase
```

### Docker问题
- 确保Docker Desktop已启动
- 检查: `docker --version`
- Docker USD镜像会自动下载

## 📞 技术支持

如遇问题，请检查:
1. Python版本是否3.8+
2. 网络连接是否正常
3. 防火墙是否阻止8000端口

---

⭐ 专业的晶体结构转换解决方案
"""
    
    with open(package_dir / "使用说明.md", "w", encoding="utf-8") as f:
        f.write(usage_guide)
    
    # 创建项目信息文件
    project_info = {
        "name": "CIF转USDZ转换工具",
        "version": "1.0.0",
        "description": "专业的晶体结构文件转换解决方案",
        "features": [
            "CIF到USDZ完整转换链",
            "3D晶体结构预览",
            "iOS AR支持",
            "Docker USD专业转换器",
            "Web界面和API"
        ],
        "requirements": {
            "python": "3.8+",
            "memory": "4GB RAM",
            "disk": "500MB",
            "docker": "可选，用于专业USD转换"
        },
        "included_tools": [
            "Python USD工具 (CIF转USDZ)",
            "Python USD API",
            "Crystal Toolkit渲染引擎",
            "FastAPI Web框架"
        ]
    }
    
    import json
    with open(package_dir / "项目信息.json", "w", encoding="utf-8") as f:
        json.dump(project_info, f, ensure_ascii=False, indent=2)
    
    # 显示包内容
    print(f"\n📋 便携版本包内容:")
    for item in sorted(package_dir.rglob("*")):
        if item.is_file():
            size = item.stat().st_size
            if size > 1024*1024:
                size_str = f"{size/1024/1024:.1f}MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size}B"
            
            rel_path = item.relative_to(package_dir)
            print(f"  📄 {rel_path} ({size_str})")
    
    # 计算总大小
    total_size = sum(f.stat().st_size for f in package_dir.rglob("*") if f.is_file())
    print(f"\n📊 总大小: {total_size/1024/1024:.1f} MB")
    
    print(f"\n🎉 便携版本包创建完成!")
    print(f"📁 位置: {package_dir.absolute()}")
    print(f"\n📋 使用方法:")
    print(f"1. 将整个 '{package_name}' 文件夹复制给其他人")
    print(f"2. 运行启动脚本即可使用")
    print(f"3. 无需额外配置，开箱即用")
    
    return True

if __name__ == "__main__":
    create_portable_package() 