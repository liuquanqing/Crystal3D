#!/usr/bin/env python3
"""
CIF转USDZ转换工具 - 安装脚本
"""
from setuptools import setup, find_packages
import os

# 读取README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "CIF转USDZ转换工具 - 专业的晶体结构文件转换解决方案"

# 读取依赖
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return []

setup(
    name="cif-usdz-converter",
    version="1.0.0",
    description="软件版本 v1.0.0 (最新)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="开发团队",
    author_email="dev@example.com",
    url="https://github.com/yourorg/cif-usdz-converter",
    
    # 包配置
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"],
        "static": ["**/*"],
        "templates": ["**/*"],
        "examples": ["**/*"],
        "tools": ["**/*"],
    },
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 依赖
    install_requires=read_requirements(),
    
    # 可选依赖
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],

        "docker": [
            "docker>=6.0.0",
        ],
    },
    
    # 命令行工具
    entry_points={
        "console_scripts": [
            "cif-converter=main:main",
            "cif-server=main:start_server",
            "cif-test=test_system:main",
        ],
    },
    
    # 分类
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
    ],
    
    # 关键词
    keywords="cif usdz crystal structure 3d conversion materials science",
    
    # 项目URLs
    project_urls={
        "Bug Reports": "https://github.com/yourorg/cif-usdz-converter/issues",
        "Source": "https://github.com/yourorg/cif-usdz-converter",
        "Documentation": "https://github.com/yourorg/cif-usdz-converter/wiki",
    },
)