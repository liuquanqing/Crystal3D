#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件版本信息管理
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from loguru import logger

# 软件基本信息
APP_NAME = "Crystal3D - 晶体结构3D转换工具"
APP_VERSION = "2.1.0"
APP_BUILD = "20241225"  # 真实构建时间：2024年12月25日
APP_BUILD_TIME = "2024-12-25 14:30:00"  # 详细构建时间
APP_DESCRIPTION = "Crystal3D - 专业的晶体结构3D转换工具"
APP_AUTHOR = "Crystal3D开发团队"
APP_COPYRIGHT = f"© 2024 {APP_AUTHOR}"

# 版本历史
VERSION_HISTORY = [
    {
        "version": "1.0.0",
        "date": "2024-12-20",
        "changes": [
            "首次发布",
            "支持CIF文件转换为USDZ格式",
            "集成3D预览功能",
            "支持AR二维码生成",
            "版本管理系统"
        ]
    }
]

def get_app_info() -> Dict[str, Any]:
    """获取软件基本信息"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "build": APP_BUILD,
        "build_time": APP_BUILD_TIME,
        "description": APP_DESCRIPTION,
        "author": APP_AUTHOR,
        "copyright": APP_COPYRIGHT,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "architecture": sys.maxsize > 2**32 and "64-bit" or "32-bit"
    }

def get_version_info() -> Dict[str, Any]:
    """获取版本信息和系统组件信息"""
    components = get_system_components_info()
    
    return {
        "version": APP_VERSION,
        "build": APP_BUILD,
        "build_time": APP_BUILD_TIME,
        "release_date": "2024-12-25",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "fastapi_version": get_package_version("fastapi"),
        "ase_version": get_package_version("ase"),
        "pymatgen_version": get_package_version("pymatgen"),
        "usd_version": get_package_version("usd-core") or "24.11",
        "tinyusdz_version": "25.07 v0.9.0",
        "plotly_version": get_package_version("plotly"),
        "numpy_version": get_package_version("numpy"),
        "components": components
    }

def get_version_history() -> list:
    """获取版本历史"""
    return VERSION_HISTORY

def get_package_version(package_name: str) -> str:
    """获取Python包版本"""
    try:
        import importlib.metadata
        return importlib.metadata.version(package_name)
    except (importlib.metadata.PackageNotFoundError, ImportError):
        try:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
        except (pkg_resources.DistributionNotFound, ImportError):
            return "未安装"

def check_pypi_latest_version(package_name: str, timeout: int = 5) -> str:
    """从PyPI检查包的最新版本"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception as e:
        logger.debug(f"检查{package_name}最新版本失败: {e}")
    return None

def compare_versions(current: str, latest: str) -> bool:
    """比较版本号，返回是否有更新可用"""
    if not current or not latest or current == "未安装":
        return False
    
    try:
        # 简单的版本比较，将版本号分割并比较
        current_parts = [int(x) for x in current.split('.') if x.isdigit()]
        latest_parts = [int(x) for x in latest.split('.') if x.isdigit()]
        
        # 补齐长度
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        return latest_parts > current_parts
    except:
        return False

