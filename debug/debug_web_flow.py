#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Web API转换流程中的Jmol使用问题
"""

import os
import sys
sys.path.append('.')

from converter.main_converter import CIFToUSDZConverter
from loguru import logger

def debug_web_conversion_flow():
    """调试Web API转换流程"""
    print("=== Web API转换流程调试 ===")
    
    # 模拟Web API的参数
    sphere_resolution = 20
    bond_cylinder_resolution = 8
    include_bonds = True
    scale_factor = 1.0
    
    # 创建转换器实例（与Web API相同的方式）
    converter = CIFToUSDZConverter(
        sphere_resolution=sphere_resolution,
        bond_cylinder_resolution=bond_cylinder_resolution,
        include_bonds=include_bonds,
        scale_factor=scale_factor
    )
    
    print(f"转换器初始化完成")
    print(f"Jmol转换器可用性: {converter.jmol_converter.is_available()}")
    
    # 测试文件路径
    test_cif = "examples/test_nacl.cif"
    test_usdz = "debug_output.usdz"
    
    if os.path.exists(test_cif):
        print(f"\n测试CIF文件存在: {test_cif}")
        
        try:
            print("\n=== 开始完整转换流程 ===")
            
            # 执行完整转换（与Web API相同的调用）
            result = converter.convert(test_cif, test_usdz, clean_temp=False)
            
            print(f"\n=== 转换结果 ===")
            print(f"转换成功: {result['success']}")
            print(f"转换消息: {result['message']}")
            print(f"完成步骤: {result['steps_completed']}")
            
            if 'metadata' in result:
                metadata = result['metadata']
                print(f"\n=== 转换元数据 ===")
                for key, value in metadata.items():
                    print(f"{key}: {value}")
                    
                # 特别关注converter_used字段
                converter_used = metadata.get('converter_used', 'unknown')
                print(f"\n*** 使用的转换器: {converter_used} ***")
                
                if converter_used != 'jmol':
                    print(f"\n⚠️  警告: 没有使用Jmol转换器！")
                    print(f"   预期: jmol")
                    print(f"   实际: {converter_used}")
                else:
                    print(f"\n✅ 成功使用Jmol转换器！")
            
            # 检查输出文件
            if os.path.exists(test_usdz):
                file_size = os.path.getsize(test_usdz)
                print(f"\n输出文件: {test_usdz} ({file_size} bytes)")
            else:
                print(f"\n❌ 输出文件不存在: {test_usdz}")
                
        except Exception as e:
            print(f"转换过程出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"测试CIF文件不存在: {test_cif}")

if __name__ == "__main__":
    debug_web_conversion_flow()