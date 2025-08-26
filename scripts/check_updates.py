#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本检查和更新工具
检查TinyUSDZ和Pixar USD的版本信息，并提供更新建议
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path

class VersionChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tinyusdz_path = self.project_root / "tinyusdz"
        
    def check_pixar_usd_version(self):
        """检查当前Pixar USD版本"""
        try:
            from pxr import Usd
            import importlib.metadata
            
            # 获取当前版本
            current_version = Usd.GetVersion()
            package_version = importlib.metadata.version('usd-core')
            
            print(f"📦 Pixar USD (usd-core)")
            print(f"   当前版本: {package_version} (API: {current_version})")
            
            # 检查最新版本
            try:
                response = requests.get("https://pypi.org/pypi/usd-core/json", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['info']['version']
                    print(f"   最新版本: {latest_version}")
                    
                    if package_version != latest_version:
                        print(f"   ⚠️  有新版本可用！")
                        print(f"   更新命令: pip install --upgrade usd-core")
                    else:
                        print(f"   ✅ 已是最新版本")
                else:
                    print(f"   ❌ 无法获取最新版本信息")
            except Exception as e:
                print(f"   ❌ 检查更新失败: {e}")
                
            return {
                'name': 'Pixar USD',
                'current': package_version,
                'available': True
            }
            
        except ImportError:
            print(f"📦 Pixar USD (usd-core)")
            print(f"   ❌ 未安装")
            print(f"   安装命令: pip install usd-core")
            return {
                'name': 'Pixar USD',
                'current': None,
                'available': False
            }
        except Exception as e:
            print(f"📦 Pixar USD (usd-core)")
            print(f"   ❌ 检查失败: {e}")
            return {
                'name': 'Pixar USD',
                'current': None,
                'available': False
            }
    
    def check_tinyusdz_version(self):
        """检查TinyUSDZ版本"""
        print(f"\n📦 TinyUSDZ")
        
        if not self.tinyusdz_path.exists():
            print(f"   ❌ TinyUSDZ目录不存在: {self.tinyusdz_path}")
            return {
                'name': 'TinyUSDZ',
                'current': None,
                'available': False
            }
        
        # 检查本地版本信息
        readme_path = self.tinyusdz_path / "README.md"
        current_version = "Unknown"
        
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找版本信息
                    import re
                    version_match = re.search(r'### (\d+\.\d+) v([\d\.]+)', content)
                    if version_match:
                        current_version = f"{version_match.group(1)} v{version_match.group(2)}"
                    else:
                        # 查找其他版本模式
                        version_match = re.search(r'v(\d+\.\d+\.\d+)', content)
                        if version_match:
                            current_version = version_match.group(1)
            except Exception as e:
                print(f"   ⚠️  读取版本信息失败: {e}")
        
        print(f"   当前版本: {current_version}")
        
        # 检查GitHub最新版本
        try:
            response = requests.get(
                "https://api.github.com/repos/lighttransport/tinyusdz/releases/latest",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data['tag_name']
                release_date = data['published_at'][:10]
                print(f"   最新版本: {latest_version} ({release_date})")
                
                if current_version != latest_version and current_version != "Unknown":
                    print(f"   ⚠️  有新版本可用！")
                    print(f"   更新方式: 手动下载或git pull")
                    print(f"   下载地址: {data['html_url']}")
                else:
                    print(f"   ✅ 版本信息已检查")
            else:
                print(f"   ❌ 无法获取最新版本信息 (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ 检查更新失败: {e}")
        
        # 检查TinyUSDZ是否可用
        try:
            sys.path.insert(0, str(self.tinyusdz_path))
            import tinyusdz
            available = True
            print(f"   ✅ 模块可用")
        except ImportError as e:
            available = False
            print(f"   ❌ 模块不可用: {e}")
        finally:
            if str(self.tinyusdz_path) in sys.path:
                sys.path.remove(str(self.tinyusdz_path))
        
        return {
            'name': 'TinyUSDZ',
            'current': current_version,
            'available': available
        }
    
    def check_all_versions(self):
        """检查所有组件版本"""
        print("🔍 检查USD相关组件版本...\n")
        
        results = []
        
        # 检查Pixar USD
        pixar_result = self.check_pixar_usd_version()
        results.append(pixar_result)
        
        # 检查TinyUSDZ
        tinyusdz_result = self.check_tinyusdz_version()
        results.append(tinyusdz_result)
        
        # 总结
        print("\n" + "="*50)
        print("📋 版本检查总结:")
        for result in results:
            status = "✅ 可用" if result['available'] else "❌ 不可用"
            version = result['current'] or "未安装"
            print(f"   {result['name']}: {version} - {status}")
        
        return results
    
    def update_pixar_usd(self):
        """更新Pixar USD"""
        print("🔄 更新Pixar USD...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "usd-core"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Pixar USD更新成功")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Pixar USD更新失败: {e}")
            print(e.stderr)
            return False
    
    def show_update_instructions(self):
        """显示更新说明"""
        print("\n" + "="*50)
        print("📖 更新说明:")
        print("\n1. Pixar USD (usd-core):")
        print("   - 自动更新: python scripts/check_updates.py --update-pixar")
        print("   - 手动更新: pip install --upgrade usd-core")
        print("\n2. TinyUSDZ:")
        print("   - 需要手动更新 (Git子模块或重新下载)")
        print("   - 检查最新版本: https://github.com/lighttransport/tinyusdz/releases")
        print("   - 如果是Git子模块: git submodule update --remote tinyusdz")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='USD组件版本检查和更新工具')
    parser.add_argument('--update-pixar', action='store_true', help='自动更新Pixar USD')
    parser.add_argument('--check-only', action='store_true', help='仅检查版本，不显示更新说明')
    
    args = parser.parse_args()
    
    checker = VersionChecker()
    
    # 检查版本
    results = checker.check_all_versions()
    
    # 更新Pixar USD
    if args.update_pixar:
        checker.update_pixar_usd()
        print("\n🔍 重新检查版本...")
        checker.check_pixar_usd_version()
    
    # 显示更新说明
    if not args.check_only:
        checker.show_update_instructions()

if __name__ == "__main__":
    main()