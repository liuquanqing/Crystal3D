#!/usr/bin/env python3
"""
CIF转USDZ转换工具 - 一键部署脚本
支持本地运行、Docker部署、云服务器部署
"""
import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
        
    def check_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统要求...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
            print("需要Python 3.8+")
            return False
        
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Java检查已移除 - 项目不再依赖Jmol
        
        return True
    
    def install_dependencies(self):
        """安装Python依赖"""
        print("📦 安装Python依赖...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True)
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    def create_directories(self):
        """创建必要目录"""
        print("📁 创建项目目录...")
        
        directories = ["tools", "logs", "static", "examples", "output"]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ {dir_name}/")
    
    def check_docker(self):
        """检查Docker是否可用"""
        try:
            subprocess.run(["docker", "--version"], 
                          capture_output=True, check=True, timeout=5)
            subprocess.run(["docker-compose", "--version"], 
                          capture_output=True, check=True, timeout=5)
            return True
        except:
            return False
    
    def deploy_local(self):
        """本地部署"""
        print("\n🏠 本地部署模式")
        print("=" * 50)
        
        if not self.check_requirements():
            return False
        
        self.create_directories()
        
        if not self.install_dependencies():
            return False
        
        print("\n🚀 启动服务...")
        try:
            # 在新进程中启动服务
            if self.system == "windows":
                subprocess.Popen([sys.executable, "main.py"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, "main.py"])
            
            print("✅ 服务已启动")
            print("📖 访问地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/docs")
            return True
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def deploy_docker(self):
        """Docker部署"""
        print("\n🐳 Docker部署模式")
        print("=" * 50)
        
        if not self.check_docker():
            print("❌ Docker或Docker Compose未安装")
            print("请先安装Docker: https://docs.docker.com/get-docker/")
            return False
        
        print("🔨 构建Docker镜像...")
        try:
            subprocess.run(["docker-compose", "build"], check=True)
            print("✅ 镜像构建完成")
        except subprocess.CalledProcessError:
            print("❌ 镜像构建失败")
            return False
        
        print("🚀 启动Docker容器...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("✅ 容器已启动")
            print("📖 访问地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/docs")
            print("🔧 管理命令:")
            print("  查看日志: docker-compose logs -f")
            print("  停止服务: docker-compose down")
            print("  重启服务: docker-compose restart")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ 容器启动失败")
            return False
    
    def deploy_server(self):
        """服务器部署"""
        print("\n🌐 服务器部署模式")
        print("=" * 50)
        
        # 创建部署脚本
        deploy_script = """#!/bin/bash
# CIF转USDZ转换工具 - 服务器部署脚本

echo "🚀 开始部署CIF转USDZ转换工具..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
sudo apt install -y python3 python3-pip python3-venv nginx git openjdk-17-jdk

# 创建应用目录
sudo mkdir -p /opt/cif-converter
sudo chown $USER:$USER /opt/cif-converter
cd /opt/cif-converter

# 克隆项目（如果是Git仓库）
# git clone <your-repo-url> .

# 复制项目文件（如果是本地上传）
# 请手动上传项目文件到 /opt/cif-converter

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建systemd服务文件
sudo tee /etc/systemd/system/cif-converter.service > /dev/null <<EOF
[Unit]
Description=CIF to USDZ Converter
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/cif-converter
Environment=PATH=/opt/cif-converter/venv/bin
ExecStart=/opt/cif-converter/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 配置Nginx
sudo tee /etc/nginx/sites-available/cif-converter > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用Nginx配置
sudo ln -sf /etc/nginx/sites-available/cif-converter /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable cif-converter
sudo systemctl start cif-converter

echo "✅ 部署完成!"
echo "📖 访问地址: http://your-domain.com"
echo "🔧 管理命令:"
echo "  查看状态: sudo systemctl status cif-converter"
echo "  查看日志: sudo journalctl -u cif-converter -f"
echo "  重启服务: sudo systemctl restart cif-converter"
"""
        
        # 保存部署脚本
        script_path = self.project_root / "deploy_server.sh"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(deploy_script)
        
        # 设置执行权限
        if self.system != "windows":
            os.chmod(script_path, 0o755)
        
        print(f"✅ 服务器部署脚本已生成: {script_path}")
        print("\n📋 服务器部署步骤:")
        print("1. 将项目文件上传到服务器")
        print("2. 运行部署脚本: bash deploy_server.sh")
        print("3. 配置域名和SSL证书")
        
        return True
    
    def create_portable_package(self):
        """创建便携版本包"""
        print("\n📦 创建便携版本包")
        print("=" * 50)
        
        package_dir = self.project_root / "cif-converter-portable"
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        package_dir.mkdir()
        
        # 复制核心文件
        core_files = [
            "main.py", "requirements.txt", "setup.py", "README.md",
            "api/", "converter/", "static/", "utils/", "examples/"
        ]
        
        for item in core_files:
            src = self.project_root / item
            dst = package_dir / item
            
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        # 创建启动脚本
        if self.system == "windows":
            start_script = """@echo off
echo 🚀 启动CIF转USDZ转换工具...
python -m pip install -r requirements.txt
python main.py
pause
"""
            with open(package_dir / "start.bat", "w", encoding="utf-8") as f:
                f.write(start_script)
        else:
            start_script = """#!/bin/bash
echo "🚀 启动CIF转USDZ转换工具..."
python3 -m pip install -r requirements.txt
python3 main.py
"""
            script_path = package_dir / "start.sh"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(start_script)
            os.chmod(script_path, 0o755)
        
        # 创建使用说明
        readme_content = """# CIF转USDZ转换工具 - 便携版

## 快速开始

### Windows用户
双击 `start.bat` 即可启动

### Linux/macOS用户
运行: `bash start.sh`

## 访问地址
http://localhost:8000

## 功能特性
- CIF文件上传和解析
- 3D晶体结构预览
- USDZ格式转换
- iOS AR预览支持

## 技术要求
- Python 3.8+
- 4GB RAM
- 500MB磁盘空间

## 可选增强
- Docker Desktop (启用Docker USD专业转换)
- Apple USD工具 (最佳USDZ质量)

## 支持
如有问题，请查看完整文档。
"""
        
        with open(package_dir / "使用说明.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"✅ 便携版本包已创建: {package_dir}")
        print("📋 包含内容:")
        print("  - 所有源代码")
        print("  - 启动脚本")
        print("  - 使用说明")
        print("  - 示例文件")
        
        return True
    
    def show_menu(self):
        """显示部署菜单"""
        print("🎯 CIF转USDZ转换工具 - 部署向导")
        print("=" * 60)
        print("选择部署方式:")
        print()
        print("1. 🏠 本地运行   - 开发测试推荐")
        print("2. 🐳 Docker部署 - 生产环境推荐") 
        print("3. 🌐 服务器部署 - 云服务器部署")
        print("4. 📦 便携版本   - 无需安装，直接运行")
        print("5. ❌ 退出")
        print()
        
        while True:
            try:
                choice = input("请选择 (1-5): ").strip()
                
                if choice == "1":
                    return self.deploy_local()
                elif choice == "2":
                    return self.deploy_docker()
                elif choice == "3":
                    return self.deploy_server()
                elif choice == "4":
                    return self.create_portable_package()
                elif choice == "5":
                    print("👋 退出部署向导")
                    return True
                else:
                    print("❌ 无效选择，请输入1-5")
                    
            except KeyboardInterrupt:
                print("\n👋 用户取消")
                return True

def main():
    """主函数"""
    manager = DeploymentManager()
    manager.show_menu()

if __name__ == "__main__":
    main() 