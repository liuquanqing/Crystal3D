@echo off
chcp 65001 >nul
echo ========================================
echo CIF转USDZ转换工具 - Docker部署脚本
echo ========================================
echo.

echo [1/5] 检查Docker环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装或未启动，请先安装Docker Desktop
    echo 📥 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo ✅ Docker环境检查通过

echo.
echo [2/5] 检查docker-compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose未安装
    echo 💡 请安装Docker Desktop或单独安装docker-compose
    pause
    exit /b 1
)
echo ✅ docker-compose检查通过

echo.
echo [3/5] 创建必要目录...
if not exist "user_files" mkdir user_files
if not exist "output" mkdir output
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
echo ✅ 目录创建完成

echo.
echo [4/5] 构建Docker镜像...
echo 🔧 使用轻量配置，快速构建...
echo ⏳ 这可能需要几分钟时间，请耐心等待...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Docker镜像构建失败
    echo 💡 尝试清理并重新构建: docker system prune -f
    pause
    exit /b 1
)
echo ✅ Docker镜像构建完成

echo.
echo [5/5] 启动服务...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ 服务启动失败
    echo 💡 查看日志: docker-compose -f docker-compose.optimized.yml logs
    pause
    exit /b 1
)

echo ✅ 服务启动成功！
echo.
echo ========================================
echo 🎉 部署完成！
echo ========================================
echo.
echo 📍 服务地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo 📁 用户文件目录: .\user_files
echo 📁 输出目录: .\output
echo 📁 转换结果: .\conversion_results
echo 📁 运行日志: .\logs
echo.
echo 💡 使用提示:
echo   - 将CIF文件放入user_files目录
echo   - 访问 http://localhost:8000 使用Web界面
echo   - 查看logs目录获取运行日志
echo.
echo 🔧 管理命令:
echo   - 停止服务: docker-compose down
echo   - 查看日志: docker-compose logs -f
echo   - 重启服务: docker-compose restart
echo   - 重新构建: docker-compose build --no-cache
echo.
echo ⚡ 特性:
echo   - 轻量级镜像（基于Python官方镜像）
echo   - 快速构建和启动
echo   - 完整功能支持
echo   - 与本地环境一致
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:8000 