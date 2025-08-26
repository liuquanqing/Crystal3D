#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本检查功能
验证CIF转换器和USD转换器的版本检查
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.version_checker import get_version_checker
from loguru import logger

def test_version_checker():
    """测试版本检查器"""
    print("=== 测试版本检查功能 ===")
    print()
    
    try:
        # 获取版本检查器
        checker = get_version_checker()
        
        # 检查所有组件
        results = checker.check_all_components()
        
        print("📦 组件版本信息:")
        print("-" * 50)
        
        for component_name, version_info in results.items():
            status_icon = "✅" if version_info.available else "❌"
            update_icon = "🔄" if version_info.update_available else "✅"
            
            print(f"{status_icon} {version_info.name}:")
            
            if version_info.available:
                print(f"   当前版本: {version_info.current_version}")
                if version_info.latest_version:
                    print(f"   最新版本: {version_info.latest_version}")
                    if version_info.update_available:
                        print(f"   {update_icon} 有新版本可用！")
                    else:
                        print(f"   {update_icon} 已是最新版本")
                else:
                    print("   最新版本: 检查失败")
            else:
                print("   状态: 不可用")
                
                # 提供安装建议
                if component_name == 'pymatgen':
                    print("   安装命令: pip install pymatgen")
                elif component_name == 'ase':
                    print("   安装命令: pip install ase")
                elif component_name == 'pixar_usd':
                    print("   安装命令: pip install usd-core")
                elif component_name == 'tinyusdz':
                    print("   说明: 本地编译版本，请检查编译状态")
            
            print()
        
        # 获取摘要信息
        summary = checker.get_version_summary()
        
        print("📊 版本检查摘要:")
        print("-" * 50)
        print(f"可用组件: {summary['total_available']}/{len(results)}")
        print(f"可更新组件: {summary['updates_available']}")
        print(f"检查时间: {summary['last_checked']}")
        print()
        
        # 分类显示
        print("🔧 CIF转换器库:")
        cif_libs = ['pymatgen', 'ase']
        for lib in cif_libs:
            if lib in results:
                info = results[lib]
                status = "可用" if info.available else "不可用"
                version = f"v{info.current_version}" if info.current_version else "未知"
                print(f"   • {info.name}: {status} {version}")
        
        print()
        print("🎬 USD转换器库:")
        usd_libs = ['pixar_usd', 'tinyusdz']
        for lib in usd_libs:
            if lib in results:
                info = results[lib]
                status = "可用" if info.available else "不可用"
                version = f"v{info.current_version}" if info.current_version else "未知"
                print(f"   • {info.name}: {status} {version}")
        
        print()
        
        # 更新建议
        updates_needed = [info for info in results.values() if info.update_available]
        if updates_needed:
            print("🔄 更新建议:")
            print("-" * 50)
            for info in updates_needed:
                if info.name == "Pymatgen":
                    print(f"   pip install --upgrade pymatgen  # {info.current_version} → {info.latest_version}")
                elif info.name == "ASE":
                    print(f"   pip install --upgrade ase  # {info.current_version} → {info.latest_version}")
                elif info.name == "Pixar USD":
                    print(f"   pip install --upgrade usd-core  # {info.current_version} → {info.latest_version}")
                elif info.name == "TinyUSDZ":
                    print(f"   手动更新TinyUSDZ  # {info.current_version} → {info.latest_version}")
                    print(f"   下载地址: https://github.com/lighttransport/tinyusdz/releases")
        else:
            print("✅ 所有可用组件都是最新版本！")
        
        return True
        
    except Exception as e:
        logger.error(f"版本检查测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_converter_status():
    """测试主转换器的状态检查"""
    print("\n=== 测试主转换器状态检查 ===")
    print()
    
    try:
        from converter.main_converter import CIFToUSDZConverter
        
        # 创建转换器实例
        converter = CIFToUSDZConverter()
        
        # 获取状态
        status = converter.get_all_converter_status()
        
        print("📊 转换器状态摘要:")
        print("-" * 50)
        summary = status['summary']
        print(f"总转换器数: {summary['total_converters']}")
        print(f"可用转换器: {summary['available_converters']}")
        print(f"不可用转换器: {summary['unavailable_converters']}")
        print(f"可更新组件: {summary['updates_available']}")
        print()
        
        # 显示版本信息
        if 'version_info' in status:
            print("📦 集成的版本信息:")
            print("-" * 50)
            for component, info in status['version_info'].items():
                status_icon = "✅" if info['available'] else "❌"
                update_icon = "🔄" if info.get('update_available', False) else "✅"
                
                print(f"{status_icon} {info['name']}: ", end="")
                if info['available']:
                    print(f"v{info['current_version']} {update_icon}")
                else:
                    print("不可用")
        
        return True
        
    except Exception as e:
        logger.error(f"主转换器状态检查测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🔍 CIF和USD转换器版本检查测试")
    print("=" * 60)
    
    # 测试版本检查器
    success1 = test_version_checker()
    
    # 测试主转换器状态
    success2 = test_main_converter_status()
    
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    print(f"版本检查器: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"主转换器状态: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！版本检查功能已成功集成。")
        print("\n💡 使用建议:")
        print("   • 定期运行版本检查以获取最新更新")
        print("   • 优先更新Pymatgen和ASE以获得最佳CIF转换质量")
        print("   • 保持Pixar USD最新版本以获得最佳USDZ兼容性")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()