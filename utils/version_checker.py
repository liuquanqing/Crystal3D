#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本检查工具
用于检查USD相关组件的版本信息
"""

import sys
import requests
from pathlib import Path
from loguru import logger

class VersionInfo:
    def __init__(self, name, current_version=None, latest_version=None, available=False, update_available=False):
        self.name = name
        self.current_version = current_version
        self.latest_version = latest_version
        self.available = available
        self.update_available = update_available
    
    def to_dict(self):
        return {
            'name': self.name,
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'available': self.available,
            'update_available': self.update_available
        }

class ComponentVersionChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tinyusdz_path = self.project_root / "tinyusdz"
    
    def check_pixar_usd(self):
        """检查Pixar USD版本"""
        try:
            from pxr import Usd
            import importlib.metadata
            
            # 获取当前版本
            api_version = Usd.GetVersion()
            package_version = importlib.metadata.version('usd-core')
            
            # 检查最新版本
            latest_version = None
            update_available = False
            
            try:
                response = requests.get("https://pypi.org/pypi/usd-core/json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['info']['version']
                    update_available = package_version != latest_version
            except Exception as e:
                logger.warning(f"无法检查Pixar USD最新版本: {e}")
            
            return VersionInfo(
                name="Pixar USD",
                current_version=package_version,
                latest_version=latest_version,
                available=True,
                update_available=update_available
            )
            
        except ImportError:
            return VersionInfo(
                name="Pixar USD",
                available=False
            )
        except Exception as e:
            logger.error(f"检查Pixar USD版本失败: {e}")
            return VersionInfo(
                name="Pixar USD",
                available=False
            )
    
    def check_tinyusdz(self):
        """检查TinyUSDZ版本"""
        if not self.tinyusdz_path.exists():
            return VersionInfo(
                name="TinyUSDZ",
                available=False
            )
        
        # 检查本地版本
        current_version = self._get_tinyusdz_local_version()
        
        # 检查最新版本
        latest_version = None
        update_available = False
        
        try:
            response = requests.get(
                "https://api.github.com/repos/lighttransport/tinyusdz/releases/latest",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data['tag_name']
                if current_version and current_version != "Unknown":
                    update_available = current_version != latest_version
        except Exception as e:
            logger.warning(f"无法检查TinyUSDZ最新版本: {e}")
        
        # 检查模块可用性
        available = self._check_tinyusdz_available()
        
        return VersionInfo(
            name="TinyUSDZ",
            current_version=current_version,
            latest_version=latest_version,
            available=available,
            update_available=update_available
        )
    
    def _get_tinyusdz_local_version(self):
        """获取TinyUSDZ本地版本"""
        readme_path = self.tinyusdz_path / "README.md"
        
        if not readme_path.exists():
            return "Unknown"
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import re
            # 查找版本信息
            version_match = re.search(r'### (\d+\.\d+) v([\d\.]+)', content)
            if version_match:
                return f"{version_match.group(1)} v{version_match.group(2)}"
            
            # 查找其他版本模式
            version_match = re.search(r'v(\d+\.\d+\.\d+)', content)
            if version_match:
                return version_match.group(1)
                
            return "Unknown"
            
        except Exception as e:
            logger.warning(f"读取TinyUSDZ版本信息失败: {e}")
            return "Unknown"
    
    def _check_tinyusdz_available(self):
        """检查TinyUSDZ模块是否可用"""
        try:
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.tinyusdz_path))
            
            import tinyusdz
            return True
            
        except ImportError:
            return False
        except Exception as e:
            logger.warning(f"检查TinyUSDZ可用性失败: {e}")
            return False
        finally:
            sys.path = original_path
    
    def check_pymatgen(self):
        """检查Pymatgen版本"""
        try:
            import pymatgen
            import importlib.metadata
            
            # 获取当前版本
            current_version = importlib.metadata.version('pymatgen')
            
            # 检查最新版本
            latest_version = None
            update_available = False
            
            try:
                response = requests.get("https://pypi.org/pypi/pymatgen/json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['info']['version']
                    update_available = current_version != latest_version
            except Exception as e:
                logger.warning(f"无法检查Pymatgen最新版本: {e}")
            
            return VersionInfo(
                name="Pymatgen",
                current_version=current_version,
                latest_version=latest_version,
                available=True,
                update_available=update_available
            )
            
        except ImportError:
            return VersionInfo(
                name="Pymatgen",
                available=False
            )
        except Exception as e:
            logger.error(f"检查Pymatgen版本失败: {e}")
            return VersionInfo(
                name="Pymatgen",
                available=False
            )
    
    def check_ase(self):
        """检查ASE版本"""
        try:
            import ase
            import importlib.metadata
            
            # 获取当前版本
            current_version = importlib.metadata.version('ase')
            
            # 检查最新版本
            latest_version = None
            update_available = False
            
            try:
                response = requests.get("https://pypi.org/pypi/ase/json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['info']['version']
                    update_available = current_version != latest_version
            except Exception as e:
                logger.warning(f"无法检查ASE最新版本: {e}")
            
            return VersionInfo(
                name="ASE",
                current_version=current_version,
                latest_version=latest_version,
                available=True,
                update_available=update_available
            )
            
        except ImportError:
            return VersionInfo(
                name="ASE",
                available=False
            )
        except Exception as e:
            logger.error(f"检查ASE版本失败: {e}")
            return VersionInfo(
                name="ASE",
                available=False
            )
    
    def check_fastapi(self):
        """检查FastAPI版本"""
        try:
            import fastapi
            import importlib.metadata
            
            # 获取当前版本
            current_version = importlib.metadata.version('fastapi')
            
            # 检查最新版本
            latest_version = None
            update_available = False
            
            try:
                response = requests.get("https://pypi.org/pypi/fastapi/json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['info']['version']
                    update_available = current_version != latest_version
            except Exception as e:
                logger.warning(f"无法检查FastAPI最新版本: {e}")
            
            return VersionInfo(
                name="FastAPI",
                current_version=current_version,
                latest_version=latest_version,
                available=True,
                update_available=update_available
            )
            
        except ImportError:
            return VersionInfo(
                name="FastAPI",
                available=False
            )
        except Exception as e:
            logger.error(f"检查FastAPI版本失败: {e}")
            return VersionInfo(
                name="FastAPI",
                available=False
            )
    
    def check_all_components(self):
        """检查所有组件版本"""
        logger.info("检查所有组件版本...")
        
        # 按重要性排序：ASE和Pymatgen是CIF转换的核心库，FastAPI是Web框架，USD相关是3D处理
        from collections import OrderedDict
        results = OrderedDict([
            ('ase', self.check_ase()),
            ('pymatgen', self.check_pymatgen()),
            ('fastapi', self.check_fastapi()),
            ('pixar_usd', self.check_pixar_usd()),
            ('tinyusdz', self.check_tinyusdz())
        ])
        
        # 记录结果
        for component_name, version_info in results.items():
            if version_info.available:
                status = "可用"
                if version_info.update_available:
                    status += " (有更新)"
                logger.info(f"{version_info.name}: {version_info.current_version} - {status}")
            else:
                logger.warning(f"{version_info.name}: 不可用")
        
        return results
    
    def get_version_summary(self):
        """获取版本摘要信息"""
        results = self.check_all_components()
        
        summary = {
            'components': {},
            'total_available': 0,
            'updates_available': 0,
            'last_checked': None
        }
        
        for component_name, version_info in results.items():
            summary['components'][component_name] = version_info.to_dict()
            
            if version_info.available:
                summary['total_available'] += 1
            
            if version_info.update_available:
                summary['updates_available'] += 1
        
        from datetime import datetime
        summary['last_checked'] = datetime.now().isoformat()
        
        return summary

# 全局实例
_version_checker = None

def get_version_checker():
    """获取版本检查器实例"""
    global _version_checker
    if _version_checker is None:
        _version_checker = ComponentVersionChecker()
    return _version_checker

def check_component_versions():
    """检查组件版本的便捷函数"""
    checker = get_version_checker()
    return checker.check_all_components()

def get_version_summary():
    """获取版本摘要的便捷函数"""
    checker = get_version_checker()
    return checker.get_version_summary()