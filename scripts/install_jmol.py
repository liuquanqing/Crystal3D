#!/usr/bin/env python3
"""
Jmol自动安装脚本
为Windows/Linux/macOS自动下载和配置Jmol
"""
import os
import sys
import platform
import subprocess
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path
import tempfile

def detect_system():
    """检测操作系统"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"🔍 检测到系统: {system} ({arch})")
    return system, arch

def check_java():
    """检查Java是否已安装"""
    print("☕ 检查Java环境...")
    
    try:
        result = subprocess.run(
            ["java", "-version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            # 解析Java版本
            version_output = result.stderr if result.stderr else result.stdout
            print(f"✅ Java已安装: {version_output.split('\\n')[0]}")
            return True
        else:
            print("❌ Java未正确安装")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Java未找到")
        return False

def install_java():
    """安装Java（如果需要）"""
    system, arch = detect_system()
    
    print("📥 开始安装Java...")
    
    if system == "windows":
        print("🔗 Windows Java安装:")
        print("请访问: https://adoptium.net/temurin/releases/")
        print("下载并安装 Temurin JDK 17+ (x64)")
        input("安装完成后按回车继续...")
        
    elif system == "darwin":  # macOS
        print("🍺 macOS Java安装:")
        try:
            subprocess.run(["brew", "install", "openjdk"], check=True)
            print("✅ Java通过Homebrew安装完成")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("请手动安装:")
            print("brew install openjdk")
            print("或访问: https://adoptium.net/")
    
    elif system == "linux":
        print("🐧 Linux Java安装:")
        try:
            # 尝试apt (Ubuntu/Debian)
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "openjdk-17-jdk"], check=True)
            print("✅ Java通过apt安装完成")
        except subprocess.CalledProcessError:
            try:
                # 尝试yum (CentOS/RHEL)
                subprocess.run(["sudo", "yum", "install", "-y", "java-17-openjdk"], check=True)
                print("✅ Java通过yum安装完成")
            except subprocess.CalledProcessError:
                print("请手动安装Java:")
                print("sudo apt install openjdk-17-jdk  # Ubuntu/Debian")
                print("sudo yum install java-17-openjdk  # CentOS/RHEL")

def download_jmol():
    """下载Jmol"""
    print("📦 下载Jmol...")
    
    # Jmol下载URLs
    jmol_urls = [
        "https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.32/Jmol-14.32.10-binary.tar.gz/download",
        "https://github.com/BobHanson/Jmol-SwingJS/releases/download/v14.32.10/Jmol-14.32.10-binary.tar.gz",
        # 备用直链
        "https://sourceforge.net/projects/jmol/files/latest/download"
    ]
    
    tools_dir = Path("tools")
    tools_dir.mkdir(exist_ok=True)
    
    for i, url in enumerate(jmol_urls):
        try:
            print(f"🔄 尝试下载源 {i+1}...")
            
            # 下载到临时文件
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
                print(f"📥 正在下载: {url}")
                
                with urllib.request.urlopen(url) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\\r进度: {percent:.1f}%", end="", flush=True)
                
                print("\\n✅ 下载完成")
                return tmp_file.name
                
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            continue
    
    raise Exception("所有下载源都失败了")

def extract_jmol(tar_path):
    """解压Jmol"""
    print("📂 解压Jmol...")
    
    tools_dir = Path("tools")
    extract_dir = tools_dir / "jmol_temp"
    
    try:
        # 解压tar.gz文件
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(extract_dir)
        
        # 查找Jmol.jar文件
        jar_file = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file == "Jmol.jar":
                    jar_file = os.path.join(root, file)
                    break
            if jar_file:
                break
        
        if not jar_file:
            raise Exception("在解压文件中未找到Jmol.jar")
        
        # 复制到tools目录
        target_jar = tools_dir / "Jmol.jar"
        shutil.copy2(jar_file, target_jar)
        
        print(f"✅ Jmol.jar已安装到: {target_jar}")
        
        # 清理临时文件
        shutil.rmtree(extract_dir, ignore_errors=True)
        os.unlink(tar_path)
        
        return str(target_jar)
        
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        # 清理
        shutil.rmtree(extract_dir, ignore_errors=True)
        if os.path.exists(tar_path):
            os.unlink(tar_path)
        raise

def test_jmol(jar_path):
    """测试Jmol安装"""
    print("🧪 测试Jmol...")
    
    try:
        cmd = ["java", "-jar", jar_path, "-n", "-s", "print 'Jmol is working!'; quit;"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Jmol测试成功！")
            return True
        else:
            print(f"❌ Jmol测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Jmol测试异常: {e}")
        return False

def setup_environment(jar_path):
    """设置环境变量"""
    print("⚙️ 配置环境...")
    
    abs_jar_path = os.path.abspath(jar_path)
    
    # 创建环境配置文件
    env_file = Path(".env")
    
    env_content = f"""# Jmol配置
JMOL_JAR_PATH={abs_jar_path}

# 其他配置
SPHERE_RESOLUTION=20
INCLUDE_BONDS=true
SCALE_FACTOR=1.0
"""
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ 环境配置已保存到: {env_file}")
    
    # 输出手动设置指令
    system, _ = detect_system()
    
    print("\\n🔧 手动环境变量设置（可选）:")
    if system == "windows":
        print(f"set JMOL_JAR_PATH={abs_jar_path}")
    else:
        print(f"export JMOL_JAR_PATH={abs_jar_path}")

def main():
    """主安装流程"""
    print("🚀 Jmol自动安装程序")
    print("=" * 50)
    
    try:
        # 1. 检测系统
        system, arch = detect_system()
        
        # 2. 检查Java
        if not check_java():
            print("\\n⚠️ 需要先安装Java")
            install_java()
            
            # 重新检查
            if not check_java():
                print("❌ Java安装失败，请手动安装后重试")
                return False
        
        # 3. 检查是否已安装Jmol
        existing_jar = Path("tools/Jmol.jar")
        if existing_jar.exists():
            print(f"✅ 发现已存在的Jmol: {existing_jar}")
            if test_jmol(str(existing_jar)):
                print("🎉 Jmol已正确安装并可用！")
                setup_environment(str(existing_jar))
                return True
            else:
                print("⚠️ 现有Jmol不可用，重新安装...")
        
        # 4. 下载Jmol
        tar_path = download_jmol()
        
        # 5. 解压安装
        jar_path = extract_jmol(tar_path)
        
        # 6. 测试安装
        if test_jmol(jar_path):
            print("🎉 Jmol安装成功！")
            setup_environment(jar_path)
            
            # 7. 运行项目测试
            print("\\n🧪 运行项目集成测试...")
            try:
                subprocess.run([sys.executable, "test_jmol_integration.py"], check=True)
            except subprocess.CalledProcessError:
                print("⚠️ 集成测试失败，但Jmol已安装")
            
            return True
        else:
            print("❌ Jmol安装失败")
            return False
    
    except KeyboardInterrupt:
        print("\\n❌ 用户取消安装")
        return False
    except Exception as e:
        print(f"❌ 安装异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\n" + "=" * 50)
        print("🎉 安装完成！现在您可以:")
        print("1. 运行服务: python main.py")
        print("2. 测试转换: python test_jmol_integration.py")
        print("3. 享受专业级CIF转OBJ质量，告别'海马'！")
        print("=" * 50)
    else:
        print("\\n❌ 安装失败，请查看错误信息")
        sys.exit(1) 