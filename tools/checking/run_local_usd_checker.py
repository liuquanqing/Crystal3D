#!/usr/bin/env python3
"""
使用本地usdpython环境运行usdARKitChecker的包装脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_usd_environment():
    """设置USD相关的环境变量"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    usdpython_dir = project_root / "tools" / "usdpython"
    
    env = os.environ.copy()
    
    # 添加本地usdzconvert到PYTHONPATH
    usdzconvert_path = usdpython_dir / "usdzconvert"
    if usdzconvert_path.exists():
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{usdzconvert_path}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = str(usdzconvert_path)
        
        # 添加到PATH
        if 'PATH' in env:
            env['PATH'] = f"{usdzconvert_path}:{env['PATH']}"
        else:
            env['PATH'] = str(usdzconvert_path)
    
    # 尝试使用系统的USD环境变量（如果存在）
    system_usd_paths = [
        "/Applications/usdpython/USD.framework/Versions/Current/Resources/plugins",
        "/Applications/usdpython/USD.framework/Versions/Current/Libraries",
        "/Applications/usdpython/USD.framework/Versions/Current/Python"
    ]
    
    # 设置PXR插件路径
    if Path(system_usd_paths[0]).exists():
        env['PXR_PLUGINPATH_NAME'] = system_usd_paths[0]
    
    # 设置USD库路径
    if Path(system_usd_paths[1]).exists():
        env['USD_LIBRARY_PATH'] = system_usd_paths[1]
        if 'DYLD_LIBRARY_PATH' in env:
            env['DYLD_LIBRARY_PATH'] = f"{system_usd_paths[1]}:{env['DYLD_LIBRARY_PATH']}"
        else:
            env['DYLD_LIBRARY_PATH'] = system_usd_paths[1]
    
    # 添加系统USD Python路径
    if Path(system_usd_paths[2]).exists():
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{system_usd_paths[2]}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = system_usd_paths[2]
    
    return env

def main():
    if len(sys.argv) < 2:
        print("用法: python run_local_usd_checker.py [选项] <usdz文件>")
        print("选项:")
        print("  --verbose, -v    详细输出模式")
        sys.exit(1)
    
    # 设置环境
    env = setup_usd_environment()
    
    # 获取脚本目录
    script_dir = Path(__file__).parent
    checker_script = script_dir / "usdARKitChecker"
    
    if not checker_script.exists():
        print(f"错误: 找不到usdARKitChecker脚本: {checker_script}")
        sys.exit(1)
    
    # 构建命令
    cmd = [sys.executable, str(checker_script)] + sys.argv[1:]
    
    print(f"运行命令: {' '.join(cmd)}")
    print(f"使用环境变量:")
    print(f"  PXR_PLUGINPATH_NAME: {env.get('PXR_PLUGINPATH_NAME', 'Not set')}")
    print(f"  USD_LIBRARY_PATH: {env.get('USD_LIBRARY_PATH', 'Not set')}")
    print(f"  PYTHONPATH: {env.get('PYTHONPATH', 'Not set')[:100]}...")
    print()
    
    # 运行命令
    try:
        # 先尝试导入pxr模块测试
        test_cmd = [sys.executable, "-c", "from pxr import Usd; print('USD库导入成功')"]
        test_result = subprocess.run(test_cmd, env=env, capture_output=True, text=True)
        
        print("USD库测试结果:")
        if test_result.stdout:
            print(f"  输出: {test_result.stdout.strip()}")
        if test_result.stderr:
            print(f"  错误: {test_result.stderr.strip()}")
        print(f"  返回码: {test_result.returncode}")
        print()
        
        # 运行主命令
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        # 输出结果
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        print(f"\n命令返回码: {result.returncode}")
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"运行usdARKitChecker时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()