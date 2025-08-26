#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from converter.main_converter import CIFToUSDZConverter
import os

def test_nacl_conversion():
    print("=== 测试NaCl转换详情 ===")
    
    converter = CIFToUSDZConverter()
    
    # 转换NaCl
    result = converter.convert('examples/NaCl.cif', 'user_test_nacl.usdz')
    
    print(f"转换结果: {result['success']}")
    metadata = result.get('metadata', {})
    print(f"原子数: {metadata.get('atom_count', '未知')}")
    print(f"化学式: {metadata.get('original_formula', '未知')}")
    print(f"使用的转换器: {metadata.get('converter_used', '未知')}")
    print(f"顶点数: {metadata.get('vertices_count', '未知')}")
    print(f"面数: {metadata.get('faces_count', '未知')}")
    print(f"材质数: {metadata.get('materials_count', '未知')}")
    
    # 显示CIF元数据
    cif_meta = metadata.get('cif_metadata', {})
    print(f"\n=== CIF元数据 ===")
    print(f"化学式: {cif_meta.get('formula', '未知')}")
    print(f"原子数: {cif_meta.get('num_atoms', '未知')}")
    print(f"元素: {cif_meta.get('elements', [])}")
    print(f"晶格参数: a={cif_meta.get('lattice_parameters', {}).get('a', '未知'):.3f}")
    print(f"体积: {cif_meta.get('volume', '未知'):.3f}")
    print(f"密度: {cif_meta.get('density', '未知'):.3f}")
    
    # 检查文件大小
    if os.path.exists('user_test_nacl.usdz'):
        size = os.path.getsize('user_test_nacl.usdz')
        print(f"USDZ文件大小: {size} bytes ({size/1024/1024:.2f} MB)")
    
    # 检查原始CIF文件内容
    print("\n=== 原始CIF文件内容 ===")
    with open('examples/NaCl.cif', 'r', encoding='utf-8') as f:
        content = f.read()
        print(content[:500])  # 显示前500字符
        
    return result

if __name__ == "__main__":
    test_nacl_conversion()