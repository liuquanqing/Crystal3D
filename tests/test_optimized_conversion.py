#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的转换系统和文件夹管理功能
"""

import requests
import json
import os
from pathlib import Path

def test_conversion_with_folder_management():
    """测试带有文件夹管理的转换功能"""
    print("=== 测试优化后的转换系统 ===")
    
    # 测试文件路径
    test_file = "test_nacl.cif"
    if not os.path.exists(test_file):
        print(f"错误: 测试文件 {test_file} 不存在")
        return
    
    # API端点
    base_url = "http://localhost:8000"
    convert_url = f"{base_url}/convert"
    
    print(f"\n1. 上传并转换文件: {test_file}")
    
    try:
        # 准备文件上传
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/octet-stream')}
            
            # 发送转换请求
            response = requests.post(convert_url, files=files)
        
        if response.status_code == 200:
            print("✓ 转换成功!")
            
            # 获取响应头信息
            headers = response.headers
            session_id = headers.get('X-Session-ID')
            output_dir = headers.get('X-Output-Directory')
            file_size = headers.get('X-File-Size')
            
            print(f"  - 会话ID: {session_id}")
            print(f"  - 输出目录: {output_dir}")
            print(f"  - 文件大小: {file_size} 字节")
            
            # 保存转换结果
            output_filename = f"optimized_test_result.usdz"
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"  - 结果已保存为: {output_filename}")
            
            # 测试新的API端点
            if session_id:
                test_new_api_endpoints(base_url, session_id)
            
        else:
            print(f"✗ 转换失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求失败: {str(e)}")

def test_new_api_endpoints(base_url, session_id):
    """测试新的API端点"""
    print("\n2. 测试新的API端点")
    
    # 测试获取会话信息
    print("\n2.1 获取会话信息")
    try:
        response = requests.get(f"{base_url}/conversions/{session_id}")
        if response.status_code == 200:
            session_info = response.json()
            print("✓ 会话信息获取成功")
            print(f"  - 原始文件名: {session_info['session_info']['original_filename']}")
            print(f"  - 创建时间: {session_info['session_info']['created_at']}")
            print(f"  - 状态: {session_info['session_info']['status']}")
            
            # 显示文件信息
            files = session_info['session_info'].get('files', {})
            if files:
                print("  - 保存的文件:")
                for file_type, file_info in files.items():
                    print(f"    * {file_type}: {file_info['filename']} ({file_info['size_mb']} MB)")
        else:
            print(f"✗ 获取会话信息失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取会话信息出错: {str(e)}")
    
    # 测试获取转换历史
    print("\n2.2 获取转换历史")
    try:
        response = requests.get(f"{base_url}/conversions/history?limit=5")
        if response.status_code == 200:
            history = response.json()
            print("✓ 转换历史获取成功")
            print(f"  - 历史记录数量: {history['total_count']}")
            
            for i, record in enumerate(history['history'][:3], 1):
                print(f"  - 记录 {i}: {record['original_filename']} ({record['status']})")
        else:
            print(f"✗ 获取转换历史失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取转换历史出错: {str(e)}")
    
    # 测试获取统计信息
    print("\n2.3 获取统计信息")
    try:
        response = requests.get(f"{base_url}/conversions/statistics")
        if response.status_code == 200:
            stats = response.json()
            print("✓ 统计信息获取成功")
            statistics = stats['statistics']
            print(f"  - 总转换次数: {statistics['total_conversions']}")
            print(f"  - 成功转换次数: {statistics['successful_conversions']}")
            print(f"  - 成功率: {statistics['success_rate']}%")
            print(f"  - 输出目录: {statistics['base_output_dir']}")
        else:
            print(f"✗ 获取统计信息失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取统计信息出错: {str(e)}")

def check_output_directory():
    """检查输出目录结构"""
    print("\n3. 检查输出目录结构")
    
    output_base = Path("conversion_results")
    if output_base.exists():
        print(f"✓ 输出基础目录存在: {output_base}")
        
        # 列出所有会话目录
        session_dirs = [d for d in output_base.iterdir() if d.is_dir()]
        print(f"  - 会话目录数量: {len(session_dirs)}")
        
        # 显示最新的几个会话目录
        for i, session_dir in enumerate(sorted(session_dirs, reverse=True)[:3], 1):
            print(f"  - 会话 {i}: {session_dir.name}")
            
            # 列出会话目录中的文件
            files = list(session_dir.glob("*"))
            for file in files:
                if file.is_file():
                    size_mb = round(file.stat().st_size / (1024 * 1024), 3)
                    print(f"    * {file.name} ({size_mb} MB)")
        
        # 检查索引文件
        index_file = output_base / "conversion_index.json"
        if index_file.exists():
            print(f"\n✓ 转换索引文件存在: {index_file}")
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                print(f"  - 索引中的转换记录: {len(index_data.get('conversions', []))}")
                print(f"  - 总计数: {index_data.get('total_count', 0)}")
            except Exception as e:
                print(f"  - 读取索引文件出错: {str(e)}")
        else:
            print("✗ 转换索引文件不存在")
    else:
        print(f"✗ 输出基础目录不存在: {output_base}")

def main():
    """主函数"""
    print("开始测试优化后的转换系统...")
    
    # 测试转换功能
    test_conversion_with_folder_management()
    
    # 检查输出目录
    check_output_directory()
    
    print("\n=== 测试完成 ===")
    print("\n优化功能说明:")
    print("1. 自动创建带时间戳的会话目录")
    print("2. 保存原始CIF文件和最终USDZ文件到会话目录")
    print("3. 记录详细的转换元数据")
    print("4. 提供转换历史查询API")
    print("5. 提供统计信息API")
    print("6. 支持会话信息查询")
    print("7. 支持旧会话清理功能")

if __name__ == "__main__":
    main()