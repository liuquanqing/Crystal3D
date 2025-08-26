#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试完整转换流程中的Jmol使用问题
"""

import os
import sys
sys.path.append('.')

from converter.main_converter import CIFToUSDZConverter
from loguru import logger

def debug_conversion_flow():
    """调试完整转换流程"""
    print("=== 转换流程调试 ===")
    
    # 创建主转换器实例
    converter = CIFToUSDZConverter()
    
    print(f"主转换器初始化完成")
    print(f"Jmol转换器可用性: {converter.jmol_converter.is_available()}")
    print(f"Jmol JAR路径: {converter.jmol_converter.jmol_jar_path}")
    print(f"Java路径: {converter.jmol_converter.java_path}")
    
    # 测试CIF文件路径
    test_cif = "examples/test_nacl.cif"
    if os.path.exists(test_cif):
        print(f"\n测试CIF文件存在: {test_cif}")
        
        # 解析CIF文件
        try:
            print("\n=== 开始CIF解析 ===")
            parse_success = converter.cif_parser.parse_file(test_cif)
            print(f"CIF解析结果: {parse_success}")
            
            if parse_success:
                # 检查解析器中的文件路径属性
                print(f"解析器文件路径属性: {getattr(converter.cif_parser, 'file_path', 'None')}")
                
                # 模拟OBJ生成过程
                print("\n=== 模拟OBJ生成过程 ===")
                obj_path = "temp_test.obj"
                result = {'steps_completed': []}
                
                # 手动调用_generate_obj方法
                print(f"调用_generate_obj方法...")
                print(f"Jmol可用性检查: {converter.jmol_converter.is_available()}")
                
                # 检查CIF解析器的file_path属性
                cif_file_path = getattr(converter.cif_parser, 'file_path', None)
                print(f"从解析器获取的CIF文件路径: {cif_file_path}")
                
                if cif_file_path:
                    print(f"CIF文件路径存在，应该使用Jmol")
                else:
                    print(f"CIF文件路径不存在，这可能是问题所在")
                    
        except Exception as e:
            print(f"解析过程出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"测试CIF文件不存在: {test_cif}")

if __name__ == "__main__":
    debug_conversion_flow()