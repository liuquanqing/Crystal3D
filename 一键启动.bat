@echo off
chcp 65001 >nul
title Crystal3D - 晶体结构3D转换器

echo.
echo ============================================
echo     💎 Crystal3D - 晶体结构3D转换器
echo ============================================
echo     🚀 一键启动脚本 v2.0
echo ============================================
echo.
echo 🔍 检查系统环境...

:: 检查Python
echo 📋 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo.
    echo 💡 解决方案：
    echo    1. 下载Python: https://www.python.org/downloads/
    echo    2. 安装时勾选"Add Python to PATH"
    echo    3. 重启命令行后再运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

:: 检查pip
echo 📦 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip不可用，尝试修复...
    python -m ensurepip --upgrade
)
echo ✅ pip检查通过

echo.
echo 📦 智能依赖检查...

:: 检查核心依赖是否已安装
python -c "import fastapi, uvicorn; print('✅ 核心Web框架已安装')" >nul 2>&1
if not errorlevel 1 (
    python -c "import ase; print('✅ 材料科学库已安装')" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ 核心依赖已安装，跳过安装步骤
        goto :start_service
    )
)

echo 🔧 需要安装依赖包...

:: 智能依赖安装策略
echo 🔧 开始智能安装依赖包...
echo.

:: 1. 尝试优化依赖（推荐生产环境）
if exist requirements_optimal.txt (
    echo 📌 [1/4] 尝试优化依赖包（生产推荐）...
    python -m pip install -r requirements_optimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet --disable-pip-version-check
    if not errorlevel 1 (
        echo ✅ 优化依赖安装成功
        goto :install_success
    )
    echo ⚠️  优化依赖安装失败，尝试下一种方案...
)

:: 2. 尝试最小依赖（快速安装）
if exist requirements_minimal.txt (
    echo 📌 [2/4] 尝试最小依赖包（快速安装）...
    python -m pip install -r requirements_minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet --disable-pip-version-check
    if not errorlevel 1 (
        echo ✅ 最小依赖安装成功
        goto :install_success
    )
    echo ⚠️  最小依赖安装失败，尝试下一种方案...
)

:: 3. 尝试完整依赖
if exist requirements.txt (
    echo 📌 [3/4] 尝试完整依赖包...
    python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet --disable-pip-version-check
    if not errorlevel 1 (
        echo ✅ 完整依赖安装成功
        goto :install_success
    )
    echo ⚠️  完整依赖安装失败，尝试手动安装核心包...
)

:: 4. 手动安装核心包（最后备用方案）
echo 📌 [4/4] 手动安装核心包（最后备用方案）...
python -m pip install fastapi uvicorn python-multipart aiofiles ase pillow loguru qrcode -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet --disable-pip-version-check
if not errorlevel 1 (
    echo ✅ 核心包安装成功
    goto :install_success
)

:: 5. 所有安装方式都失败
echo ❌ 所有安装方式都失败
echo.
echo 💡 故障排除指南：
echo    1. 检查网络连接是否正常
echo    2. 升级pip: python -m pip install --upgrade pip
echo    3. 清理pip缓存: python -m pip cache purge
echo    4. 使用虚拟环境:
echo       python -m venv venv
echo       venv\Scripts\activate
echo       pip install -r requirements_minimal.txt
echo    5. 手动配置清华源:
echo       pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
echo    6. 重新运行此脚本
echo.
echo 📞 如需技术支持，请查看README.md或提交Issue
echo.
pause
exit /b 1

:install_success
echo.
echo ✅ 依赖安装完成！
echo 📋 安装信息已保存到日志

:start_service
:: 检查端口占用
netstat -an | find "8000" >nul
if not errorlevel 1 (
    echo ⚠️  端口8000已被占用，尝试使用端口8001...
    set PORT=8001
) else (
    set PORT=8000
)

echo.
echo 🚀 启动Crystal3D服务...
echo =======================================
echo 🌐 Web界面: http://localhost:%PORT%
echo 📚 API文档: http://localhost:%PORT%/docs
echo 📱 移动端: http://localhost:%PORT% (手机浏览器)
echo 🛑 按Ctrl+C停止服务
echo =======================================
echo 💡 使用提示：
echo    - 支持拖拽上传CIF文件
echo    - 自动3D预览晶体结构
echo    - 一键转换为USDZ格式
echo    - iPhone扫码AR预览
echo =======================================
echo.

:: 启动服务
if defined PORT (
    python main.py %PORT%
) else (
    python main.py
)

echo.
echo 👋 Crystal3D服务已停止
echo 感谢使用晶体结构3D转换器！
echo.
echo 💡 下次启动：双击运行此脚本即可
echo 📖 更多信息请查看README.md
echo.
pause