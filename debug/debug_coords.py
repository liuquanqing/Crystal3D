#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试原子坐标问题
"""

from pymatgen_converter import PymatgenConverter
import numpy as np

def debug_coordinates():
    print("调试原子坐标问题")
    print("=" * 50)
    
    # 创建转换器
    converter = PymatgenConverter()
    
    # 读取CIF文件
    cif_file = "examples/NaCl.cif"
    structure = converter.read_cif(cif_file)
    
    print(f"结构信息:")
    print(f"  原子数量: {len(structure)}")
    print(f"  晶胞参数: {structure.lattice.abc}")
    print(f"  晶胞角度: {structure.lattice.angles}")
    print()
    
    print("原子坐标:")
    for i, site in enumerate(structure):
        print(f"  原子 {i+1}: {site.specie.symbol}")
        print(f"    分数坐标: {site.frac_coords}")
        print(f"    笛卡尔坐标: {site.coords}")
        print()
    
    # 检查是否有重复坐标
    coords = [site.coords for site in structure]
    unique_coords = []
    for coord in coords:
        is_duplicate = False
        for unique_coord in unique_coords:
            if np.allclose(coord, unique_coord, atol=1e-6):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_coords.append(coord)
    
    print(f"唯一坐标数量: {len(unique_coords)}")
    print(f"总坐标数量: {len(coords)}")
    
    if len(unique_coords) < len(coords):
        print("⚠️  发现重复坐标！")
        # 找出重复的坐标
        for i, coord1 in enumerate(coords):
            for j, coord2 in enumerate(coords[i+1:], i+1):
                if np.allclose(coord1, coord2, atol=1e-6):
                    print(f"  原子 {i+1} 和原子 {j+1} 坐标相同: {coord1}")
    else:
        print("✅ 所有坐标都是唯一的")

if __name__ == "__main__":
    debug_coordinates()