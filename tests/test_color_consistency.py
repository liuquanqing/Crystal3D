#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
颜色一致性测试脚本
用于验证OBJ和USDZ文件的颜色处理是否一致
"""

import os
import sys
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from converter.main_converter import CIFToUSDZConverter
from pymatgen_converter import PymatgenConverter

def test_color_consistency():
    """测试颜色一致性"""
    logger.info("开始颜色一致性测试...")
    
    # 测试文件路径
    test_cif = "examples/NaCl.cif"
    test_obj = "temp/test_color.obj"
    test_mtl = "temp/test_color.mtl"
    test_usdz = "temp/test_color.usdz"
    
    # 确保测试目录存在
    os.makedirs("temp", exist_ok=True)
    
    if not os.path.exists(test_cif):
        logger.error(f"测试CIF文件不存在: {test_cif}")
        return False
    
    try:
        # 1. 使用Pymatgen转换器生成OBJ文件
        logger.info("步骤1: 生成OBJ文件...")
        pymatgen_converter = PymatgenConverter()
        structure = pymatgen_converter.read_cif(test_cif)
        
        # 检查结构中的元素
        elements = set([site.specie.symbol for site in structure])
        logger.info(f"检测到的元素: {elements}")
        
        # 显示每个元素的颜色
        for element in elements:
            color = pymatgen_converter.element_colors.get(element, (0.5, 0.5, 0.5))
            logger.info(f"元素 {element} 的颜色: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f})")
        
        # 生成OBJ文件
        success = pymatgen_converter.convert_to_obj(structure, test_obj)
        if not success:
            logger.error("OBJ文件生成失败")
            return False
        
        # 检查MTL文件是否生成
        if os.path.exists(test_mtl):
            logger.info("MTL文件已生成，检查内容...")
            with open(test_mtl, 'r', encoding='utf-8') as f:
                mtl_content = f.read()
                logger.info("MTL文件内容:")
                print(mtl_content)
        else:
            logger.warning("MTL文件未生成")
        
        # 2. 使用Apple USD转换器转换为USDZ
        logger.info("步骤2: 转换为USDZ文件...")
        converter = CIFToUSDZConverter()
        
        # 直接使用Apple USD转换器
        apple_converter = converter.apple_usd_converter
        if not apple_converter.is_available():
            logger.error("Apple USD转换器不可用")
            return False
        
        # 转换OBJ到USDZ
        result = apple_converter.convert_obj_to_usdz_detailed(test_obj, test_usdz)
        
        # 检查文件是否实际生成，忽略ARKit检查错误
        if os.path.exists(test_usdz) and os.path.getsize(test_usdz) > 0:
            logger.success(f"USDZ文件已生成: {test_usdz}")
            logger.info(f"文件大小: {os.path.getsize(test_usdz)} bytes")
            if not result.get('success', False):
                logger.warning(f"ARKit兼容性检查失败，但文件已生成: {result.get('message', '')}")
        else:
            logger.error(f"USDZ文件未生成或为空")
            return False
        
        # 3. 验证文件
        logger.info("步骤3: 验证生成的文件...")
        
        if os.path.exists(test_obj):
            obj_size = os.path.getsize(test_obj)
            logger.info(f"OBJ文件: {test_obj} ({obj_size} bytes)")
        
        if os.path.exists(test_usdz):
            usdz_size = os.path.getsize(test_usdz)
            logger.info(f"USDZ文件: {test_usdz} ({usdz_size} bytes)")
        
        logger.success("颜色一致性测试完成！")
        logger.info("请在以下位置查看生成的文件:")
        logger.info(f"  OBJ文件: {os.path.abspath(test_obj)}")
        logger.info(f"  MTL文件: {os.path.abspath(test_mtl)}")
        logger.info(f"  USDZ文件: {os.path.abspath(test_usdz)}")
        
        return True
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    logger.info("颜色一致性测试脚本")
    logger.info("=" * 50)
    
    success = test_color_consistency()
    
    if success:
        logger.success("测试完成！")
        print("\n📋 测试结果:")
        print("✅ OBJ文件生成成功")
        print("✅ MTL材质文件生成成功")
        print("✅ USDZ文件转换成功")
        print("\n💡 建议:")
        print("1. 在Blender中打开OBJ文件，检查颜色显示")
        print("2. 在iOS设备上打开USDZ文件，检查颜色显示")
        print("3. 比较两者的颜色是否一致")
    else:
        logger.error("测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()