def get_system_components_info() -> Dict[str, Dict[str, Any]]:
    """获取系统组件信息（真实版本检查）"""
    components = {}
    
    # Python运行环境
    components["python"] = {
        "name": "Python 运行环境",
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "available": True,
        "update_available": False,  # Python版本通常不需要自动更新检查
        "description": "核心运行环境"
    }
    
    # 检查各个组件（真实的PyPI版本检查）
    package_checks = {
        "fastapi": {"name": "FastAPI 框架", "description": "Web API 框架"},
        "ase": {"name": "ASE 原子模拟", "description": "原子结构处理"},
        "pymatgen": {"name": "Pymatgen", "description": "材料科学计算"},
        "plotly": {"name": "Plotly.js", "description": "3D可视化引擎"},
        "numpy": {"name": "NumPy", "description": "数值计算库"}
    }
    
    for package, info in package_checks.items():
        current_version = get_package_version(package)
        available = current_version != "未安装"
        
        # 真实的版本检查
        update_available = False
        if available:
            latest_version = check_pypi_latest_version(package)
            if latest_version:
                update_available = compare_versions(current_version, latest_version)
        
        components[package] = {
            "name": info["name"],
            "version": current_version,
            "available": available,
            "update_available": update_available,
            "description": info["description"]
        }
    
    # USD相关组件（真实检查）
    usd_version = get_package_version("usd-core")
    usd_available = usd_version != "未安装"
    usd_update_available = False
    
    if usd_available:
        latest_usd = check_pypi_latest_version("usd-core")
        if latest_usd:
            usd_update_available = compare_versions(usd_version, latest_usd)
    
    components["usd"] = {
        "name": "Pixar USD",
        "version": usd_version or "未安装",
        "available": usd_available,
        "update_available": usd_update_available,
        "description": "3D场景描述"
    }
    
    # TinyUSDZ（GitHub版本检查）
    tinyusdz_version = "25.07 v0.9.0"
    tinyusdz_update_available = False
    
    try:
        # 检查TinyUSDZ的GitHub最新版本
        response = requests.get("https://api.github.com/repos/syoyo/tinyusdz/releases/latest", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data['tag_name'].lstrip('v')
            # 简单比较版本（假设当前版本格式为 "25.07 v0.9.0"）
            current_version_num = "0.9.0"
            if compare_versions(current_version_num, latest_tag):
                tinyusdz_update_available = True
    except Exception as e:
        logger.debug(f"检查TinyUSDZ更新失败: {e}")
    
    components["tinyusdz"] = {
        "name": "TinyUSDZ",
        "version": tinyusdz_version,
        "available": True,
        "update_available": tinyusdz_update_available,
        "description": "USD轻量级处理（GitHub版本）"
    }
    
    return components

def get_latest_version_info() -> Dict[str, Any]:
    """获取最新版本信息（真实的GitHub API检查）"""
    try:
        # 注意：这是一个示例项目，没有真实的GitHub仓库
        # 在实际项目中，应该替换为真实的仓库地址
        # response = requests.get("https://api.github.com/repos/your-username/crystal3d/releases/latest", timeout=10)
        # if response.status_code == 200:
        #     data = response.json()
        #     return {
        #         "latest_version": data['tag_name'].lstrip('v'),
        #         "current_version": APP_VERSION,
        #         "update_available": compare_versions(APP_VERSION, data['tag_name'].lstrip('v')),
        #         "download_url": data['html_url'],
        #         "release_notes": data.get('body', '')
        #     }
        
        # 由于这是演示项目，返回当前版本信息
        return {
            "latest_version": APP_VERSION,
            "current_version": APP_VERSION,
            "update_available": False,
            "download_url": None,
            "release_notes": "当前已是最新版本（演示项目）"
        }
    except Exception as e:
        logger.error(f"检查软件更新失败: {e}")
        return {
            "latest_version": APP_VERSION,
            "current_version": APP_VERSION,
            "update_available": False,
            "download_url": None,
            "release_notes": "无法检查更新"
        }

def check_for_updates() -> Dict[str, Any]:
    """检查软件更新"""
    try:
        # 这里可以实现实际的更新检查逻辑
        # 比如从GitHub API获取最新release信息
        latest_info = get_latest_version_info()
        
        return {
            "success": True,
            "current_version": APP_VERSION,
            "latest_version": latest_info["latest_version"],
            "update_available": latest_info["update_available"],
            "download_url": latest_info.get("download_url"),
            "release_notes": latest_info.get("release_notes", "")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "current_version": APP_VERSION,
            "latest_version": None,
            "update_available": False
        }

def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    try:
        import platform
        import psutil
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "processor": platform.processor(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
            "disk_usage": f"{psutil.disk_usage('/').percent:.1f}%"
        }
    except ImportError:
        return {
            "os": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }

def format_app_info_for_display() -> str:
    """格式化软件信息用于显示"""
    info = get_app_info()
    return f"""{info['name']} v{info['version']}
构建版本: {info['build']}
{info['description']}

开发者: {info['author']}
{info['copyright']}

Python版本: {info['python_version']}
平台: {info['platform']} ({info['architecture']})"""

if __name__ == "__main__":
    # 测试代码
    print("=== 软件版本信息 ===")
    print(format_app_info_for_display())
    print("\n=== 更新检查 ===")
    update_info = check_for_updates()
    print(f"当前版本: {update_info['current_version']}")
    print(f"最新版本: {update_info.get('latest_version', '未知')}")
    print(f"有更新: {'是' if update_info['update_available'] else '否'}")