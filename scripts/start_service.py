#!/usr/bin/env python3
"""
CIF转USDZ转换服务启动脚本
支持开发模式和生产模式启动
"""
import os
import sys
import argparse
import uvicorn
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils import setup_logger
from config import config


def start_development_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """启动开发服务器"""
    logger = setup_logger('DEBUG')
    logger.info("启动开发模式服务器...")
    
    print(f"🚀 启动CIF转USDZ转换服务 (开发模式)")
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 配置信息:")
    print(f"  - 临时目录: {config.TEMP_DIR}")
    print(f"  - 日志目录: {config.LOG_DIR}")
    print(f"  - 日志级别: {config.LOG_LEVEL}")
    print(f"  - 文件大小限制: {config.MAX_FILE_SIZE_MB}MB")
    print(f"  - 批量文件限制: {config.MAX_BATCH_FILES}个")
    print("─" * 60)
    
    try:
        uvicorn.run(
            "api.routes:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        sys.exit(1)


def start_production_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    """启动生产服务器"""
    logger = setup_logger(config.LOG_LEVEL)
    logger.info("启动生产模式服务器...")
    
    print(f"🚀 启动CIF转USDZ转换服务 (生产模式)")
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"👥 工作进程: {workers}")
    print("─" * 60)
    
    try:
        uvicorn.run(
            "api.routes:app",
            host=host,
            port=port,
            workers=workers,
            log_level=config.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        sys.exit(1)


def check_dependencies():
    """检查依赖和配置"""
    print("🔍 检查依赖和配置...")
    
    # 检查重要的Python包
    required_packages = [
        'fastapi', 'uvicorn', 'pymatgen', 'ase', 
        'numpy', 'aiofiles', 'loguru'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (未安装)")
    
    if missing_packages:
        print(f"\n⚠️  缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查配置
    print(f"\n🔧 配置检查:")
    print(f"✓ 临时目录: {config.TEMP_DIR}")
    print(f"✓ 日志目录: {config.LOG_DIR}")
    print(f"✓ 示例目录: {config.EXAMPLES_DIR}")
    
    # 检查USD转换工具
    from converter.usdz_converter import USDZConverter
    usdz_converter = USDZConverter()
    if usdz_converter.is_available():
        print(f"✓ USD转换工具: {usdz_converter.usd_converter_path}")
    else:
        print("⚠️  USD转换工具未找到，将使用备用方案")
    
    print("✅ 依赖检查完成")
    return True


def run_quick_test():
    """运行快速测试"""
    print("\n🧪 运行快速功能测试...")
    
    try:
        from converter.main_converter import CIFToUSDZConverter
        
        # 测试转换器创建
        converter = CIFToUSDZConverter()
        info = converter.get_conversion_info()
        
        print("✓ 转换器创建成功")
        print(f"✓ 版本: {info['converter_version']}")
        print(f"✓ USD工具可用: {info['usd_converter_available']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="CIF转USDZ转换服务启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 开发模式（自动重载）
  python start_service.py --dev
  
  # 生产模式
  python start_service.py --prod --workers 4
  
  # 自定义端口
  python start_service.py --dev --port 9000
  
  # 仅检查依赖
  python start_service.py --check-only
        """
    )
    
    parser.add_argument('--dev', action='store_true', help='开发模式（自动重载）')
    parser.add_argument('--prod', action='store_true', help='生产模式')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--workers', type=int, default=1, help='生产模式工作进程数')
    parser.add_argument('--check-only', action='store_true', help='仅检查依赖，不启动服务')
    parser.add_argument('--no-check', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    # 默认开发模式
    if not args.dev and not args.prod:
        args.dev = True
    
    # 检查依赖
    if not args.no_check:
        if not check_dependencies():
            sys.exit(1)
        
        if not run_quick_test():
            sys.exit(1)
    
    # 仅检查模式
    if args.check_only:
        print("✅ 所有检查通过，可以启动服务")
        return
    
    # 调整生产模式主机地址
    if args.prod and args.host == '127.0.0.1':
        args.host = '0.0.0.0'
    
    # 启动服务
    if args.dev:
        start_development_server(args.host, args.port, reload=True)
    elif args.prod:
        start_production_server(args.host, args.port, args.workers)


if __name__ == "__main__":
    main() 