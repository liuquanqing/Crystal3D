#!/usr/bin/env python3
"""
USD ARKit Checker Wrapper
解决USD环境配置问题的包装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_usd_environment():
    """设置USD环境变量"""
    # 设置USD插件路径
    usd_paths = [
        "/Applications/usdpython/USD.framework/Versions/Current/Resources/plugins",
        "/Applications/usdpython/USD.framework/Versions/Current/Resources",
        "/Applications/usdpython/usdzconvert"
    ]
    
    # 设置环境变量
    env = os.environ.copy()
    env['PXR_PLUGINPATH_NAME'] = ':'.join(usd_paths)
    env['USD_LIBRARY_PATH'] = '/Applications/usdpython/USD.framework/Versions/Current/Libraries'
    env['PYTHONPATH'] = '/Applications/usdpython/USD.framework/Versions/Current/lib/python:' + env.get('PYTHONPATH', '')
    
    return env

def run_usd_checker(usdz_file, verbose=False):
    """运行usdARKitChecker"""
    checker_path = Path(__file__).parent / 'usdARKitChecker'
    
    if not checker_path.exists():
        print(f"错误: 找不到usdARKitChecker文件: {checker_path}")
        return False
    
    if not Path(usdz_file).exists():
        print(f"错误: 找不到USDZ文件: {usdz_file}")
        return False
    
    # 设置环境
    env = setup_usd_environment()
    
    # 构建命令
    cmd = [sys.executable, str(checker_path)]
    if verbose:
        cmd.append('-v')
    cmd.append(usdz_file)
    
    try:
        print(f"运行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        print("标准输出:")
        print(result.stdout)
        
        if result.stderr:
            print("标准错误:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"运行usdARKitChecker时出错: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python run_usd_checker.py <usdz_file> [-v]")
        sys.exit(1)
    
    usdz_file = sys.argv[1]
    verbose = '-v' in sys.argv
    
    success = run_usd_checker(usdz_file, verbose)
    sys.exit(0 if success else 1)